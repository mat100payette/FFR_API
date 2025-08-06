from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QStyle,
    QToolButton,
    QVBoxLayout,
)

from models.api.api_action_args import ChartArgs
from models.charts.extended_chart import ExtendedChart
from services.ffr_api_service import get_chart
from utils.chart_numpy import get_vectorized_per_hand_hits_data
from utils.io import default_cache_path


class LoadChartDialog(QDialog):
    _default_data_path = default_cache_path()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set dialog window title
        self.setWindowTitle("Load Chart")

        # Create radio buttons for "Load from API" and "Load from disk"
        self.api_radio = QRadioButton("Load from API", self)
        self.api_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.disk_radio = QRadioButton("Load from disk", self)
        self.disk_radio.setCursor(Qt.CursorShape.PointingHandCursor)

        # Group the radio buttons so only one can be selected at a time
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.api_radio)
        self.radio_group.addButton(self.disk_radio)

        # Set default selection to "Load from API"
        self.api_radio.setChecked(True)

        # --- Load from API section ---
        self.chart_id_spinbox = QSpinBox(self)
        self.chart_id_spinbox.setRange(1, 4000)

        self.save_chart_data_checkbox = QCheckBox("Save chart data", self)
        self.save_chart_data_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_path_edit = QLineEdit(self)
        self.save_path_edit.setEnabled(False)  # Initially disabled until checkbox is checked

        # Set placeholder text (pale default path)
        self.save_path_edit.setPlaceholderText(str(self._default_data_path))

        # Button to open directory picker for the save path
        self.save_path_button = QPushButton("Browse", self)
        self.save_path_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_path_button.setEnabled(False)  # Disabled initially
        self.save_path_button.clicked.connect(self._open_save_path_picker)

        # Use QToolButton with built-in question mark icon
        self.info_icon = QToolButton(self)
        self.info_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion))
        self.info_icon.setToolTip("Specifies the directory where the chart data will be saved.")

        # Use an HBox layout to position the checkbox, question mark, text field, and browse button
        self.save_layout = QHBoxLayout()
        self.save_layout.addWidget(self.save_chart_data_checkbox)
        self.save_layout.addWidget(self.info_icon)
        self.save_layout.addWidget(self.save_path_edit)
        self.save_layout.addWidget(self.save_path_button)

        # API layout and section with QGroupBox
        self.api_groupbox = QGroupBox("")
        self.api_layout = QFormLayout(self.api_groupbox)
        self.api_layout.addRow("Chart ID:", self.chart_id_spinbox)
        self.api_layout.addRow(self.save_layout)  # Add the HBox layout

        # --- Load from disk section ---
        self.local_path_edit = QLineEdit(self)
        self.local_path_edit.setPlaceholderText(str(self._default_data_path))

        # Button to open file picker for json and lzma files
        self.local_path_button = QPushButton("Browse", self)
        self.local_path_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.local_path_button.clicked.connect(self._open_local_file_picker)

        # Use an HBox layout for the local path field and browse button
        self.local_path_layout = QHBoxLayout()
        self.local_path_layout.addWidget(self.local_path_edit)
        self.local_path_layout.addWidget(self.local_path_button)

        # Disk layout and section with QGroupBox
        self.disk_groupbox = QGroupBox("")
        self.disk_layout = QFormLayout(self.disk_groupbox)
        self.disk_layout.addRow("Local Path:", self.local_path_layout)

        # Add OK and Cancel buttons
        self.ok_button = QPushButton("OK", self)
        self.cancel_button = QPushButton("Cancel", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.api_radio)
        main_layout.addWidget(self.api_groupbox)
        main_layout.addWidget(self.disk_radio)
        main_layout.addWidget(self.disk_groupbox)
        main_layout.addWidget(self.ok_button)
        main_layout.addWidget(self.cancel_button)

        # Connect radio button state changes to toggle sections
        self.api_radio.toggled.connect(self._toggle_sections)
        self.save_chart_data_checkbox.toggled.connect(self._toggle_save_path_edit)
        self._toggle_sections()

    def _toggle_sections(self):
        """Enable or disable sections based on the selected radio button."""
        if self.api_radio.isChecked():
            # Enable API section and disable disk section
            self.api_groupbox.setEnabled(True)
            self.disk_groupbox.setEnabled(False)
            self.local_path_edit.clear()
        else:
            # Enable disk section and disable API section
            self.api_groupbox.setEnabled(False)
            self.disk_groupbox.setEnabled(True)
            self.save_chart_data_checkbox.setChecked(False)
            self.save_path_edit.clear()

    def _toggle_save_path_edit(self):
        """Enable or disable the save path text field based on the checkbox."""
        is_checked = self.save_chart_data_checkbox.isChecked()
        self.save_path_edit.setEnabled(is_checked)
        self.save_path_button.setEnabled(is_checked)
        if not is_checked:
            self.save_path_edit.clear()

    def _open_save_path_picker(self):
        """Open a directory picker for the save path."""
        selected_dir = QFileDialog.getExistingDirectory(self, "Select Save Directory", str(self._default_data_path))
        if selected_dir:
            self.save_path_edit.setText(selected_dir)

    def _open_local_file_picker(self):
        """Open a file picker for json and lzma files."""
        file_filter = "JSON and LZMA files (*.json *.lzma)"
        selected_file, _ = QFileDialog.getOpenFileName(self, "Select File to Load", str(self._default_data_path), file_filter)
        if selected_file:
            self.local_path_edit.setText(selected_file)

    def get_chart_data(self):
        """Returns the chart data based on the selected mode (API or disk)."""
        chart_id = self.chart_id_spinbox.value()

        if self.api_radio.isChecked():
            # Load from API
            api_args = ChartArgs(level=chart_id, compressed=False, extended=True)

            # Check if saving chart data is required
            if self.save_chart_data_checkbox.isChecked():
                save_path = self.save_path_edit.text() or self.save_path_edit.placeholderText()
                api_args.to_dir = save_path
        else:
            # Load from disk
            local_path = self.local_path_edit.text()
            api_args = ChartArgs(level=chart_id, from_file=local_path, compressed=False, extended=True)

        # Use get_chart to load the chart either from API or disk
        chart = get_chart(api_args)

        if chart is None:
            raise ValueError("No chart data found for the specified ID or path.")

        if not isinstance(chart, ExtendedChart):
            raise TypeError("Expected ExtendedChart type, got {}".format(type(chart)))

        # Process the chart data (both left and right hits)
        left_hits_data, right_hits_data = get_vectorized_per_hand_hits_data(chart)

        return left_hits_data, right_hits_data
