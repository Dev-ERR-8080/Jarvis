# ui/simple_test_ui.py
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

def run_simple_ui():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('Test Window')
    
    layout = QVBoxLayout()
    button = QPushButton('Hello, PyQt!')
    layout.addWidget(button)
    
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    run_simple_ui()