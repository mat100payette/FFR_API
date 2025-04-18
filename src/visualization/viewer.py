from typing import Literal

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QPainterPath, QTransform
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout

from models.api.api_action_args import ViewerArgs
from visualization.chart_viewbox import ChartViewBox
from visualization.colors import manip_score_to_color
from visualization.dialogs.load_chart_dialog import LoadChartDialog
from visualization.ui_controllers import NoteSizeController, ScrollDir, ScrollDirController

type PositionData = tuple[list[float], list[int], list[str], list[str], list[int]]

_DEFAULT_POINT_TIP_FORMAT = "ms: {y:g}\nmanip: {data}%"


def run_viewer(args: ViewerArgs) -> None:
    app: QtWidgets.QApplication = QtWidgets.QApplication([])

    window = MainWindow()
    window.show()

    # Start the PySide6 event loop
    app.exec_()


class MainWindow(QMainWindow):
    _chart_view_box: ChartViewBox
    _chart_plot_item: pg.PlotItem

    _left_hits_data: np.ndarray
    _right_hits_data: np.ndarray

    _left_hand_plot: pg.ScatterPlotItem
    _right_hand_plot: pg.ScatterPlotItem

    _shortcuts_label: QLabel

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chart Visualizer")

        # Create the plot widget and layout
        self.graphWidget: pg.GraphicsLayout = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.graphWidget)

        self._note_size_controller = NoteSizeController()
        self._note_size_controller.signal.connect(self.update_note_scale)

        self._scroll_dir_controller = ScrollDirController()
        self._scroll_dir_controller.signal.connect(self.update_scroll_dir)

        # Create ViewBox and plot
        self._chart_view_box = ChartViewBox(
            arrow_size_controller=self._note_size_controller,
            scroll_dir_controller=self._scroll_dir_controller,
        )
        self._chart_plot_item = pg.PlotItem(viewBox=self._chart_view_box)
        self._chart_view_box.set_arrows_plot(self._chart_plot_item)
        self._chart_view_box.shortcuts_signal.connect(self.toggle_shortcuts)
        self._chart_plot_item.hideAxis("bottom")

        self.graphWidget.addItem(self._chart_plot_item)
        self.init_menu()
        self.create_shortcuts()

    def init_menu(self):
        # Create menu bar
        menubar = self.menuBar()

        # Menu items
        chart_menu = menubar.addMenu("Chart")
        view_menu = menubar.addMenu("View")
        settings_menu = menubar.addMenu("Settings")

        # Add actions
        load_chart_Action = QAction("Load Chart", self)
        load_chart_Action.triggered.connect(self.open_load_chart_dialog)
        chart_menu.addAction(load_chart_Action)

        save_action = QAction("Save as Image", self)
        save_action.triggered.connect(self.save_image)
        chart_menu.addAction(save_action)

        reset_action = QAction("Reset Zoom", self)
        reset_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_action)

        scroll_direction_group = QActionGroup(self)
        scroll_direction_group.setExclusive(True)

        # Create individual actions
        upscroll_action = QAction("Upscroll", self, checkable=True)
        downscroll_action = QAction("Downscroll", self, checkable=True)

        self.upscroll_action = upscroll_action
        self.downscroll_action = downscroll_action

        # Connect actions to handler
        upscroll_action.triggered.connect(lambda: self.update_scroll_dir("up"))
        downscroll_action.triggered.connect(lambda: self.update_scroll_dir("down"))

        # Add to group and menu
        scroll_direction_group.addAction(upscroll_action)
        scroll_direction_group.addAction(downscroll_action)

        settings_menu.addAction(upscroll_action)
        settings_menu.addAction(downscroll_action)

        # Set default selection
        downscroll_action.setChecked(True)

    def create_shortcuts(self):
        # Shortcuts label to display the key bindings
        shortcuts_text: str = """
        Shortcuts:
        - Mouse Right Drag: Multidirectional zoom
        - Alt + Mouse Wheel: Resize arrows
        - Ctrl + Mouse Wheel: Horizontal zoom
        - Mouse Wheel: Vertical zoom
        - Ctrl + D: Toggle scroll direction
        - F1: Show this help
        - S: Save current plot view as image
        """
        self._shortcuts_label: QLabel = QLabel(shortcuts_text, parent=self.graphWidget)
        self._shortcuts_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.7); color: white; padding: 5px;")
        self._shortcuts_label.setVisible(False)

        # Position the label at the top right corner
        layout: QVBoxLayout = QVBoxLayout(self.graphWidget)
        layout.addWidget(self._shortcuts_label)
        layout.setAlignment(self._shortcuts_label, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

    def toggle_shortcuts(self, visible: bool):
        """Show or hide the shortcuts label based on the signal from ChartViewBox."""
        self._shortcuts_label.setVisible(visible)

    def open_load_chart_dialog(self):
        # Create and show the Load Chart dialog
        dialog = LoadChartDialog(self)
        if dialog.exec():
            left_hits_data, right_hits_data = dialog.get_chart_data()
            self._left_hits_data = left_hits_data
            self._right_hits_data = right_hits_data

            self.set_viewer_hits_data()

    def set_viewer_hits_data(self):
        left_ms_values: np.ndarray = self._left_hits_data[:, 0]
        left_columns: np.ndarray = self._left_hits_data[:, 2]
        left_scores: np.ndarray = self._left_hits_data[:, 3]

        right_ms_values: np.ndarray = self._right_hits_data[:, 0]
        right_columns: np.ndarray = self._right_hits_data[:, 2]
        right_scores: np.ndarray = self._right_hits_data[:, 3]

        # Get positions, symbols, and colors for both hands
        left_x, left_y, left_symbols, left_colors, left_hover_scores = get_positions_and_colors(
            left_ms_values,
            left_columns,
            left_scores,
            is_left_hand=True,
        )
        right_x, right_y, right_symbols, right_colors, right_hover_scores = get_positions_and_colors(
            right_ms_values,
            right_columns,
            right_scores,
            is_left_hand=False,
        )

        # Create scatter plots for left and right hand inputs with colors and hover tooltips for scores
        self._left_hand_plot = create_hoverable_scatter_plot(left_x, left_y, left_symbols, left_colors, left_hover_scores)
        self._right_hand_plot = create_hoverable_scatter_plot(right_x, right_y, right_symbols, right_colors, right_hover_scores)

        self.update_note_scale(self._note_size_controller.note_size)

        # Set the new plot items
        self._chart_plot_item.clear()
        self._chart_plot_item.addItem(self._left_hand_plot)
        self._chart_plot_item.addItem(self._right_hand_plot)
        self._chart_plot_item.showGrid(x=False, y=False)
        self._chart_plot_item.hideAxis("bottom")

    def save_image(self):
        print("Save Image triggered!")
        # Add save logic

    def reset_zoom(self):
        print("Reset Zoom triggered!")
        # Reset zoom logic

    def update_note_scale(self, note_size: int):
        """
        Update the note size dynamically without recreating the entire plot.
        """
        self._left_hand_plot.setSize(note_size)
        self._right_hand_plot.setSize(note_size)

    def update_scroll_dir(self, dir: ScrollDir):
        """
        Update the scroll direction dynamically without recreating the entire plot.
        """
        if dir == "up":
            self._chart_plot_item.getViewBox().invertY(True)
            self.upscroll_action.setChecked(True)
        elif dir == "down":
            self._chart_plot_item.getViewBox().invertY(False)
            self.downscroll_action.setChecked(True)


# Function to create a scatter plot with hoverable points
def create_hoverable_scatter_plot(x: list[float], y: list[int], symbols: list[str], colors: list[str], scores: list[int]) -> pg.ScatterPlotItem:
    scatter_plot: pg.ScatterPlotItem = pg.ScatterPlotItem(
        x=x,
        y=y,
        symbol=symbols,
        size=12,
        brush=colors,
        hoverable=True,
        tip=_DEFAULT_POINT_TIP_FORMAT.format,
    )

    # Store the scores in the data dict of the scatter plot for easy access
    scatter_plot.setData(x=x, y=y, symbol=symbols, brush=colors, data=scores)
    scatter_plot.setAcceptHoverEvents(True)

    return scatter_plot


def _get_note_painter_path(direction: Literal[0, 1, 2, 3]) -> QPainterPath:
    path = QPainterPath()
    path.moveTo(0.000, -0.5)
    path.lineTo(0.167, -0.333)
    path.lineTo(0.167, -0.100)
    path.lineTo(0.267, -0.200)
    path.lineTo(0.400, -0.200)
    path.lineTo(0.500, -0.100)
    path.lineTo(0.500, 0.033)
    path.lineTo(0.000, 0.500)
    path.lineTo(-0.500, 0.033)
    path.lineTo(-0.500, -0.100)
    path.lineTo(-0.400, -0.200)
    path.lineTo(-0.267, -0.200)
    path.lineTo(-0.167, -0.100)
    path.lineTo(-0.167, -0.333)
    path.closeSubpath()

    # Apply rotation based on direction
    rotation_map = {0: 90, 1: 0, 2: 180, 3: -90}

    angle = rotation_map[direction]
    transform = QTransform().rotate(angle)
    return transform.map(path)


def get_positions_and_colors(
    ms_values: np.ndarray,
    columns: np.ndarray,
    scores: np.ndarray,
    is_left_hand: bool,
) -> PositionData:

    col1_mask: np.ndarray = columns == 1
    col2_mask: np.ndarray = columns == 2
    double_mask: np.ndarray = columns == 3

    left_note_symbol = _get_note_painter_path(0)
    down_note_symbol = _get_note_painter_path(1)
    up_note_symbol = _get_note_painter_path(2)
    right_note_symbol = _get_note_painter_path(3)

    # Handle x positions and symbols based on whether it's left or right hand
    if is_left_hand:
        x_positions = np.concatenate([np.full(col1_mask.sum(), -1.5), np.full(col2_mask.sum(), -0.5), np.tile([-1.5, -0.5], double_mask.sum())])
        symbols = (
            [left_note_symbol] * col1_mask.sum() + [down_note_symbol] * col2_mask.sum() + [left_note_symbol, down_note_symbol] * double_mask.sum()
        )
    else:
        x_positions = np.concatenate([np.full(col1_mask.sum(), 0.5), np.full(col2_mask.sum(), 1.5), np.tile([0.5, 1.5], double_mask.sum())])
        symbols = [up_note_symbol] * col1_mask.sum() + [right_note_symbol] * col2_mask.sum() + [up_note_symbol, right_note_symbol] * double_mask.sum()

    y_positions = np.concatenate([ms_values[col1_mask], ms_values[col2_mask], np.repeat(ms_values[double_mask], 2)])

    colors = np.concatenate(
        [
            np.array([manip_score_to_color(score) for score in scores[col1_mask]]),
            np.array([manip_score_to_color(score) for score in scores[col2_mask]]),
            np.repeat([manip_score_to_color(score) for score in scores[double_mask]], 2),
        ]
    )

    adjusted_scores = np.concatenate([scores[col1_mask], scores[col2_mask], np.repeat(scores[double_mask], 2)])

    return x_positions.tolist(), y_positions.tolist(), symbols, colors.tolist(), adjusted_scores.tolist()
