import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from BrickDifference.ui_elements.updateDialog import UpdateDialog

def update_dialog_test():
    update_dialog = UpdateDialog()
    update_dialog.exec()

if __name__ == "__main__":
    basedir = os.path.dirname(__file__)
    basedir = basedir.removesuffix("tests")
    print(basedir)
    app = QApplication([0])

    app.setWindowIcon(QIcon(os.path.join(basedir, "BrickDifference","icons", "BrickDifference_Icon.ico")))

    update_dialog_test()