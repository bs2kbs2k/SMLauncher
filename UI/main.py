from PyQt5.QtWidgets import QDialog, QMainWindow
from UI.editDialog import Ui_EditDialog
from UI.mainWindow import Ui_MainWindow

class editDialog(QDialog, Ui_EditDialog):
    def __init__(self):
        super(editDialog, self).__init__()

        # Set up the user interface from Designer.
        self.setupUi(self)

class mainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.setupUi(self)

        self.buttonEdit.clicked.connect(self.edit)

    def edit(self):
        self.editDialog = editDialog()
        self.editDialog.show()