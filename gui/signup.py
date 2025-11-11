from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from stylinginfo import *

#sign up page qwidget

signPage = QWidget()
signPage_layout = QVBoxLayout()


title = QLabel("Welcome to AUBus!")
title.setFont(QFont('Arial', 24, QFont.Bold))
title.setAlignment(Qt.AlignCenter)
signPage_layout.addWidget(title)    


logLabel = QLabel("Create an account:")
logLabel.setFont(QFont('Arial', 14, QFont.Bold))
logLabel.setAlignment(Qt.AlignCenter)
logLabel.setStyleSheet("""
    QLabel {     
        margin-bottom: 100px;
        }
""")
signPage_layout.addWidget(logLabel)    
signPage_layout.setSpacing(0)


username_input = QLineEdit()
username_input.setPlaceholderText("Username")
username_input.setMinimumWidth(300)
username_input.setMinimumHeight(40)
username_input.setStyleSheet(user_pass_input_style)
signPage_layout.addWidget(username_input)


password_input = QLineEdit()
password_input.setPlaceholderText("Password")
password_input.setEchoMode(QLineEdit.Password)
password_input.setMinimumWidth(300)
password_input.setMinimumHeight(40)
password_input.setStyleSheet(user_pass_input_style)
signPage_layout.addWidget(password_input)


sign_btn = QPushButton("Sign up")
sign_btn.setMinimumHeight(45)
sign_btn.setStyleSheet(loginbutton_style)
#login_btn.clicked.connect(login)
sign_btn.setCursor(QCursor(Qt.PointingHandCursor))
signPage_layout.addWidget(sign_btn) 


logsign_btn = QPushButton("Have an account?")
logsign_btn.setFont(QFont('Arial', 10, QFont.Bold))
logsign_btn.setStyleSheet(noAccount_ask)
logsign_btn.setCursor(QCursor(Qt.PointingHandCursor))

signPage_layout.addWidget(logsign_btn)

signPage.setLayout(signPage_layout)