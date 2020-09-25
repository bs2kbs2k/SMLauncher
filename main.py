import sys
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtCore import QFile, QTextStream
import UI
import breeze_resources

app = QApplication(sys.argv)
app.setStyle(QStyleFactory.create("Windows"))

file = QFile(":/dark.qss")
file.open(QFile.ReadOnly | QFile.Text)
stream = QTextStream(file)
app.setStyleSheet(stream.readAll())

window = UI.mainWindow()
window.show()
sys.exit(app.exec_())
