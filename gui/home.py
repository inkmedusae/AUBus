from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from stylinginfo import *

home = QWidget()
home_layout = QVBoxLayout()

#welcomeLabel = QLabel("AUBus")
#welcomeLabel.setFont(QFont('Arial', 24, QFont.Bold))
#home_layout.addWidget(welcomeLabel)


sidebar = QWidget()
sidebar.setStyleSheet("background-color: #2c3e50;")
sidebar.setFixedWidth(200)
sidebar_layout = QVBoxLayout(sidebar)


btn1 = QPushButton("Profile")
btn2 = QPushButton("Settings")
logout_btn = QPushButton("Log out")

for btn in [btn1, btn2, logout_btn]:
    btn.setStyleSheet(homeSide_btn_style)
    btn.setCursor(QCursor(Qt.PointingHandCursor))

    sidebar_layout.addWidget(btn)
        
sidebar_layout.addStretch()
sidebar.setLayout(sidebar_layout)


content_area = QWidget()
content_area.setStyleSheet("background-color: white;")
content_layout = QVBoxLayout(content_area)
     
label = QLabel("Main Content Area")
label.setAlignment(Qt.AlignCenter)
content_layout.addWidget(label)


home_layout.addWidget(content_area)
home_layout.addWidget(sidebar)
home.setLayout(home_layout)