import sys
import signal
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QRadialGradient, QColor

class JarvisBubble(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis Assistant")
        self.setFixedSize(300, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Pulse animation state
        self.pulse_value = 0
        self.pulse_direction = 1

        # Timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_pulse)
        self.timer.start(30)  # update every 30 ms

        self.show()

    def animate_pulse(self):
        """Animate pulsing glow."""
        if self.pulse_value >= 30:
            self.pulse_direction = -1
        elif self.pulse_value <= 0:
            self.pulse_direction = 1

        self.pulse_value += self.pulse_direction
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Bubble properties
        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = min(self.width(), self.height()) / 2 - 20

        # ---- Outer glowing aura ----
        gradient = QRadialGradient(center_x, center_y, radius + 40)
        gradient.setColorAt(0, QColor(90, 180, 255, 200))
        gradient.setColorAt(0.6, QColor(90, 120, 255, 100))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(center_x - (radius + self.pulse_value)),
            int(center_y - (radius + self.pulse_value)),
            int(2 * (radius + self.pulse_value)),
            int(2 * (radius + self.pulse_value))
        )

        # ---- Inner glossy sphere ----
        sphere_gradient = QRadialGradient(center_x, center_y, radius)
        sphere_gradient.setColorAt(0, QColor(200, 240, 255))
        sphere_gradient.setColorAt(0.3, QColor(100, 150, 255))
        sphere_gradient.setColorAt(1, QColor(20, 30, 80))
        painter.setBrush(sphere_gradient)
        painter.drawEllipse(
            int(center_x - radius),
            int(center_y - radius),
            int(2 * radius),
            int(2 * radius)
        )

def handle_sigint(signum, frame):
    """Allow graceful shutdown with Ctrl+C."""
    print("\nShutting down Jarvis UI...")
    QApplication.quit()

if __name__ == "__main__":
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, handle_sigint)

    app = QApplication(sys.argv)
    jarvis_ui = JarvisBubble()

    # Enable Ctrl+C to exit in terminal
    timer = QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    sys.exit(app.exec())
