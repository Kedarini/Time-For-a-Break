from sqlite3.dbapi2 import connect
import sys
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Qt, Slot

class Program(QWidget):
	def __init__(self):
		super().__init__()

		self.duration = 5 # 5 minutes

		self.setWindowTitle("Time For a Break")
		self.setStyleSheet("""
			background-color: #89986D;
			color: #F6F0D7;
			font-size: 40px;
			""")

		self.label = QLabel(
			"It is time to take a break!",
			alignment=Qt.AlignCenter
		)
		self.label.show()

		self.countdown = QLabel(
			f"{self.duration // 60} min {self.duration % 60} sec",
			alignment = Qt.AlignCenter
		)

		self.button = QPushButton("Break done!")
		self.button.setStyleSheet("""
			width: 10vw
			""")
		self.button.clicked.connect(lambda: self.quit())

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.countdown)
		self.setLayout(self.layout)

		self.timer = QTimer()
		self.timer.timeout.connect(self.timer_update)
		self.timer.start(1000)

	def timer_update(self):
		self.duration -= 1
		if self.duration <= 0:
			self.timer.stop()
			self.layout.addWidget(self.button)
		else:
			self.countdown.setText(
				f"{self.duration // 60} min {self.duration % 60} sec"
			)


	@Slot()
	def quit(self):
		for widget in QApplication.topLevelWidgets():
			widget.close()


if __name__ == "__main__":
	app = QApplication([])

	widgets = []
	for screen in app.screens():
		widget = Program()
		widget.setGeometry(screen.geometry())
		widget.showFullScreen()
		widgets.append(widget)

	sys.exit(app.exec())
