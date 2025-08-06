import numpy as np
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter
from pyqtgraph.Qt import QtCore, QtWidgets
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent

from utils.image import qimage_to_pil_image, stitch_images_vertically
from visualization.ui_controllers import NoteSizeController, ScrollDirController


class ChartViewBox(pg.ViewBox):
    _arrows_plot: pg.PlotItem | None

    shortcuts_signal = Signal(bool)

    def __init__(
        self,
        arrow_size_controller: NoteSizeController,
        scroll_dir_controller: ScrollDirController,
    ) -> None:
        super().__init__()

        self._arrows_plot = None

        self.arrow_size_controller = arrow_size_controller
        self.scroll_dir_controller = scroll_dir_controller

    def set_arrows_plot(self, plot: pg.PlotItem):
        self._arrows_plot = plot

    def wheelEvent(self, event: QtWidgets.QGraphicsSceneWheelEvent) -> None:
        modifiers: QtCore.Qt.KeyboardModifier = QtWidgets.QApplication.keyboardModifiers()
        delta: int = event.delta()

        if modifiers == QtCore.Qt.KeyboardModifier.AltModifier:
            current_size: int = self.arrow_size_controller.note_size
            if delta > 0:
                # Increase arrow size
                new_size = current_size + 1
            else:
                # Decrease arrow size but ensure it's not too small
                new_size = max(1, current_size - 1)

            self.arrow_size_controller.note_size = new_size

        elif modifiers == QtCore.Qt.KeyboardModifier.ControlModifier:
            # Horizontal zoom (Ctrl + scroll)
            self.scaleBy((0.9, 1) if delta > 0 else (1.1, 1))
        else:
            # Vertical zoom (normal scroll)
            self.scaleBy((1, 0.9) if delta > 0 else (1, 1.1))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        modifiers: QtCore.Qt.KeyboardModifier = QtWidgets.QApplication.keyboardModifiers()
        key = event.key()

        if key == Qt.Key.Key_F1:
            self.shortcuts_signal.emit(True)
        elif key == Qt.Key.Key_S:
            self._save_entire_plot_as_image()
        elif key == Qt.Key.Key_D and modifiers == QtCore.Qt.KeyboardModifier.ControlModifier:
            self._toggle_scroll_dir()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        key = event.key()

        if key == Qt.Key.Key_F1:
            self.shortcuts_signal.emit(False)
        else:
            super().keyReleaseEvent(event)

    def _toggle_scroll_dir(self):
        self.scroll_dir_controller.toggle_dir()

    def _save_entire_plot_as_image(self) -> None:
        """
        Save the entire plot (without padding) as an image while maintaining the current zoom level.
        This version supports rendering and stitching together segments of the plot to cover all data at the current zoom.
        """
        # Get the current view range (visible range)
        original_xrange, original_yrange = self.viewRange()
        parent_plotitem: pg.PlotItem = self.parentItem()

        # Get the current vertical axis ticks to ensure they stay consistent
        vertical_axis: pg.AxisItem = parent_plotitem.getAxis("left")
        vertical_axis.hide()

        # Initialize overall bounds to capture the full data range
        y_min, y_max = np.inf, -np.inf

        if self._arrows_plot is None:
            raise ValueError("Arrows plot is not set. Please set it before capturing the plot.")

        # Get the bounds of the arrows plot
        scatter_plot_item: pg.ScatterPlotItem = self._arrows_plot.listDataItems()[0]
        _, y_data = scatter_plot_item.getData()

        # Update the overall data bounds based on each plot's data
        y_min = min(y_min, np.min(y_data))
        y_max = max(y_max, np.max(y_data))

        # Calculate the current view size
        current_yrange_size = original_yrange[1] - original_yrange[0]

        # Calculate the total data range size
        data_yrange_size = y_max - y_min

        # Calculate how many chunks are needed vertically
        num_chunks_y = int(np.ceil(data_yrange_size / current_yrange_size))

        # List to hold the captured chunks
        captured_chunks = []
        chunk_width: int | None = None
        chunk_height: int | None = None

        for y in range(num_chunks_y):
            # Calculate the vertical range for each chunk
            y_start = y_min + y * current_yrange_size
            y_end = min(y_start + current_yrange_size, y_max)

            # Preserve the aspect ratio of the original view
            view_height = y_end - y_start

            # Log the current view range for debugging
            print(f"Capturing chunk {y}: yRange=({y_start}, {y_end})")

            # Set the view to the new range (xRange stays constant, yRange changes)
            self.setRange(xRange=original_xrange, yRange=(y_start, y_start + view_height), padding=0)

            # Force the scene to repaint and update
            self.scene().update()
            QtWidgets.QApplication.processEvents()  # Ensure the event loop processes any pending UI updates

            # Export the PlotItem (without scene padding)
            exporter = ImageExporter(parent_plotitem)  # Export only the PlotItem
            chunk_qimage = exporter.export(toBytes=True)
            if chunk_qimage is None:
                raise RuntimeError(f"Failed to export chunk {y} as QImage.")

            chunk_size = chunk_qimage.size()

            if chunk_width is None:
                chunk_width = chunk_size.width()

            if chunk_height is None:
                chunk_height = chunk_size.height()

            # Check if the QImage was created successfully
            if chunk_qimage.isNull():
                print(f"Error: QImage for chunk {y} is null.")
                continue

            # Convert QImage to PIL image
            pil_image = qimage_to_pil_image(chunk_qimage)

            # Store the chunk for later stitching
            captured_chunks.append(pil_image)

        if not captured_chunks:
            print("Error: No image chunks were captured.")
            return

        captured_chunks = captured_chunks[::-1]

        if chunk_width is None or chunk_height is None:
            raise RuntimeError("Chunk width or height is None, cannot proceed with stitching.")

        # Stitch the captured chunks into a final image
        stitched_image = stitch_images_vertically(captured_chunks, chunk_width, chunk_height)

        # Save the final stitched image
        filename = "stitched_entire_plot.png"
        stitched_image.save(filename)
        print(f"Stitched entire plot saved as {filename}")

        # Restore the original view range and axis ticks after capturing
        self.setRange(xRange=original_xrange, yRange=original_yrange)
        vertical_axis.show()
