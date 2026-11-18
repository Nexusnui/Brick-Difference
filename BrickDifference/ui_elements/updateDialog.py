from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QPushButton,
    QLayout
)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl


def open_link():
    QDesktopServices.openUrl(QUrl("https://github.com/Nexusnui/Brick-Difference/releases/latest"))


class UpdateDialog(QDialog):
    def __init__(self, parent= None):
        super().__init__(parent)
        self.setWindowTitle("Updates for Brick Difference")
        main_layout = QFormLayout()
        link_label = QPushButton("View Latest Release")
        link_label.clicked.connect(open_link)
        main_layout.addRow("Update Brick Difference", link_label)

        self.setLayout(main_layout)
        main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
