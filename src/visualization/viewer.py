import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout

from models.api.api_action_args import ViewerArgs
from visualization.chart_viewbox import ChartViewBox
from visualization.colors import manip_score_to_color
from visualization.dialogs.load_chart_dialog import LoadChartDialog
from visualization.ui_controllers import ArrowSizeController

type PositionData = tuple[list[float], list[int], list[str], list[str], list[int]]


# Function to create a scatter plot with hoverable points
def create_hoverable_scatter_plot(x: list[float], y: list[int], symbols: list[str], colors: list[str], scores: list[int]) -> pg.ScatterPlotItem:
    scatter_plot: pg.ScatterPlotItem = pg.ScatterPlotItem(x=x, y=y, symbol=symbols, size=12, brush=colors, hoverable=True, tip='ms: {y:g}\nmanip: {data}%'.format)
    
    # Store the scores in the data dict of the scatter plot for easy access
    scatter_plot.setData(x=x, y=y, symbol=symbols, brush=colors, data=scores)
    scatter_plot.setAcceptHoverEvents(True)
    
    return scatter_plot


def get_positions_and_colors(ms_values: np.ndarray, columns: np.ndarray, scores: np.ndarray, is_left_hand: bool) -> PositionData:
    col1_mask: np.ndarray = columns == 1
    col2_mask: np.ndarray = columns == 2
    double_mask: np.ndarray = columns == 3

    # Handle x positions and symbols based on whether it's left or right hand
    if is_left_hand:
        x_positions = np.concatenate([
            np.full(col1_mask.sum(), -1.5),
            np.full(col2_mask.sum(), -0.5),
            np.tile([-1.5, -0.5], double_mask.sum())
        ])
        symbols = ['t3'] * col1_mask.sum() + ['t'] * col2_mask.sum() + ['t3', 't'] * double_mask.sum()
    else:
        x_positions = np.concatenate([
            np.full(col1_mask.sum(), 0.5),
            np.full(col2_mask.sum(), 1.5),
            np.tile([0.5, 1.5], double_mask.sum())
        ])
        symbols = ['t1'] * col1_mask.sum() + ['t2'] * col2_mask.sum() + ['t1', 't2'] * double_mask.sum()

    y_positions = np.concatenate([
        ms_values[col1_mask],
        ms_values[col2_mask],
        np.repeat(ms_values[double_mask], 2)
    ])

    colors = np.concatenate([
        np.array([manip_score_to_color(score) for score in scores[col1_mask]]),
        np.array([manip_score_to_color(score) for score in scores[col2_mask]]),
        np.repeat([manip_score_to_color(score) for score in scores[double_mask]], 2)
    ])

    adjusted_scores = np.concatenate([
        scores[col1_mask],
        scores[col2_mask],
        np.repeat(scores[double_mask], 2)
    ])

    return x_positions.tolist(), y_positions.tolist(), symbols, colors.tolist(), adjusted_scores.tolist()


def run_viewer(args: ViewerArgs) -> None:
    app: QtWidgets.QApplication = QtWidgets.QApplication([])

    arrow_size_controller = ArrowSizeController()

    # TODO: Move all of this elsewhere ===============================

    # Initial column spacing (horizontal space between columns)
    

    # Extract ms, column, and manip score values for both datasets
    

    # END TODO ===============================

    window = MainWindow(arrow_size_controller)
    window.show()
    
    # Start the PySide6 event loop
    app.exec_()
    

class MainWindow(QMainWindow):
    _chart_view_box: ChartViewBox
    _chart_plot_item: pg.PlotItem

    def __init__(self, arrow_size_controller: ArrowSizeController):
        super().__init__()

        self.setWindowTitle("Chart Visualizer")

        # Create the plot widget and layout
        self.graphWidget: pg.GraphicsLayout = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.graphWidget)

        # Create ViewBox and plot
        self._chart_view_box = ChartViewBox(arrow_size_controller)
        self._chart_plot_item = pg.PlotItem(viewBox=self._chart_view_box)
        self._chart_view_box.set_arrows_plot(self._chart_plot_item)

        self.graphWidget.addItem(self._chart_plot_item)
        self.init_menu()
        self.create_shortcuts()

        

    def init_menu(self):
        # Create menu bar
        menubar = self.menuBar()

        # Menu items
        chart_menu = menubar.addMenu("Chart")
        view_menu = menubar.addMenu("View")

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

    def create_shortcuts(self):
        # Shortcuts label to display the key bindings
        shortcuts_text: str = """
        Shortcuts:
        - Alt + Mouse Wheel: Resize arrows
        - Ctrl + Mouse Wheel: Horizontal zoom
        - Mouse Wheel: Vertical zoom
        - D: Toggle between arrow view and density view
        - M: Toggle gradient based on manip score
        - F1: Show this help
        - S: Save current plot view as image
        """
        shortcuts_label: QLabel = QLabel(shortcuts_text, parent=self.graphWidget)
        shortcuts_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.7); color: white; padding: 5px;")
        shortcuts_label.setVisible(False)

        # Position the label at the top right corner
        layout: QVBoxLayout = QVBoxLayout(self.graphWidget)
        layout.addWidget(shortcuts_label)
        layout.setAlignment(shortcuts_label, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

    def open_load_chart_dialog(self):
        # Create and show the Load Chart dialog
        dialog = LoadChartDialog(self)
        if dialog.exec():
            left_hits_data, right_hits_data = dialog.get_chart_data()
            
            left_ms_values: np.ndarray = left_hits_data[:, 0]
            left_columns: np.ndarray = left_hits_data[:, 1]
            left_scores: np.ndarray = left_hits_data[:, 2]
            
            right_ms_values: np.ndarray = right_hits_data[:, 0]
            right_columns: np.ndarray = right_hits_data[:, 1]
            right_scores: np.ndarray = right_hits_data[:, 2]

            # Get positions, symbols, and colors for both hands
            left_x, left_y, left_symbols, left_colors, left_hover_scores = get_positions_and_colors(left_ms_values, left_columns, left_scores, is_left_hand=True)
            right_x, right_y, right_symbols, right_colors, right_hover_scores = get_positions_and_colors(right_ms_values, right_columns, right_scores, is_left_hand=False)

            # Create scatter plots for left and right hand inputs with colors and hover tooltips for scores
            left_hand_plot: pg.ScatterPlotItem = create_hoverable_scatter_plot(left_x, left_y, left_symbols, left_colors, left_hover_scores)
            right_hand_plot: pg.ScatterPlotItem = create_hoverable_scatter_plot(right_x, right_y, right_symbols, right_colors, right_hover_scores)

            # Set the new plot items
            self._chart_plot_item.clear()
            self._chart_plot_item.addItem(left_hand_plot)
            self._chart_plot_item.addItem(right_hand_plot)
            self._chart_plot_item.showGrid(x=False, y=False)
            self._chart_plot_item.hideAxis('bottom')

    def save_image(self):
        print("Save Image triggered!")
        # Add save logic

    def reset_zoom(self):
        print("Reset Zoom triggered!")
        # Reset zoom logic

