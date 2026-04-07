import sys
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import QTimer, Qt, Slot


class Program(QWidget):
    def __init__(self):
        super().__init__()

        self.duration = 1  # 5 minutes

        self.setWindowTitle("Time For a Break")
        self.setStyleSheet("""
            QWidget {
                background-color: #2E3A2F;
                color: #F6F0D7;
                font-family: Segoe UI, Arial;
            }

            QLabel#title {
                font-size: 48px;
                font-weight: bold;
            }

            QLabel#timer {
                font-size: 64px;
                font-weight: 600;
                color: #E8E2C6;
            }

            QPushButton {
                background-color: #9CAB84;
                color: black;
                border-radius: 12px;
                padding: 15px 40px;
                font-size: 20px;
            }

            QPushButton:hover {
                background-color: #B5C3A1;
            }

            QPushButton:pressed {
                background-color: #7E8C6A;
            }
        """)

        # Title
        self.label = QLabel("Time to take a break")
        self.label.setObjectName("title")
        self.label.setAlignment(Qt.AlignCenter)

        # Timer
        self.countdown = QLabel(self.format_time())
        self.countdown.setObjectName("timer")
        self.countdown.setAlignment(Qt.AlignCenter)

        # Button
        self.button = QPushButton("Break done")
        self.button.clicked.connect(self.quit)
        self.button.hide()

        # Layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.countdown, alignment=Qt.AlignCenter)
        self.layout.addSpacing(40)
        self.layout.addWidget(self.button, alignment=Qt.AlignCenter)
        self.layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(self.layout)

        # Timer logic
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_update)
        self.timer.start(1000)

    def format_time(self):
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02}:{seconds:02}"

    def timer_update(self):
        self.duration -= 1
        if self.duration <= 0:
            self.timer.stop()
            self.countdown.setText("00:00")
            self.label.setText("Break finished")
            self.button.show()
        else:
            self.countdown.setText(self.format_time())

    @Slot()
    def quit(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication([])

    widgets = []
    for screen in app.screens():
        widget = Program()
        widget.setGeometry(screen.geometry())
        widget.showFullScreen()
        widgets.append(widget)

    sys.exit(app.exec())
