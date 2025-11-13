from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from stylinginfo import *

home = QWidget()

# --- Sidebar ---
sidebar = QWidget()
sidebar.setStyleSheet("background-color: #2c3e50;")
sidebar.setFixedWidth(200)
sidebar_layout = QVBoxLayout(sidebar)

welcomeLabel = QLabel("AUBus")
welcomeLabel.setFont(QFont('Arial', 24, QFont.Bold))
welcomeLabel.setAlignment(Qt.AlignCenter)
welcomeLabel.setStyleSheet("color: white; margin: 16px 0 24px 0;")
sidebar_layout.addWidget(welcomeLabel)

btn1 = QPushButton("Profile")
btn2 = QPushButton("Settings")
logout_btn = QPushButton("Log out")
for btn in [btn1, btn2, logout_btn]:
    btn.setStyleSheet(homeSide_btn_style)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    sidebar_layout.addWidget(btn)
sidebar_layout.addStretch()
sidebar.setLayout(sidebar_layout)

# --- Main content area ---
main_content_layout = QVBoxLayout()
main_content_layout.setSpacing(16)

request_button = QPushButton("Request a ride")
request_button.setCursor(QCursor(Qt.PointingHandCursor))
request_button.setStyleSheet(request_style)
main_content_layout.addWidget(request_button)

main_content_layout.addStretch()

chatbox_placeholder = QFrame()
chatbox_placeholder.setFixedSize(300, 350)
chatbox_placeholder.setStyleSheet("""
    QFrame {
        background: #FFEAEC;
        border: 1px solid #bbb;
        border-radius: 12px;
    }
""")
chatbox_layout = QVBoxLayout(chatbox_placeholder)
chatbox_layout.setContentsMargins(10, 10, 10, 10)
chatbox_layout.setSpacing(6)

chatbox_scroll = QScrollArea()
chatbox_scroll.setWidgetResizable(True)
chatbox_scroll.setFrameShape(QFrame.NoFrame)
chatbox_messages_widget = QWidget()
chatbox_messages_layout = QVBoxLayout(chatbox_messages_widget)
chatbox_messages_layout.addStretch(1)
chatbox_scroll.setWidget(chatbox_messages_widget)
chatbox_layout.addWidget(chatbox_scroll)

chatbox_input = QLineEdit()
chatbox_input.setPlaceholderText("Type your message and press Enter...")
chatbox_layout.addWidget(chatbox_input)

from PyQt5.QtCore import Qt

def send_chat_message():
    msg = chatbox_input.text().strip()
    if msg:
        label = QLabel(msg)
        label.setWordWrap(True)
        label.setStyleSheet(textBubble_style)
        label.setMaximumWidth(200)
        chatbox_messages_layout.insertWidget(chatbox_messages_layout.count()-1, label)
        chatbox_input.clear()
        # Scroll to bottom
chatbox_scroll.verticalScrollBar().setValue(chatbox_scroll.verticalScrollBar().maximum())
chatbox_input.returnPressed.connect(send_chat_message)

# Layout to push chatbox to bottom right of content area
chatbox_row = QHBoxLayout()
chatbox_row.addStretch()
chatbox_row.addWidget(chatbox_placeholder)
main_content_layout.addLayout(chatbox_row)

# --- Main horizontal layout ---
home_layout = QHBoxLayout()
home_layout.addWidget(sidebar)
home_layout.addLayout(main_content_layout)
home.setLayout(home_layout)