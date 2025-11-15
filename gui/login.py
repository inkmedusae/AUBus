from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from stylinginfo import *

# ok we'll try to make it without classes cause idk what theyre useful for
# potentially we seperate 

# the stacked layout takes multiple widgets, but put them on mutliple layers
#to have multiple widgets on the same thing, (widgets) -> layout -> widget -> stack
loginPage = QWidget()
loginPage_layout = QVBoxLayout()


title = QLabel("Welcome to AUBus!")
title.setFont(QFont('Arial', 24, QFont.Bold))
title.setAlignment(Qt.AlignCenter)
loginPage_layout.addWidget(title)


logLabel = QLabel("Login to your account:")
logLabel.setFont(QFont('Arial', 14, QFont.Bold))
logLabel.setAlignment(Qt.AlignCenter)
logLabel.setStyleSheet("""
    QLabel {     
        margin-bottom: 25px;
        margin-top: 30px;
        }
""")
loginPage_layout.addWidget(logLabel)    
loginPage_layout.setSpacing(0)


userLab = QLabel("Enter your username:")
userLab.setFont(QFont('Arial', 10))
userLab.setAlignment(Qt.AlignLeft)
userLab.setStyleSheet("""
    margin-left: 25px;
    """)
loginPage_layout.addWidget(userLab)


username_input = QLineEdit()
username_input.setPlaceholderText("Username")
username_input.setMinimumWidth(300)
username_input.setMaximumWidth(700)
username_input.setMinimumHeight(40)
username_input.setStyleSheet(user_pass_input_style)
loginPage_layout.addWidget(username_input)


passLab = QLabel("Enter your password:")
passLab.setFont(QFont('Arial', 10))
passLab.setAlignment(Qt.AlignLeft)
passLab.setStyleSheet("""
    margin-left: 25px;
    """)
loginPage_layout.addWidget(passLab)

password_input = QLineEdit()
password_input.setPlaceholderText("Password")
password_input.setEchoMode(QLineEdit.Password)
password_input.setMinimumWidth(300)
password_input.setMaximumWidth(700)
password_input.setMinimumHeight(40)
password_input.setStyleSheet(user_pass_input_style)
loginPage_layout.addWidget(password_input)


login_btn = QPushButton("Login")
login_btn.setMinimumHeight(45)
login_btn.setStyleSheet(loginbutton_style)

login_btn.setCursor(QCursor(Qt.PointingHandCursor))
loginPage_layout.addWidget(login_btn) 


signlog_btn = QPushButton("Don't have an account?")
signlog_btn.setFont(QFont('Arial', 10, QFont.Bold))
signlog_btn.setStyleSheet(noAccount_ask)
signlog_btn.setCursor(QCursor(Qt.PointingHandCursor))

loginPage_layout.addWidget(signlog_btn)

loginPage.setLayout(loginPage_layout)