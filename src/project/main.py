import sys
from PySide6.QtCore import Qt, QTimer, QSettings, QObject
from PySide6.QtGui import QAction, QIcon, QColor, QPainter, QPixmap, QActionGroup
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
    QMenu,
)

MESSAGES = [
    "Rest your eyes.\nLook 20 feet away for 20 seconds.",
    "Roll your shoulders back.\nTake three deep breaths.",
    "Stand up and stretch\nyour legs and back.",
    "Relax your hands.\nShake them out gently.",
    "Hydrate.\nDrink a glass of water.",
]

TRAY_STYLE = """
    QMenu {
        background-color: #1E2820;
        color: #EEE8D5;
        border: 1px solid #3A5040;
        border-radius: 8px;
        padding: 6px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
    }
    QMenu::item { padding: 8px 20px; border-radius: 4px; }
    QMenu::item:selected { background-color: #2E4030; color: #A8C98C; }
    QMenu::item:disabled { color: #5A7060; }
    QMenu::separator { height: 1px; background: #2E4030; margin: 4px 8px; }
"""


def make_tray_icon(size: int = 64) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#7FB069"))
    m = size // 8
    p.drawEllipse(m, m, size - m * 2, size - m * 2)
    p.end()
    return QIcon(pix)


class BreakWindow(QWidget):
    def __init__(self, screen_geometry, duration: int, show_skip: bool, message: str):
        super().__init__()
        self.duration = duration

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setGeometry(screen_geometry)
        self.setStyleSheet("""
            QWidget {
                background-color: #1C2B1E;
                color: #EEE8D5;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

        # Widgets
        self.lbl_title = QLabel("Time For a Break")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet(
            "font-size: 52px; font-weight: 300; color: #EEE8D5; letter-spacing: -1px;"
        )

        self.lbl_countdown = QLabel(self._fmt())
        self.lbl_countdown.setAlignment(Qt.AlignCenter)
        self.lbl_countdown.setStyleSheet(
            "font-size: 88px; font-weight: 700; color: #7FB069; letter-spacing: -3px;"
        )

        self.lbl_message = QLabel(message)
        self.lbl_message.setAlignment(Qt.AlignCenter)
        self.lbl_message.setWordWrap(True)
        self.lbl_message.setStyleSheet(
            "font-size: 17px; color: #8AAE80; font-weight: 300;"
        )

        self.btn_done = QPushButton("✓  Break Complete")
        self.btn_done.setFixedSize(220, 52)
        self.btn_done.hide()
        self.btn_done.setStyleSheet("""
            QPushButton {
                background-color: #7FB069;
                color: #1C2B1E;
                border: none;
                border-radius: 26px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #A8C98C; }
        """)
        self.btn_done.clicked.connect(QApplication.quit)

        self.btn_skip = QPushButton("Skip ›")
        self.btn_skip.setFixedSize(80, 32)
        self.btn_skip.setVisible(show_skip)
        self.btn_skip.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #5A7A60;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover { color: #EEE8D5; }
        """)
        self.btn_skip.clicked.connect(QApplication.quit)

        # Layout — skip floats top-right, rest is centred
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 0)
        root.setSpacing(0)

        # top row: skip pinned right
        from PySide6.QtWidgets import QHBoxLayout
        top_row = QHBoxLayout()
        top_row.addStretch()
        top_row.addWidget(self.btn_skip)
        root.addLayout(top_row)

        root.addStretch(2)
        root.addWidget(self.lbl_title, alignment=Qt.AlignCenter)
        root.addSpacing(16)
        root.addWidget(self.lbl_countdown, alignment=Qt.AlignCenter)
        root.addSpacing(28)
        root.addWidget(self.lbl_message, alignment=Qt.AlignCenter)
        root.addSpacing(40)
        root.addWidget(self.btn_done, alignment=Qt.AlignCenter)
        root.addStretch(3)

        # Countdown timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

    def _fmt(self):
        m, s = divmod(self.duration, 60)
        return f"{m:02}:{s:02}"

    def _tick(self):
        self.duration -= 1
        if self.duration <= 0:
            self.timer.stop()
            self.lbl_countdown.setText("00:00")
            self.lbl_title.setText("Break Complete")
            self.lbl_message.setText("Well done. Ready to focus again.")
            self.btn_done.show()
            self.btn_skip.hide()
        else:
            self.lbl_countdown.setText(self._fmt())

    def start(self):
        self.showFullScreen()
        self.timer.start(1000)


class BreakController(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.qs = QSettings("BreakTimer", "BreakTimer")
        self.show_skip = self.qs.value("show_skip", True, type=bool)
        self.break_duration = self.qs.value("break_duration", 300, type=int)
        self.break_every = self.qs.value("break_every", 600, type=int)
        self.msg_index = 0
        self.windows: list[BreakWindow] = []

        self.delay_timer = QTimer()
        self.delay_timer.setSingleShot(True)
        self.delay_timer.timeout.connect(self._launch_break)
        self.delay_timer.start(self.break_every * 1000)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(make_tray_icon())
        self.tray.setToolTip("Break Timer")
        self.tray.setVisible(True)
        self._rebuild_menu()

    # ── Tray menu ─────────────────────────────────────────────────

    def _rebuild_menu(self):
        menu = QMenu()
        menu.setStyleSheet(TRAY_STYLE)

        rem = self.delay_timer.remainingTime()
        status = f"Next break in ~{max(rem // 60000, 1)} min" if rem > 0 else "Break in progress"
        status_act = QAction(status)
        status_act.setEnabled(False)
        menu.addAction(status_act)
        menu.addSeparator()

        act_now = QAction("⏱  Take Break Now")
        act_now.triggered.connect(self._launch_break)
        menu.addAction(act_now)

        snooze_menu = QMenu("⏸  Snooze", menu)
        snooze_menu.setStyleSheet(TRAY_STYLE)
        for label, mins in [("5 minutes", 5), ("15 minutes", 15), ("30 minutes", 30), ("1 hour", 60)]:
            a = QAction(label)
            a.triggered.connect(lambda _, m=mins: self._snooze(m))
            snooze_menu.addAction(a)
        menu.addMenu(snooze_menu)

        menu.addSeparator()

        dur_menu = QMenu("⏲  Break Duration", menu)
        dur_menu.setStyleSheet(TRAY_STYLE)
        dur_group = QActionGroup(self)
        dur_group.setExclusive(True)
        for label, secs in [("1 min", 60), ("2 min", 120), ("5 min", 300), ("10 min", 600)]:
            a = QAction(label)
            a.setCheckable(True)
            a.setChecked(secs == self.break_duration)
            a.triggered.connect(lambda _, s=secs: self._set_break_duration(s))
            dur_group.addAction(a)
            dur_menu.addAction(a)
        menu.addMenu(dur_menu)

        interval_menu = QMenu("🔁  Break Every", menu)
        interval_menu.setStyleSheet(TRAY_STYLE)
        int_group = QActionGroup(self)
        int_group.setExclusive(True)
        for label, secs in [("10 min", 600), ("20 min", 1200), ("30 min", 1800), ("45 min", 2700), ("60 min", 3600)]:
            a = QAction(label)
            a.setCheckable(True)
            a.setChecked(secs == self.break_every)
            a.triggered.connect(lambda _, s=secs: self._set_break_every(s))
            int_group.addAction(a)
            interval_menu.addAction(a)
        menu.addMenu(interval_menu)

        menu.addSeparator()

        skip_act = QAction("👁  Show Skip Button")
        skip_act.setCheckable(True)
        skip_act.setChecked(self.show_skip)
        skip_act.triggered.connect(self._toggle_skip)
        menu.addAction(skip_act)

        menu.addSeparator()

        quit_act = QAction("✕  Quit")
        quit_act.triggered.connect(QApplication.quit)
        menu.addAction(quit_act)

        self.tray.setContextMenu(menu)

    # ── Actions ───────────────────────────────────────────────────

    def _toggle_skip(self, checked: bool):
        self.show_skip = checked
        self.qs.setValue("show_skip", checked)
        self._rebuild_menu()

    def _set_break_duration(self, secs: int):
        self.break_duration = secs
        self.qs.setValue("break_duration", secs)
        self._rebuild_menu()

    def _set_break_every(self, secs: int):
        self.break_every = secs
        self.qs.setValue("break_every", secs)
        self._rebuild_menu()

    def _snooze(self, minutes: int):
        self.delay_timer.stop()
        self.delay_timer.start(minutes * 60 * 1000)
        self.tray.showMessage("Snoozed", f"Next break in {minutes} min.", QSystemTrayIcon.MessageIcon.Information, 3000)
        self._rebuild_menu()

    # ── Break lifecycle ───────────────────────────────────────────

    def _launch_break(self):
        self.delay_timer.stop()
        self.windows.clear()
        msg = MESSAGES[self.msg_index % len(MESSAGES)]
        self.msg_index += 1
        for screen in self.app.screens():
            win = BreakWindow(screen.geometry(), self.break_duration, self.show_skip, msg)
            self.windows.append(win)
            win.start()
        self.app.aboutToQuit.connect(self._on_break_done)

    def _on_break_done(self):
        try:
            self.app.aboutToQuit.disconnect(self._on_break_done)
        except RuntimeError:
            pass
        self.delay_timer.start(self.break_every * 1000)
        self._rebuild_menu()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    controller = BreakController(app)
    sys.exit(app.exec())