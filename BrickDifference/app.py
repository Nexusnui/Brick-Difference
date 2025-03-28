import os
import platform
from enum import Enum
from BrickDifference.modelFunctions import *

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QFormLayout,
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QFileDialog,
    QMessageBox,
    QLabel
)
from PyQt6.QtCore import pyqtSignal

app_version = "0.1.0"

if platform.system() == "Windows":
    try:
        from ctypes import windll  # Only exists on Windows.

        myappid = f"nexusnui.brickdifference.{app_version}"
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

basedir = os.path.dirname(__file__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"Brick Difference {app_version}")
        main_layout = QHBoxLayout()
        sub_layout = QVBoxLayout()

    # Input Files Area
        input_files_area = QGroupBox("Input Files")
        input_files_layout = QFormLayout()
        input_files_area.setLayout(input_files_layout)

        self.input_file_a = FileWidget("path/to/first/input/file", line_editable=False)
        self.input_file_a.path_changed.connect(self.path_a_changed)
        input_files_layout.addRow("File A", self.input_file_a)
        self.input_file_b = FileWidget("path/to/second/input/file", line_editable=False)
        input_files_layout.addRow("File B", self.input_file_b)

    # Output Files Area
        output_files_area = QGroupBox("Output Files")
        output_files_layout = QFormLayout()
        output_files_area.setLayout(output_files_layout)

        self.output_file_a_and_b = FileWidget("path/to/output/file/a/and/b",
                                              True, existing_file=False,
                                              default_filename="BD_in_A_and_B.ldr")
        a_and_b_label = QLabel("In A and B ℹ️")
        a_and_b_label.setToolTip("Partlist: Parts appearing in both A and B\n"
                                 "Difference Model: Geometry A and B have in common")
        output_files_layout.addRow(a_and_b_label, self.output_file_a_and_b)
        self.output_file_only_a = FileWidget("path/to/output/file/only/a",
                                             True, existing_file=False,
                                             default_filename="BD_only_in_A.ldr")
        only_a_label = QLabel("Only in A ℹ️")
        only_a_label.setToolTip("Partlist: Parts only appearing A\n"
                                 "Difference Model: Geometry only A has")
        output_files_layout.addRow(only_a_label, self.output_file_only_a)
        self.output_file_only_b = FileWidget("path/to/output/file/only/b",
                                             True, existing_file=False,
                                             default_filename="BD_only_in_B.ldr")
        only_b_label = QLabel("Only in B ℹ️")
        only_b_label.setToolTip("Partlist: Parts only appearing B\n"
                                "Difference Model: Geometry only B has")
        output_files_layout.addRow(only_b_label, self.output_file_only_b)

    # Settings Area
        control_area = QGroupBox("Settings")
        control_layout = QFormLayout()
        control_area.setLayout(control_layout)

        self.mode_input = QComboBox()
        self.mode_input.addItems(["Partlist", "Difference Model"])
        self.mode_input.setEditable(False)
        self.mode_input.currentIndexChanged.connect(self.mode_changed)
        self.mode = Mode.PARTLIST
        control_layout.addRow("Mode", self.mode_input)

        self.column_distance_input = QSpinBox()
        self.column_distance_input.setMinimum(1)
        self.column_distance_input.setMaximum(1000)
        self.column_distance_input.setValue(165)
        column_label = QLabel("Column Distance ℹ️")
        column_label.setToolTip("Distance between part types in partlist model.\n"
                                "Distance in LDraw Units (20ldu = 1 stud)")
        control_layout.addRow(column_label, self.column_distance_input)

        self.row_distance_input = QSpinBox()
        self.row_distance_input.setMinimum(1)
        self.row_distance_input.setMaximum(1000)
        self.row_distance_input.setValue(165)
        row_label = QLabel("Row Distance ℹ️")
        row_label.setToolTip("Distance between part colours in partlist model.\n"
                             "Distance in LDraw Units (20ldu = 1 stud)")
        control_layout.addRow(row_label, self.row_distance_input)

        self.height_distance_input = QSpinBox()
        self.height_distance_input.setMinimum(1)
        self.height_distance_input.setMaximum(1000)
        self.height_distance_input.setValue(35)
        row_label = QLabel("Height Distance ℹ️")
        row_label.setToolTip("Height between parts of the same type and colour in partlist model.\n"
                             "Distance in LDraw Units (24ldu = 1 brick)")
        control_layout.addRow("Height Distance", self.height_distance_input)

        self.generate_button = QPushButton("Generate Difference Files")
        self.generate_button.clicked.connect(self.generate_files)
        control_layout.addRow(self.generate_button)

    # Add Elements to Main Layout

        sub_layout.addWidget(input_files_area)
        sub_layout.addWidget(output_files_area)
        main_layout.addLayout(sub_layout)
        main_layout.addWidget(control_area)
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def mode_changed(self, index):
        partlist_disabled = index != Mode.PARTLIST.value
        self.mode = Mode(index)
        self.column_distance_input.setDisabled(partlist_disabled)
        self.row_distance_input.setDisabled(partlist_disabled)
        self.height_distance_input.setDisabled(partlist_disabled)

    def path_a_changed(self, path):
        parent_dir = os.path.dirname(path)
        self.output_file_a_and_b.set_default_filename(parent_dir, "BD_in_A_and_B.ldr")
        self.output_file_only_a.set_default_filename(parent_dir, "BD_only_in_A.ldr")
        self.output_file_only_b.set_default_filename(parent_dir, "BD_only_in_B.ldr")

    def generate_files(self):
        filepath_a = self.input_file_a.get_current_path()
        filepath_b = self.input_file_b.get_current_path()
        filepath_a_and_b = self.output_file_a_and_b.get_current_path()
        generate_a_and_b = self.output_file_a_and_b.is_activated
        filepath_only_a = self.output_file_only_a.get_current_path()
        generate_only_a = self.output_file_only_a.is_activated
        filepath_only_b = self.output_file_only_b.get_current_path()
        generate_only_b = self.output_file_only_b.is_activated
        if self.mode == Mode.PARTLIST:
            column_distance = self.column_distance_input.value()
            row_distance = self.row_distance_input.value()
            height_distance = self.height_distance_input.value()

        if not (generate_only_a or generate_only_b or generate_a_and_b):
            QMessageBox.critical(self, "Output Disabled", "All Outputfiles are disabled")
            return

        error_messages = []
        has_critical = False
        has_acceptable = False

        a_exists, _, a_msg = self.input_file_a.validate_filepath()
        if not a_exists:
            has_critical = True
            error_messages.append(a_msg)

        b_exists, _, b_msg = self.input_file_b.validate_filepath()
        if not b_exists:
            has_critical = True
            error_messages.append(b_msg)

        a_and_b_exists, a_and_b_is_dir, a_and_b_msg = self.output_file_a_and_b.validate_filepath()
        if not a_and_b_is_dir and generate_a_and_b:
            has_critical = True
            error_messages.append(a_and_b_msg)
        elif a_and_b_exists and generate_a_and_b:
            has_acceptable = True
            error_messages.append(a_and_b_msg)

        a_only_exists, a_only_is_dir, a_only_msg = self.output_file_only_a.validate_filepath()
        if not a_only_is_dir and generate_only_a:
            has_critical = True
            error_messages.append(a_only_msg)
        elif a_only_exists and generate_only_a:
            has_acceptable = True
            error_messages.append(a_only_msg)

        b_only_exists, b_only_is_dir, b_only_msg = self.output_file_only_b.validate_filepath()
        if not b_only_is_dir and generate_only_b:
            has_critical = True
            error_messages.append(b_only_msg)
        elif b_only_exists and generate_only_b:
            has_acceptable = True
            error_messages.append(b_only_msg)

        if has_critical:
            print("".join(error_messages))
            QMessageBox.critical(self, "Filepath Error(s)", f"At least one input file does not exist.\n"
                                                            f"All Errors/Warnings:\n"
                                                            f"{"".join(error_messages)}")
            return
        elif has_acceptable:
            answer = QMessageBox.warning(
                self,
                "Output File(s) already exists",
                f"One or more Outputfiles alreay exist:\n{"".join(error_messages)}\nOverride?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if answer == QMessageBox.StandardButton.No:
                return

        filetree_a = LdrawFileTree(filepath_a)
        filetree_b = LdrawFileTree(filepath_b)

        if generate_only_b:
            if self.mode == Mode.PARTLIST:
                out_only_b, out_a_and_b = get_part_difference(
                    list(filetree_b.filetree.values())[0].get_total_partlist(),
                    list(filetree_a.filetree.values())[0].get_total_partlist()
                )
            elif self.mode == Mode.DIFF_MODEL:
                out_only_b, out_a_and_b = get_difference_model(filetree_b, filetree_a)

        if generate_only_a:
            if self.mode == Mode.PARTLIST:
                out_only_a, out_a_and_b = get_part_difference(
                    list(filetree_a.filetree.values())[0].get_total_partlist(),
                    list(filetree_b.filetree.values())[0].get_total_partlist()
                )
            elif self.mode == Mode.DIFF_MODEL:
                out_only_a, out_a_and_b = get_difference_model(filetree_a, filetree_b)

        if not generate_only_a and not generate_only_b and generate_a_and_b:
            if self.mode == Mode.PARTLIST:
                _, out_a_and_b = get_part_difference(
                    list(filetree_a.filetree.values())[0].get_total_partlist(),
                    list(filetree_b.filetree.values())[0].get_total_partlist()
                )
            elif self.mode == Mode.DIFF_MODEL:
                _, out_a_and_b = get_difference_model(filetree_a, filetree_b)

        saved_files = []
        if self.mode == Mode.PARTLIST:
            if generate_a_and_b:
                out_a_and_b.save_as_ldraw_file(filepath_a_and_b, column_distance, row_distance, height_distance)
                saved_files.append(f"{filepath_a_and_b}\n")
            if generate_only_a:
                out_only_a.save_as_ldraw_file(filepath_only_a, column_distance, row_distance, height_distance)
                saved_files.append(f"{filepath_only_a}\n")
            if generate_only_b:
                out_only_b.save_as_ldraw_file(filepath_only_b, column_distance, row_distance, height_distance)
                saved_files.append(f"{filepath_only_b}\n")
        elif self.mode == Mode.DIFF_MODEL:
            if generate_a_and_b:
                save_model(out_a_and_b, filepath_a_and_b)
                saved_files.append(f"{filepath_a_and_b}\n")
            if generate_only_a:
                save_model(out_only_a, filepath_only_a)
                saved_files.append(f"{filepath_only_a}\n")
            if generate_only_b:
                save_model(out_only_b, filepath_only_b)
                saved_files.append(f"{filepath_only_b}\n")
        QMessageBox.information(self, "Files Saved", f"Saved the following files:\n{"".join(saved_files)}")


class FileWidget(QWidget):
    path_changed = pyqtSignal(str)

    def __init__(self, placeholder: str = "",
                 has_checkbox: bool = False, line_editable: bool = True,
                 existing_file: bool = True, default_filename=""):
        super().__init__()
        main_layout = QHBoxLayout()
        self.line_editable = line_editable
        self.existing_file = existing_file
        self.default_filename = default_filename
        self.filepath_input = QLineEdit()
        if not self.line_editable:
            self.filepath_input.setDisabled(True)
        self.filepath_input.setPlaceholderText(placeholder)
        main_layout.addWidget(self.filepath_input)
        self.select_button = QPushButton("Select")
        main_layout.addWidget(self.select_button)
        self.select_button.clicked.connect(self.select_file)
        self.has_checkbox = has_checkbox
        self.is_activated = True
        if self.has_checkbox:
            self.checkbox = QCheckBox()
            self.checkbox.setCheckState(Qt.CheckState.Checked)
            main_layout.addWidget(self.checkbox)
            self.checkbox.checkStateChanged.connect(self.checkstate_changed)
        self.setLayout(main_layout)

    def select_file(self):
        filepath = ""
        if self.existing_file:
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            dialog.setNameFilter("LDraw Model (*.ldr)")
            dialog.setViewMode(QFileDialog.ViewMode.Detail)
            if dialog.exec():
                filepath = dialog.selectedFiles()[0]
        else:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "part save location", self.default_filename, "LDraw Model (*.ldr)"
            )
        if filepath and len(filepath) > 0:
            self.filepath_input.setText(filepath)
            self.path_changed.emit(filepath)

    def checkstate_changed(self, check: Qt.CheckState):
        set_disabled = check != Qt.CheckState.Checked
        self.is_activated = check == Qt.CheckState.Checked
        if self.line_editable:
            self.filepath_input.setDisabled(set_disabled)
        self.select_button.setDisabled(set_disabled)

    def validate_filepath(self):
        filepath = self.get_current_path()
        file_exists = os.path.isfile(filepath)
        dir_exists = os.path.isdir(os.path.dirname(filepath))
        message = "Nothing Wrong"
        if self.existing_file:
            if not file_exists:
                message = f"'{filepath}, does not exist\n"
        else:
            if file_exists:
                message = f"'{filepath}' already exists\n"
            if not dir_exists:
                message = f"The Directory: '{os.path.dirname(filepath)} does not exist\n"
        return file_exists, dir_exists, message

    def get_current_path(self) -> str:
        return self.filepath_input.text()

    def set_default_filename(self, def_dir, name):
        self.default_filename = os.path.join(def_dir, name)


class Mode(Enum):
    PARTLIST = 0
    DIFF_MODEL = 1
def run():
    app = QApplication([0])
    app.setWindowIcon(QIcon(os.path.join(basedir, "icons", "BrickDifference_Icon.ico")))

    window = MainWindow()

    window.show()

    app.exec()


if __name__ == "__main__":
    run()
