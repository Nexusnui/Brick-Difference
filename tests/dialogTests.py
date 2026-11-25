import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from BrickDifference.ui_elements.aboutPage import AboutPage
from BrickDifference.ui_elements.exceptiondialog import ExceptionDialog
from BrickDifference.ui_elements.updateDialog import UpdateDialog

def about_page_test():
    about_page = AboutPage()
    about_page.exec()

def exception_dialog_test():
    exc_dia = ExceptionDialog(clipboard=app.clipboard())
    exc_dia.exec()

def update_dialog_test():
    update_dialog = UpdateDialog()
    update_dialog.exec()

if __name__ == "__main__":
    basedir = os.path.dirname(__file__)
    basedir = basedir.removesuffix("tests")
    print(basedir)
    app = QApplication([0])

    app.setWindowIcon(QIcon(os.path.join(basedir, "BrickDifference","icons", "BrickDifference_Icon.ico")))

    about_page_test()
    exception_dialog_test()
    update_dialog_test()