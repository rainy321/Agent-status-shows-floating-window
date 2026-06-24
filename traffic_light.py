import sys
import os
import json
import time
from PyQt5.QtWidgets import QApplication, QWidget, QMenu
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

# 状态信号文件路径
# 【可移植关键点】用"按用户的固定路径"，而不是"exe 旁边"。
# 原因：Nuitka onefile 会把程序解压到随机临时目录运行，"exe 旁边"在那里是临时目录，
# 和 update_status.ps1 写的位置对不上，浮窗永远读不到 → 一直红灯。
# 所以一律用固定路径 %LOCALAPPDATA%\ClaudeTrafficLight\status.json，
# 浮窗、ps1、无论从哪运行、是不是 onefile、是不是 .py，都对得上同一个文件。
_SIG_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ClaudeTrafficLight")
try:
    os.makedirs(_SIG_DIR, exist_ok=True)
except OSError:
    pass
SIGNAL_FILE = os.path.join(_SIG_DIR, "status.json")


def read_status():
    """读取 Claude 的状态信号文件"""
    try:
        if os.path.exists(SIGNAL_FILE):
            with open(SIGNAL_FILE, "r") as f:
                data = json.load(f)
            # 超过10秒没更新 → 视为空闲（这一条让我们不必再搞延迟子进程）
            if time.time() - data.get("timestamp", 0) > 10:
                return "idle"
            return data.get("status", "idle")
    except Exception:
        pass
    return "idle"


class TrafficLight(QWidget):
    STATUS_MAP = {
        "working": 0,   # 绿 — 正在执行
        "thinking": 1,  # 黄 — 正在思考
        "idle": 2,      # 红 — 空闲等待
    }
    LABELS = ["工作中", "思考中", "空闲中"]
    COLORS = [
        QColor(0, 220, 0),      # 绿
        QColor(255, 200, 0),    # 黄
        QColor(220, 0, 0),      # 红
    ]
    DIM_COLORS = [
        QColor(0, 50, 0),
        QColor(60, 50, 0),
        QColor(50, 0, 0),
    ]

    def __init__(self):
        super().__init__()
        self.status = 2  # 默认空闲
        self.drag_pos = QPoint()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(80, 230)

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 110, 100)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_status)
        self.timer.start(500)  # 每0.5秒轮询

    def poll_status(self):
        raw = read_status()
        new_status = self.STATUS_MAP.get(raw, 2)
        if new_status != self.status:
            self.status = new_status
            self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # 背景
        p.setBrush(QColor(30, 30, 30, 210))
        p.setPen(QPen(QColor(60, 60, 60), 2))
        p.drawRoundedRect(5, 5, 70, 220, 15, 15)

        # 三个灯
        for i in range(3):
            cx, cy = 40, 40 + i * 58
            r = 22
            if i == self.status:
                glow = QColor(self.COLORS[i])
                glow.setAlpha(50)
                p.setPen(Qt.NoPen)
                p.setBrush(glow)
                p.drawEllipse(cx - r - 5, cy - r - 5, (r + 5) * 2, (r + 5) * 2)
                p.setBrush(self.COLORS[i])
                p.setPen(QPen(QColor(255, 255, 255, 80), 1))
            else:
                p.setBrush(self.DIM_COLORS[i])
                p.setPen(QPen(QColor(50, 50, 50), 1))
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # 状态文字
        font = QFont("Microsoft YaHei", 9)
        p.setFont(font)
        p.setPen(QColor(200, 200, 200))
        p.drawText(5, 195, 70, 25, Qt.AlignCenter, self.LABELS[self.status])

        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quit_action = menu.addAction("退出")
        action = menu.exec_(event.globalPos())
        if action == quit_action:
            try:
                os.remove(SIGNAL_FILE)
            except Exception:
                pass
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    light = TrafficLight()
    light.show()
    sys.exit(app.exec_())
