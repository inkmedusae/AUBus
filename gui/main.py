# in this file we manage the main window, the stack and the app
# stack index ordering:
# login -> 0
# signup -> 1
# create profile -> 2
# home page -> 3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from stylinginfo import *
app = QApplication(sys.argv)
from profilePage import profilePage
from login import *
from signup import *
from home import *

def go_sign():
    stack.setCurrentIndex(1)
signlog_btn.clicked.connect(go_sign)

def go_login():
    stack.setCurrentIndex(0)
logsign_btn.clicked.connect(go_login)

def go_profile():
    stack.setCurrentIndex(2)
sign_btn.clicked.connect(go_profile)

def login():
    stack.setCurrentIndex(3)
login_btn.clicked.connect(login)
logout_btn.clicked.connect(go_login)
stack = QStackedLayout()
stack.setAlignment(Qt.AlignCenter)



stack.addWidget(loginPage)
stack.addWidget(signPage)
stack.addWidget(profilePage)
stack.addWidget(home)

window = QWidget()
window.setLayout(stack)
window.setWindowTitle("AUBus")
window.setGeometry(100, 100, 500, 600)



# if we want to make the window size constant (no resize) uncomment this
window.setFixedSize(900, 550)
window.show()
sys.exit(app.exec_())