# in this file we manage the main window, the stack and the app
# stack index ordering:
# login -> 0
# signup -> 1
# create profile -> 2
# home page -> 3

#REQUEST ->
#request() -> connect 3al button
#user -> location, time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from stylinginfo import *
app = QApplication(sys.argv)
from profilePage import *
from login import *
from signup import *
from home import *
from driver_home import *

def reset_profile_form():
    user_type['value'] = None
    traveling_schedule['value'] = None
    location['value'] = None
    schedule_input.clear()
    location_input.clear()
    location_details.clear()
    profile_stack.setCurrentIndex(0)
    update_button_states()

def go_sign():
    reset_profile_form()
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
logout_btn_driver.clicked.connect(go_login)
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

window.setStyleSheet("background-color: #FFEAEC;")



def save_profile():
    if user_type['value'] == 'driver':
        stack.insertWidget(3, driver_home)
        stack.setCurrentIndex(3)
    else:
        stack.setCurrentIndex(3)


btn_confirm.clicked.connect(save_profile)
# if we want to make the window size constant (no resize) uncomment this
window.setFixedSize(900, 550)
window.show()
sys.exit(app.exec_())