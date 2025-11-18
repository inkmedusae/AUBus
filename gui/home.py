import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stylinginfo import *
from finalserverclient.aubus_client import client_create_ride

key = "7a77199e48174a098bf174356251411"

def create_home(preferences=None, username=None, area=None):
    """
    Creates a personalized home widget based on user preferences.
    preferences: dictionary with GUI customization settings
    username: current user's username
    area: user's area for weather display
    """
    if preferences is None:
        preferences = {
            "sidebar_color": "#2c3e50",
            "background_color": "#FFEAEC",
            "button_color": "#2c3e50",
            "button_hover_color": "#34495e",
            "text_color": "white",
            "theme_name": "default",
            "font_size": 14
        }
    
    if area is None:
        area = "Beirut"
    
    home_widget = QWidget()
    
    # --- Sidebar ---
    sidebar = QWidget()
    sidebar.setStyleSheet(f"background-color: {preferences.get('sidebar_color', '#2c3e50')};")
    sidebar.setFixedWidth(200)
    sidebar_layout = QVBoxLayout(sidebar)
    
    welcome_text = "AUBus"
    welcomeLabel = QLabel(welcome_text)
    welcomeLabel.setFont(QFont('Arial', 24, QFont.Bold))
    welcomeLabel.setAlignment(Qt.AlignCenter)
    welcomeLabel.setStyleSheet(f"color: {preferences.get('text_color', 'white')}; margin: 16px 0 24px 0;")
    sidebar_layout.addWidget(welcomeLabel)
    
    btn1 = QPushButton("Profile")
    btn2 = QPushButton("Settings")
    logout_btn = QPushButton("Log out")
    
    # Apply user-specific button styling
    button_style = f"""
        QPushButton {{
            background-color: {preferences.get('button_color', '#2c3e50')};
            color: {preferences.get('text_color', 'white')};
            border: none;
            padding: 15px;
            text-align: left;
            margin-top: 10px;
            margin-bottom: 10px;
            font-size: {preferences.get('font_size', 14)}px;
        }}
        QPushButton:hover {{
            background-color: {preferences.get('button_hover_color', '#34495e')};
        }}
    """
    
    for btn in [btn1, btn2, logout_btn]:
        btn.setStyleSheet(button_style)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        sidebar_layout.addWidget(btn)
    sidebar_layout.addStretch()
    sidebar.setLayout(sidebar_layout)
    
    main_content_layout = QVBoxLayout()
    main_content_layout.setSpacing(10)
    
    # --- Weather Bar ---
    weather_bar = QFrame()
    weather_bar.setStyleSheet(f"""
        QFrame {{
            background-color: {preferences.get('button_hover_color', '#34495e')};
            border-radius: 8px;
            padding: 5px;
        }}
    """)
    weather_bar_layout = QHBoxLayout(weather_bar)
    weather_bar_layout.setSpacing(5)
    
    weather_day_widgets = []
    
    def create_weather_day_widget(date, temp, condition):
        day_widget = QFrame()
        day_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {preferences.get('button_color', '#2c3e50')};
                border-radius: 6px;
                padding: 2px;
            }}
        """)
        day_layout = QVBoxLayout(day_widget)
        day_layout.setSpacing(1)
        
        date_label = QLabel(date)
        date_label.setFont(QFont('Arial', 8, QFont.Bold))
        date_label.setStyleSheet("color: #3498db;")
        date_label.setAlignment(Qt.AlignCenter)
        
        temp_label = QLabel(temp)
        temp_label.setFont(QFont('Arial', 12, QFont.Bold))
        temp_label.setStyleSheet(f"color: {preferences.get('text_color', '#ecf0f1')};")
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
    
    def fetch_and_display_weather(location=area):
        # Try to fetch weather for the user's location first
        try:
            url = f"http://api.weatherapi.com/v1/forecast.json?key={key}&q={location}&days=4&aqi=no"        
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            forecast_days = data['forecast']['forecastday']
            
            # Clear existing weather widgets
            for widget in weather_day_widgets:
                weather_bar_layout.removeWidget(widget)
                widget.deleteLater()
            weather_day_widgets.clear()
            
            # Add new weather widgets
            for day_data in forecast_days:
                date = day_data['date']
                temp = f"{day_data['day']['avgtemp_c']}°C"
                condition = day_data['day']['condition']['text']
                
                day_widget = create_weather_day_widget(date, temp, condition)
                weather_bar_layout.addWidget(day_widget)
                weather_day_widgets.append(day_widget)
            return  # Success, exit function
        except Exception as e:
            print(f"Weather fetch error for {location}: {e}")
        
        # If user location fails, try Beirut as fallback
        try:
            url = f"http://api.weatherapi.com/v1/forecast.json?key={key}&q=Beirut&days=4&aqi=no"        
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            forecast_days = data['forecast']['forecastday']
            # Clear existing weather widgets
            for widget in weather_day_widgets:
                weather_bar_layout.removeWidget(widget)
                widget.deleteLater()
            weather_day_widgets.clear()
            # Add new weather widgets
            for day_data in forecast_days:
                date = day_data['date']
                temp = f"{day_data['day']['avgtemp_c']}°C"
                condition = day_data['day']['condition']['text']
                day_widget = create_weather_day_widget(date, temp, condition)
                weather_bar_layout.addWidget(day_widget)
                weather_day_widgets.append(day_widget)
        except Exception as e2:
            # Both attempts failed, show error message
            error_label = QLabel("Weather unavailable")
            error_label.setStyleSheet("color: #e74c3c;")
            error_label.setAlignment(Qt.AlignCenter)
            weather_bar_layout.addWidget(error_label)
            print(f"Weather fetch error for Beirut: {e2}")
    
    main_content_layout.addWidget(weather_bar)
    QTimer.singleShot(100, lambda: fetch_and_display_weather(area))
    
    request_button = QPushButton("Request a ride")
    request_button.setCursor(QCursor(Qt.PointingHandCursor))
    request_button.setStyleSheet(button_style)
    main_content_layout.addWidget(request_button)
    
    # Function to handle ride request
    def handle_ride_request():
        """Creates a ride request and notifies all drivers in the same area"""
        if not username:
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.setText("User information not available. Please log in again.")
            error_msg.setWindowTitle("Error")
            error_msg.exec_()
            return
        
        if not area:
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.setText("Area information not available. Please update your profile.")
            error_msg.setWindowTitle("Error")
            error_msg.exec_()
            return
        
        # Create a dialog to get pickup time
        dialog = QDialog()
        dialog.setWindowTitle("Request a Ride")
        dialog.setModal(True)
        dialog_layout = QVBoxLayout()
        
        # Area display (read-only)
        area_label = QLabel(f"Area: {area}")
        area_label.setStyleSheet("font-size: 14px; padding: 5px;")
        dialog_layout.addWidget(area_label)
        
        # Time input
        time_label = QLabel("Pickup Time (e.g., 08:30 AM):")
        time_input = QLineEdit()
        time_input.setPlaceholderText("08:30 AM")
        dialog_layout.addWidget(time_label)
        dialog_layout.addWidget(time_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        submit_btn = QPushButton("Request Ride")
        submit_btn.setStyleSheet(button_style)
        cancel_btn.setStyleSheet(button_style)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(submit_btn)
        dialog_layout.addLayout(button_layout)
        
        dialog.setLayout(dialog_layout)
        
        def submit_request():
            pickup_time = time_input.text().strip()
            if not pickup_time:
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Warning)
                error_msg.setText("Please enter a pickup time")
                error_msg.setWindowTitle("Invalid Input")
                error_msg.exec_()
                return
            
            # Call the client function to create ride request
            response = client_create_ride(username, area, pickup_time)
            
            dialog.close()
            
            # Show result message
            msg = QMessageBox()
            if response.get("status") == "success":
                msg.setIcon(QMessageBox.Information)
                msg.setText(f"Ride request created successfully!\n\nAll drivers in {area} have been notified.")
                msg.setWindowTitle("Success")
            else:
                msg.setIcon(QMessageBox.Critical)
                error_message = response.get('message', 'Unknown error')
                # Check if it's a connection error
                if "Connection failed" in error_message or "connect" in error_message.lower():
                    msg.setText(f"Cannot connect to server.\n\nPlease make sure the AUBus server is running.\n\nTo start the server, run:\npython finalserverclient/aubus_server.py")
                else:
                    msg.setText(f"Failed to create ride request:\n{error_message}")
                msg.setWindowTitle("Error")
            msg.exec_()
        
        submit_btn.clicked.connect(submit_request)
        cancel_btn.clicked.connect(dialog.close)
        time_input.returnPressed.connect(submit_request)
        
        dialog.exec_()
    
    # Connect the button to the handler
    request_button.clicked.connect(handle_ride_request)
    
    main_content_layout.addStretch()
    
    chatbox_placeholder = QFrame()
    chatbox_placeholder.setFixedSize(275, 325)
    chatbox_placeholder.setStyleSheet(f"""
        QFrame {{
            background: {preferences.get('background_color', '#FFEAEC')};
            border: 1px solid #bbb;
            border-radius: 12px;
        }}
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
            bubble_style = f"color: #222; background: {preferences.get('button_color', '#2c3e50')}; border-radius: 8px; padding: 4px 8px; color: {preferences.get('text_color', 'white')}; margin-left: 25px;"
            label.setStyleSheet(bubble_style)
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
    
    # Start with empty chatbox - no shared messages between users
    # Each user gets a fresh chatbox instance
    chatbox_scroll.verticalScrollBar().setValue(chatbox_scroll.verticalScrollBar().maximum())
    chatbox_input.returnPressed.connect(send_chat_message)
    
    chatbox_row = QHBoxLayout()
    chatbox_row.addStretch()
    chatbox_row.addWidget(chatbox_placeholder)
    main_content_layout.addLayout(chatbox_row)
    
    home_layout = QHBoxLayout()
    home_layout.addWidget(sidebar)
    home_layout.addLayout(main_content_layout)
    home_widget.setLayout(home_layout)
    
    # Store references for external access
    home_widget.logout_btn = logout_btn
    home_widget.btn1 = btn1
    home_widget.btn2 = btn2
    home_widget.username = username  # Store username for ride requests
    home_widget.area = area  # Store area for ride requests
    
    return home_widget

# Create default home widget for backward compatibility
home = create_home()