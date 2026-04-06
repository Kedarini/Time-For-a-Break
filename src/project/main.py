import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
class FullScreenApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.showMaximized()
        self.setStyleSheet("background-color: black;")
        self.label = QtWidgets.QLabel("Press Esc to toggle full screen", self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 24px;")
        self.label.move(0, 0)
        self.label.resize(self.width(), self.height())
        self._geom = self.geometry()
        self.show()

    def toggle_geom(self):
        if self._geom is None:
            self._geom = self.geometry()
            self.showMaximized()
        else:
            self.showNormal()
            self.setGeometry(self._geom)
            self._geom = None

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.toggle_geom()

app = QtWidgets.QApplication([])
window = FullScreenApp()
app.exec()
