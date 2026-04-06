import sys
from PySide6 import QtCore, QtWidgets

class Program(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.time_left = 5 # 10
		self.setWindowTitle("Time For a Break!")
		self.setStyleSheet("background-color: lightblue; color: black; font-size: 40px;")
		self.label = QtWidgets.QLabel("It is time to take a break!", alignment=QtCore.Qt.AlignCenter)
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update_countdown)
		self.countdown = QtWidgets.QLabel(f"{self.time_left // 60} min {self.time_left % 60} sec", alignment=QtCore.Qt.AlignCenter)
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.countdown)
		self.setLayout(self.layout)

		self.timer.start(1000)

	def update_countdown(self):
		self.time_left -= 1
		if self.time_left <= 0:
			self.timer.stop()
			self.countdown.setText("Enjoy!")
			self.button = QtWidgets.QPushButton("Quit")
			self.button.clicked.connect(lambda: self.close_windows())
			self.layout.addWidget(self.button)
		else:
			self.countdown.setText(f"{self.time_left // 60} min {self.time_left % 60} sec")

	@QtCore.Slot()
	def close_windows(self):
		for widget in QtWidgets.QApplication.topLevelWidgets():
			widget.close()

if __name__ == "__main__":
	app = QtWidgets.QApplication([])

	widgets = []
	for screen in app.screens():
		widget = Program()
		widget.setGeometry(screen.geometry())
		widget.showFullScreen()
		widgets.append(widget)

	sys.exit(app.exec())
