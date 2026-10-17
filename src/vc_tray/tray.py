"""System tray indicator for vc-record. Blinks red while recording."""
import shutil
import subprocess
import sys
from pathlib import Path

from .record import recording_pid, OUT_DIR

AUTOSTART = Path.home() / ".config" / "autostart" / "vc-tray.desktop"


def install_autostart():
    exe = shutil.which("vc-tray") or str(Path.home() / ".local/bin/vc-tray")
    AUTOSTART.parent.mkdir(parents=True, exist_ok=True)
    AUTOSTART.write_text(
        "[Desktop Entry]\nType=Application\nName=Voice Changer Recording Tray\n"
        f"Exec={exe}\nX-KDE-autostart-after=panel\n"
    )
    print(f"Autostart installed: {AUTOSTART}")


def toggle():
    subprocess.Popen([shutil.which("vc-record") or "vc-record", "toggle"])


def main():
    if "--install-autostart" in sys.argv:
        install_autostart()
        return

    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
    from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

    def make_icon(fill, ring=None):
        pm = QPixmap(64, 64)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if ring:
            p.setPen(QColor(ring))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(8, 8, 48, 48)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(fill))
        p.drawEllipse(16, 16, 32, 32)
        p.end()
        return QIcon(pm)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    idle, rec_on, rec_off = make_icon("#888888"), make_icon("#ff2020", "#ff2020"), make_icon("#800000")
    tray = QSystemTrayIcon(idle)

    menu = QMenu()
    a_toggle = QAction("Start/Stop voice recording")
    a_toggle.triggered.connect(toggle)
    a_open = QAction("Open recordings folder")
    a_open.triggered.connect(lambda: subprocess.Popen(["xdg-open", str(OUT_DIR)]))
    a_quit = QAction("Quit tray icon")
    a_quit.triggered.connect(app.quit)
    for a in (a_toggle, a_open):
        menu.addAction(a)
    menu.addSeparator()
    menu.addAction(a_quit)
    tray.setContextMenu(menu)

    state = {"on": False}

    def update():
        if recording_pid():
            state["on"] = not state["on"]
            tray.setIcon(rec_on if state["on"] else rec_off)
            tray.setToolTip("Voice changer: RECORDING")
        else:
            state["on"] = False
            tray.setIcon(idle)
            tray.setToolTip("Voice changer: idle")

    tray.activated.connect(
        lambda r: toggle() if r == QSystemTrayIcon.ActivationReason.Trigger else None
    )

    timer = QTimer()
    timer.timeout.connect(update)
    timer.start(1000)
    update()
    tray.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
