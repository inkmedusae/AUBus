from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from stylinginfo import *

# sign up page qwidget

signPage = QWidget()
signPage_layout = QVBoxLayout()

title = QLabel("Welcome to AUBus!")
title.setFont(QFont('Arial', 24, QFont.Bold))
title.setAlignment(Qt.AlignCenter)
signPage_layout.addWidget(title)    

signLabel = QLabel("Create an account:")
signLabel.setFont(QFont('Arial', 14, QFont.Bold))
signLabel.setAlignment(Qt.AlignCenter)
signLabel.setStyleSheet("""
    QLabel {     
        margin-bottom: 25px;
        margin-top: 30px;
        }
""")
signPage_layout.addWidget(signLabel)    
signPage_layout.setSpacing(0)

userLab_signup = QLabel("Enter your username:")
userLab_signup.setFont(QFont('Arial', 10))
userLab_signup.setAlignment(Qt.AlignLeft)
userLab_signup.setStyleSheet("""
    margin-left: 25px;
    """)
signPage_layout.addWidget(userLab_signup) 

username_input_signup = QLineEdit()
username_input_signup.setPlaceholderText("Username")
username_input_signup.setMinimumWidth(300)
username_input_signup.setMinimumHeight(40)
username_input_signup.setMaximumWidth(700)
username_input_signup.setStyleSheet(user_pass_input_style)
signPage_layout.addWidget(username_input_signup)

passLab_signup = QLabel("Enter your password:")
passLab_signup.setFont(QFont('Arial', 10))
passLab_signup.setAlignment(Qt.AlignLeft)
passLab_signup.setStyleSheet("""
    margin-left: 25px;
    """)
signPage_layout.addWidget(passLab_signup)

password_input_signup = QLineEdit()
password_input_signup.setPlaceholderText("Password")
password_input_signup.setEchoMode(QLineEdit.Password)
password_input_signup.setMinimumWidth(300)
password_input_signup.setMinimumHeight(40)
password_input_signup.setMaximumWidth(700)
password_input_signup.setStyleSheet(user_pass_input_style)
signPage_layout.addWidget(password_input_signup)

sign_btn = QPushButton("Sign up")
sign_btn.setMinimumHeight(45)
sign_btn.setStyleSheet(loginbutton_style)
sign_btn.setCursor(QCursor(Qt.PointingHandCursor))
signPage_layout.addWidget(sign_btn) 

logsign_btn = QPushButton("Have an account?")
logsign_btn.setFont(QFont('Arial', 10, QFont.Bold))
logsign_btn.setStyleSheet(noAccount_ask)
logsign_btn.setCursor(QCursor(Qt.PointingHandCursor))
signPage_layout.addWidget(logsign_btn)

signPage.setLayout(signPage_layout)
