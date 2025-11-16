import requests
from PyQt5.QtWidgets import *
from weather import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from stylinginfo import *

def get_requests_for_driver(username, location):
    # Placeholder: Replace with actual request retrieval logic
    return [
        {'passenger': 'user1', 'pickup': 'Achrafieh',  'time': '8:00 AM'},
        {'passenger': 'user2', 'pickup': 'Badaro', 'time': '9:00 AM'},
    ]

driver_home = QWidget()
driver_home_layout = QHBoxLayout(driver_home)

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
logout_btn_driver = QPushButton("Log out")
for btn in [btn1, btn2, logout_btn_driver]:
    btn.setStyleSheet(homeSide_btn_style)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    sidebar_layout.addWidget(btn)
sidebar_layout.addStretch()
sidebar.setLayout(sidebar_layout)
driver_home_layout.addWidget(sidebar)

main_content_layout = QVBoxLayout()
main_content_layout.setSpacing(10)

# --- Weather Bar ---
weather_bar = QFrame()
weather_bar.setStyleSheet("""
    QFrame {
        background-color: #34495e;
        border-radius: 8px;
        padding: 5px;
    }
""")
weather_bar_layout = QHBoxLayout(weather_bar)
weather_bar_layout.setSpacing(5)
weather_day_widgets = []

def create_weather_day_widget(date, temp, condition):
    day_widget = QFrame()
    day_widget.setStyleSheet("""
        QFrame {
            background-color: #2c3e50;
            border-radius: 6px;
            padding: 2px;
        }
    """)
    day_layout = QVBoxLayout(day_widget)
    day_layout.setSpacing(1)

    date_label = QLabel(date)
    date_label.setFont(QFont('Arial', 8, QFont.Bold))
    date_label.setStyleSheet("color: #3498db;")
    date_label.setAlignment(Qt.AlignCenter)

    temp_label = QLabel(temp)
    temp_label.setFont(QFont('Arial', 12, QFont.Bold))
    temp_label.setStyleSheet("color: #ecf0f1;")
    temp_label.setAlignment(Qt.AlignCenter)

    condition_label = QLabel(condition)
    condition_label.setFont(QFont('Arial', 8))
    condition_label.setStyleSheet("color: #bdc3c7;")
    condition_label.setAlignment(Qt.AlignCenter)
    condition_label.setWordWrap(True)

    day_layout.addWidget(date_label)
    day_layout.addWidget(temp_label)
    day_layout.addWidget(condition_label)
    return day_widget

def fetch_and_display_weather(location="Beirut"):
    try:
        key = "7a77199e48174a098bf174356251411"
        url = f"http://api.weatherapi.com/v1/forecast.json?key={key}&q={location}&days=4&aqi=no"        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        forecast_days = data['forecast']['forecastday']

        for widget in weather_day_widgets:
            weather_bar_layout.removeWidget(widget)
            widget.deleteLater()
        weather_day_widgets.clear()

        for day_data in forecast_days:
            date = day_data['date']
            temp = f"{day_data['day']['avgtemp_c']}°C"
            condition = day_data['day']['condition']['text']
            day_widget = create_weather_day_widget(date, temp, condition)
            weather_bar_layout.addWidget(day_widget)
            weather_day_widgets.append(day_widget)
    except Exception as e:
        error_label = QLabel(f"Weather unavailable")
        error_label.setStyleSheet("color: #e74c3c;")
        error_label.setAlignment(Qt.AlignCenter)
        weather_bar_layout.addWidget(error_label)
        print(f"Weather fetch error: {e}")

main_content_layout.addWidget(weather_bar)
QTimer.singleShot(100, lambda: fetch_and_display_weather("Beirut"))

# --- Requests Bar ---
requests_bar = QFrame()
requests_bar.setStyleSheet("""
    QFrame {
        background-color: #2c3e50;
        border-radius: 8px;
        padding: 5px;
    }
""")
requests_bar_layout = QHBoxLayout(requests_bar)

for req in get_requests_for_driver('driver_username', 'driver_location'):
    req_text = f"<b>Passenger:</b> {req['passenger']}<br><b>Pickup:</b> {req['pickup']}<br><b>Time:</b> {req['time']}"
    req_label = QLabel(req_text)
    req_label.setStyleSheet(request_style)
    req_label.setTextFormat(Qt.RichText)
    requests_bar_layout.addWidget(req_label)

requests_bar_layout.addStretch()
main_content_layout.addWidget(requests_bar)

main_content_layout.addStretch()

chatbox_placeholder = QFrame()
chatbox_placeholder.setFixedSize(275, 325)
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

def send_chat_message():
    msg = chatbox_input.text().strip()
    if msg:
        label = QLabel(msg)
        label.setWordWrap(True)
        label.setStyleSheet(textBubble_style)
        label.setMaximumWidth(225)
        chatbox_messages_layout.insertWidget(chatbox_messages_layout.count()-1, label)
        chatbox_input.clear()

def rec_chat_message(message):
    label = QLabel(message)
    label.setWordWrap(True)
    label.setStyleSheet(recBubble_style)
    label.setAlignment(Qt.AlignRight)
    label.setMaximumWidth(175)
    chatbox_messages_layout.insertWidget(chatbox_messages_layout.count()-1, label)

rec_chat_message("Hello")    
chatbox_scroll.verticalScrollBar().setValue(chatbox_scroll.verticalScrollBar().maximum())
chatbox_input.returnPressed.connect(send_chat_message)

chatbox_row = QHBoxLayout()
chatbox_row.addStretch()
chatbox_row.addWidget(chatbox_placeholder)
main_content_layout.addLayout(chatbox_row)

driver_home_layout.addLayout(main_content_layout)
