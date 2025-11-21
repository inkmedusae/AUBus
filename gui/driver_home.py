import requests
from PyQt5.QtWidgets import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
import socket
import threading
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stylinginfo import *
from finalserverclient.aubus_client import client_get_pending_rides, client_accept_ride

key = "7a77199e48174a098bf174356251411"

# Signal for thread-safe chat message display in driver home
class DriverChatSignals(QObject):
    message_received = pyqtSignal(str)  # Signal to display received message

driver_chat_signals = DriverChatSignals()
# ----------------------------------------------
def get_local_ip():
    """
    Attempts to determine the machine's outward-facing IP address.
    Falls back to hostname resolution if the UDP trick fails.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"
# ----------------------------------------------
def get_requests_for_driver(username, location):
    """
    Fetches real pending ride requests from the server for the driver's area.
    Returns a list of ride request dictionaries.
    Falls back to empty list if server is unavailable.
    """
    if not location:
        return []
    
    try:
        response = client_get_pending_rides(location)
        if response.get("status") == "success":
            rides = response.get("rides", [])
            # Convert to the format expected by the display code
            return [
                {
                    'id': ride['id'],
                    'passenger': ride['passenger_username'],
                    'pickup': ride['area'],
                    'time': ride['time']
                }
                for ride in rides
            ]
        else:
            # Server returned an error, but connection was successful
            # Only log if it's not a connection error
            if "Connection failed" not in response.get('message', ''):
                print(f"[INFO] No pending rides available: {response.get('message', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"[ERROR] Exception while fetching pending rides: {e}")
        return []
# LATEST PATCH - TO CHECK
# ----------------------------------------------
# ----------------------------------------------
# ----------------------------------------------

def start_driver_chat_listener(driver_home_widget, listen_port=6000):
    """
    Starts a P2P chat server on the driver's machine to listen for passenger connections.
    """
    def listen_for_passenger():
        try:
            driver_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            driver_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            driver_server.bind(('0.0.0.0', int(listen_port)))
            driver_server.listen(1)
            print(f"[DRIVER CHAT] Listening for passenger on port {listen_port}")

            passenger_conn, passenger_addr = driver_server.accept()
            print(f"[DRIVER CHAT] Passenger connected from {passenger_addr}")

            driver_home_widget.passenger_socket = passenger_conn
            driver_home_widget.chat_active = True

            # Enable chatbox for sending
            if hasattr(driver_home_widget, 'chatbox_input'):
                driver_home_widget.chatbox_input.setEnabled(True)

            while driver_home_widget.chat_active:
                try:
                    msg = passenger_conn.recv(1024).decode('utf-8')
                    if not msg:
                        print(f"[DRIVER CHAT] Passenger closed connection (empty message)")
                        break
                    print(f"[DRIVER CHAT] Received message: {msg}")
                    # Emit signal to display message safely on main thread
                    driver_chat_signals.message_received.emit(f"Passenger: {msg}")
                except Exception as e:
                    print(f"[DRIVER CHAT ERROR] Exception during receive: {e}")
                    break

            try:
                passenger_conn.close()
            except:
                pass
            try:
                driver_server.close()
            except:
                pass
            driver_home_widget.chat_active = False
        except Exception as e:
            print(f"[DRIVER CHAT] Error: {e}")

    listener_thread = threading.Thread(target=listen_for_passenger, daemon=True)
    listener_thread.start()

# ----------------------------------------------
# ----------------------------------------------
# ----------------------------------------------
def create_driver_home(username=None, area=None):
    """
    username: current user's username
    area: user's area for weather display
    """

    if area is None:
        area = "Beirut"
    
    driver_home_widget = QWidget()
    driver_home_layout = QHBoxLayout(driver_home_widget)
    
    # ----------------------------------------------
    # ----------------------------------------------
    # Initialize chat attributes
    driver_home_widget.passenger_socket = None
    driver_home_widget.chat_active = False
    driver_home_widget.active_ride_id = None
    driver_home_widget.active_passenger = None
    # ----------------------------------------------
    # ----------------------------------------------

    # --- Sidebar ---
    sidebar = QWidget()
    sidebar.setStyleSheet("background-color: #2c3e50;")
    sidebar.setFixedWidth(200)
    sidebar_layout = QVBoxLayout(sidebar)
    
    welcome_text = "AUBus"
    welcomeLabel = QLabel(welcome_text)
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
    
    # --- Requests Section ---
    requests_container = QFrame()
    requests_container.setFixedHeight(100)
    requests_container.setStyleSheet("""
        QFrame {
            background-color: #2c3e50;
            border-radius: 8px;
        }
    """)
    requests_container_layout = QHBoxLayout(requests_container)
    requests_container_layout.setContentsMargins(6, 4, 6, 4)
    requests_container_layout.setSpacing(6)
    
    refresh_btn = QPushButton("🔄 Refresh")
    refresh_btn_style = """
        QPushButton {
            background-color: #34495e;
            color: white;
            border: none;
            padding: 5px;
            font-size: 12px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #2c3e50;
        }
    """
    refresh_btn.setStyleSheet(refresh_btn_style)
    refresh_btn.setCursor(QCursor(Qt.PointingHandCursor))
    refresh_btn.setFixedWidth(90)
    requests_container_layout.addWidget(refresh_btn)

    # Scrollable area for requests
    requests_scroll = QScrollArea()
    requests_scroll.setStyleSheet("""
        QScrollArea {
            background-color: #2c3e50;
            border-radius: 8px;
            padding: 4px;
        }
        QScrollArea > QWidget > QWidget {
            background-color: #2c3e50;
        }
    """)
    requests_scroll.setWidgetResizable(True)
    requests_scroll.setFrameShape(QFrame.NoFrame)
    requests_scroll.setMaximumHeight(100)
    requests_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    requests_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    requests_widget = QWidget()
    requests_widget.setStyleSheet("background-color: #2c3e50;")
    requests_layout = QHBoxLayout(requests_widget)
    requests_layout.setSpacing(8)
    requests_layout.setContentsMargins(0, 0, 0, 0)
    requests_layout.setAlignment(Qt.AlignLeft)
    requests_scroll.setWidget(requests_widget)
    requests_container_layout.addWidget(requests_scroll, 1)
    
    def update_requests_display():
        """Fetches and displays current pending ride requests"""
        # Clear existing request widgets
        for i in reversed(range(requests_layout.count())):
            item = requests_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    requests_layout.removeWidget(widget)
                    widget.deleteLater()
        
        # Fetch new requests
        requests = get_requests_for_driver(username, area)
        
        if not requests:
            no_requests_label = QLabel("No pending ride requests in your area.")
            no_requests_label.setStyleSheet("color: white;")
            no_requests_label.setAlignment(Qt.AlignCenter)
            requests_layout.addWidget(no_requests_label)
        else:
            for req in requests:
                req_frame = QFrame()
                req_frame.setStyleSheet("""
                    QFrame {
                        background-color: #34495e;
                        border-radius: 6px;
                        padding: 3px;
                    }
                """)
                req_frame_layout = QHBoxLayout(req_frame)
                req_frame_layout.setAlignment(Qt.AlignVCenter)

                
                req_info = QLabel(
                    f"<b>Passenger:</b> {req['passenger']}<br>"
                    f"<b>Area:</b> {req['pickup']}<br>"
                    f"<b>Time:</b> {req['time']}"
                )
                req_info.setStyleSheet("color: white;")
                req_info.setTextFormat(Qt.RichText)
                req_frame_layout.addWidget(req_info)
                req_frame_layout.addStretch()
                
                accept_btn = QPushButton("Accept")
                accept_btn.setStyleSheet(driver_button_styling)
                accept_btn.setCursor(QCursor(Qt.PointingHandCursor))
                accept_btn.setMinimumWidth(80)
                
                def create_accept_handler(ride_id, passenger_name):
                    def accept_ride():
                        if not username:
                            error_msg = QMessageBox()
                            error_msg.setIcon(QMessageBox.Warning)
                            error_msg.setText("User information not available.")
                            error_msg.setWindowTitle("Error")
                            error_msg.exec_()
                            return
# ----------------------------------------------
# ----------------------------------------------
                        # Start P2P listener first so we can provide the server with
                        # the driver's contact info (IP and port) when accepting.
                        listen_port = 6000
                        driver_ip = get_local_ip()
                        print(f"[DRIVER ACCEPT] Detected IP: {driver_ip}, Port: {listen_port}")
                        start_driver_chat_listener(driver_home_widget, listen_port)

                        # Inform the server that this driver accepted the ride and
                        # include the IP/port so the passenger can connect directly.
                        print(f"[DRIVER ACCEPT] Sending accept request with driver_ip={driver_ip}, driver_port={listen_port}")
                        response = client_accept_ride(ride_id, username)
                        msg = QMessageBox()
                        if response.get("status") == "success":
                            msg.setIcon(QMessageBox.Information)
                            msg.setText(f"Ride accepted successfully!\n\nYou are now matched with {passenger_name}.")
                            msg.setWindowTitle("Success")

                            # Store ride information for P2P chat
                            driver_home_widget.active_ride_id = ride_id
                            driver_home_widget.active_passenger = passenger_name
                            
                            # Refresh requests after accepting
                            QTimer.singleShot(500, update_requests_display)
                        else:
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText(f"Failed to accept ride:\n{response.get('message', 'Unknown error')}")
                            msg.setWindowTitle("Error")
                        msg.exec_()
                    return accept_ride
                
                accept_btn.clicked.connect(create_accept_handler(req['id'], req['passenger']))
                req_frame_layout.addWidget(accept_btn)
                
                requests_layout.addWidget(req_frame)
        
        requests_layout.addStretch()
    
    # Connect refresh button
    refresh_btn.clicked.connect(update_requests_display)
    
    # Initial load of requests
    QTimer.singleShot(200, update_requests_display)
    
    # Auto-refresh every 10 seconds
    refresh_timer = QTimer()
    refresh_timer.timeout.connect(update_requests_display)
    refresh_timer.start(10000)  # Refresh every 10 seconds
    
    main_content_layout.addWidget(requests_container)
    
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
    chatbox_input.setEnabled(False)  # Disabled until ride accepted
    chatbox_layout.addWidget(chatbox_input)
# ----------------------------------------------
# ----------------------------------------------
    def send_chat_message():
        msg = chatbox_input.text().strip()
        if msg and hasattr(driver_home_widget, 'passenger_socket') and driver_home_widget.passenger_socket:
            try:
                print(f"[DRIVER SEND] Sending message to passenger: {msg}")
                # Send message to passenger
                driver_home_widget.passenger_socket.send(msg.encode('utf-8'))
                print(f"[DRIVER SEND] Message sent successfully")
                # Display sent message
                label = QLabel(msg)
                label.setWordWrap(True)
                bubble_style = "color: #222; background: #2c3e50; border-radius: 8px; padding: 4px 8px; color: white; margin-left: 25px;"
                label.setStyleSheet(bubble_style)
                label.setMaximumWidth(225)
                chatbox_messages_layout.insertWidget(chatbox_messages_layout.count()-1, label)
                chatbox_input.clear()
                chatbox_scroll.verticalScrollBar().setValue(chatbox_scroll.verticalScrollBar().maximum())
            except Exception as e:
                print(f"[CHAT ERROR] Failed to send message: {e}")
        else:
            print(f"[DRIVER SEND] Not connected to passenger or empty message")
    
    def display_received_message(message):
        label = QLabel(message)
        label.setWordWrap(True)
        label.setStyleSheet("color: #222; background: #ecf0f1; border-radius: 8px; padding: 4px 8px; margin-right: 25px;")
        label.setAlignment(Qt.AlignRight)
        label.setMaximumWidth(225)
        chatbox_messages_layout.insertWidget(chatbox_messages_layout.count()-1, label)
        chatbox_scroll.verticalScrollBar().setValue(chatbox_scroll.verticalScrollBar().maximum())
    
    # Store references for P2P chat
    driver_home_widget.passenger_socket = None
    driver_home_widget.chat_active = False
    driver_home_widget.chatbox_input = chatbox_input
    driver_home_widget.display_received_message = display_received_message
    
    # Connect signal to display function (thread-safe)
    driver_chat_signals.message_received.connect(display_received_message)
# ----------------------------------------------
# # ----------------------------------------------  
    # Start with empty chatbox - no shared messages between users
    # Each user gets a fresh chatbox instance
    chatbox_scroll.verticalScrollBar().setValue(chatbox_scroll.verticalScrollBar().maximum())
    chatbox_input.returnPressed.connect(send_chat_message)
    chatbox_row = QHBoxLayout()
    chatbox_row.addStretch()
    chatbox_row.addWidget(chatbox_placeholder)
    main_content_layout.addLayout(chatbox_row)
    
    driver_home_layout.addLayout(main_content_layout)
    
    # Store references for external access
    driver_home_widget.logout_btn_driver = logout_btn_driver
    driver_home_widget.btn1 = btn1
    driver_home_widget.btn2 = btn2
    
    return driver_home_widget

# Create default driver_home widget for backward compatibility
driver_home = create_driver_home()
