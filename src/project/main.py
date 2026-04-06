import sys
import os
from PySide6 import QtCore, QtWidgets, QtGui

class Program(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Time For a Break!")
		self.setStyleSheet("background-color: lightblue; color: black; font-size: 24px;")
		self.label = QtWidgets.QLabel("It is time to take a break!", alignment=QtCore.Qt.AlignCenter)
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(self.label)
		self.setLayout(self.layout)


if __name__ == "__main__":
	app = QtWidgets.QApplication([])

	widgets = []
	for screen in app.screens():
		widget = Program()
		widget.setGeometry(screen.geometry())
		widget.showFullScreen()
		widgets.append(widget)

	sys.exit(app.exec())
