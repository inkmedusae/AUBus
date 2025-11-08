from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedLayout
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.stack = QStackedLayout()

        # Two pages
        page1 = QWidget()
        page1_layout = QVBoxLayout(page1)
        page1_layout.addWidget(QLabel("Layout 1"))
        btn1 = QPushButton("Switch to Layout 2")
        btn1.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        page1_layout.addWidget(btn1)

        page2 = QWidget()
        page2_layout = QVBoxLayout(page2)
        page2_layout.addWidget(QLabel("Layout 2"))
        btn2 = QPushButton("Switch to Layout 1")
        btn2.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        page2_layout.addWidget(btn2)

        self.stack.addWidget(page1)
        self.stack.addWidget(page2)

        self.setLayout(self.stack)


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())
