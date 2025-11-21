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
import os
import threading
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stylinginfo import *
app = QApplication(sys.argv)
from profilePage import *
from login import *
from signup import *
from home import *
from driver_home import *
from servertest import *
#from finalserverclient.aubus_server import *

import sqlite3

init_db()
init_ride_db()

# Start the server in a background thread
def start_server_thread():
    """Starts the AUBus server in a background thread"""
    PORT = 5555
    print("[INFO] Starting AUBus server in background...")
    start_server(PORT)

server_thread = threading.Thread(target=start_server_thread, daemon=True)
server_thread.start()

# Temporary storage for signup credentials
temp_signup_credentials = {}

# Store current logged-in user information
current_user = {
    "username": None,
    "role": None,
    "area": None,
}

def username_exists(username):
    """Check if username exists in database without creating an account"""
    conn = sqlite3.connect('THE.db')
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

def reset_profile_form():
    user_type['value'] = None
    traveling_schedule['value'] = None
    location['value'] = None
    # Reset all time pickers to default (8:00 AM)
    from PyQt5.QtCore import QTime
    for time_input in schedule_inputs.values():
        time_input.setTime(QTime(8, 0))
    location_input.clear()
    location_details.clear()
    profile_stack.setCurrentIndex(0)
    update_button_states()

def go_sign():
    reset_profile_form()
    username_input_signup.clear()
    password_input_signup.clear()
    stack.setCurrentIndex(1)
signlog_btn.clicked.connect(go_sign)

#need to clear text boxes when logging out
def go_login():
    # Clear current user data
    global current_user
    current_user["username"] = None
    current_user["role"] = None
    current_user["area"] = None
    
    # Remove all user-specific widgets (home/driver_home) to ensure isolation
    widgets_to_remove = []
    for i in range(stack.count()):
        widget = stack.itemAt(i).widget()
        # Check if it's a user widget (has logout button)
        if hasattr(widget, 'logout_btn') or hasattr(widget, 'logout_btn_driver'):
            widgets_to_remove.append(widget)
    for widget in widgets_to_remove:
        stack.removeWidget(widget)
        widget.deleteLater()  # Clean up to free memory
    
    # Clear input fields and go to login page
    username_input.clear()
    password_input.clear()
    stack.setCurrentIndex(0)
    
    # Reset window background to default
    window.setStyleSheet("background-color: #FFEAEC;")
logsign_btn.clicked.connect(go_login)

def signup():
    username = username_input_signup.text().strip()
    password = password_input_signup.text().strip()
    
    if not username or not password:
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Warning)
        error_msg.setText("Please enter both username and password")
        error_msg.setWindowTitle("Invalid Input")
        error_msg.exec_()
        return
    
    # Check if username already exists
    if username_exists(username):
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Warning)
        error_msg.setText("Username already exists. Please choose a different one.")
        error_msg.setWindowTitle("Username Taken")
        error_msg.exec_()
        return
    
    # Store credentials temporarily (will be used when saving profile)
    global temp_signup_credentials
    temp_signup_credentials = {"username": username, "password": password}
    
    # Proceed to profile creation
    stack.setCurrentIndex(2)

sign_btn.clicked.connect(signup)

#def go_profile():
#    stack.setCurrentIndex(2)
#sign_btn.clicked.connect(go_profile)

def login():
    data = {
        "username": username_input.text(),
        "password": password_input.text()
    }
    result = login_user(data)
    if result["status"] == "success":
        # Store current user information
        global current_user
        current_user["username"] = result.get("username")
        current_user["role"] = result.get("role")
        current_user["area"] = result.get("area")
        

        window.setStyleSheet("background-color: #FFEAEC;")
        
        # Check if user is a driver or passenger
        if result.get("role") == "driver":
            # Remove any existing driver_home widgets to ensure isolation
            widgets_to_remove = []
            for i in range(stack.count()):
                widget = stack.itemAt(i).widget()
                # Check if it's a driver_home widget by looking for the logout_btn_driver attribute
                if hasattr(widget, 'logout_btn_driver'):
                    widgets_to_remove.append(widget)
            for widget in widgets_to_remove:
                stack.removeWidget(widget)
                widget.deleteLater()  # Clean up to free memory
            
            # Create a completely fresh driver_home widget for this user
            from driver_home import create_driver_home
            new_driver_home = create_driver_home(current_user["username"], current_user["area"])
            # Connect logout button
            new_driver_home.logout_btn_driver.clicked.connect(go_login)
            stack.addWidget(new_driver_home)
            stack.setCurrentWidget(new_driver_home)
        else:
            # Remove any existing home widgets to ensure isolation
            widgets_to_remove = []
            for i in range(stack.count()):
                widget = stack.itemAt(i).widget()
                # Check if it's a home widget by looking for the logout_btn attribute
                if hasattr(widget, 'logout_btn') and not hasattr(widget, 'logout_btn_driver'):
                    widgets_to_remove.append(widget)
            for widget in widgets_to_remove:
                stack.removeWidget(widget)
                widget.deleteLater()  # Clean up to free memory
            
            # Create a completely fresh home widget for this user
            from home import create_home
            new_home = create_home(current_user["username"], current_user["area"])
            # Connect logout button
            new_home.logout_btn.clicked.connect(go_login)
            stack.addWidget(new_home)
            stack.setCurrentWidget(new_home)
    else:
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Warning)
        error_msg.setText("Invalid username or password")
        error_msg.setWindowTitle("Login Failed")
        error_msg.exec_()
login_btn.clicked.connect(login)
stack = QStackedLayout()
stack.setAlignment(Qt.AlignCenter)

# Only add login, signup, and profile pages to stack
# Home pages will be added dynamically per user to ensure isolation
stack.addWidget(loginPage)
stack.addWidget(signPage)
stack.addWidget(profilePage)
# Don't add default home/driver_home to stack - they'll be created per user

window = QWidget()
window.setLayout(stack)
window.setWindowTitle("AUBus")
window.setGeometry(100, 100, 500, 600)

window.setStyleSheet("background-color: #FFEAEC;")

def save_profile():
    # Validate that profile is complete
    if not user_type['value'] or not location['value']:
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Warning)
        error_msg.setText("Please complete all required fields")
        error_msg.setWindowTitle("Incomplete Profile")
        error_msg.exec_()
        return
    
    if user_type['value'] == 'driver' and not traveling_schedule['value']:
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Warning)
        error_msg.setText("Please enter your traveling schedule")
        error_msg.setWindowTitle("Incomplete Profile")
        error_msg.exec_()
        return
    
    # Prepare data for account creation using stored credentials
    profile_data = {
        "username": temp_signup_credentials.get("username"),
        "password": temp_signup_credentials.get("password"),
        "area": location['value'],
        "role": user_type['value']
    }
    # Add weekly schedule for drivers
    if user_type['value'] == 'driver' and traveling_schedule['value']:
        profile_data['weekly_schedule'] = json.dumps(traveling_schedule['value'])

    # Create the user record with complete profile information
    result = register_user(profile_data)

    if result["status"] == "success":
        success_msg = QMessageBox()
        success_msg.setIcon(QMessageBox.Information)
        success_msg.setText("Account created successfully!")
        success_msg.setWindowTitle("Success")
        success_msg.exec_()

        # Immediately log the user in to get the correct role from the database
        login_data = {
            "username": temp_signup_credentials.get("username"),
            "password": temp_signup_credentials.get("password")
        }
        login_result = login_user(login_data)
        if login_result["status"] == "success":
            global current_user
            current_user["username"] = login_result.get("username")
            current_user["role"] = login_result.get("role")
            current_user["area"] = login_result.get("area")

            # Go to appropriate home page based on role from database
            if current_user["role"] == 'driver':
                try:
                    widgets_to_remove = []
                    for i in range(stack.count()):
                        widget = stack.itemAt(i).widget()
                        if hasattr(widget, 'logout_btn_driver'):
                            widgets_to_remove.append(widget)
                    for widget in widgets_to_remove:
                        stack.removeWidget(widget)
                        widget.deleteLater()
                    from driver_home import create_driver_home
                    new_driver_home = create_driver_home(current_user["username"], current_user["area"])
                    if hasattr(new_driver_home, 'logout_btn_driver'):
                        new_driver_home.logout_btn_driver.clicked.connect(go_login)
                        stack.addWidget(new_driver_home)
                        stack.setCurrentWidget(new_driver_home)
                    else:
                        raise Exception("Driver home widget creation failed.")
                except Exception as e:
                    error_msg = QMessageBox()
                    error_msg.setIcon(QMessageBox.Critical)
                    error_msg.setText(f"Error loading driver home page: {e}")
                    error_msg.setWindowTitle("Driver Home Error")
                    error_msg.exec_()
            elif current_user["role"] == 'passenger':
                try:
                    widgets_to_remove = []
                    for i in range(stack.count()):
                        widget = stack.itemAt(i).widget()
                        if hasattr(widget, 'logout_btn') and not hasattr(widget, 'logout_btn_driver'):
                            widgets_to_remove.append(widget)
                    for widget in widgets_to_remove:
                        stack.removeWidget(widget)
                        widget.deleteLater()
                    from home import create_home
                    new_home = create_home(current_user["username"], current_user["area"])
                    if hasattr(new_home, 'logout_btn'):
                        new_home.logout_btn.clicked.connect(go_login)
                        stack.addWidget(new_home)
                        stack.setCurrentWidget(new_home)
                    else:
                        raise Exception("Passenger home widget creation failed.")
                except Exception as e:
                    error_msg = QMessageBox()
                    error_msg.setIcon(QMessageBox.Critical)
                    error_msg.setText(f"Error loading passenger home page: {e}")
                    error_msg.setWindowTitle("Passenger Home Error")
                    error_msg.exec_()
            else:
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.setText("Unknown user type. Cannot load home page.")
                error_msg.setWindowTitle("Home Page Error")
                error_msg.exec_()
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.setText(f"Error loading passenger home page: {e}")
                error_msg.setWindowTitle("Passenger Home Error")
                error_msg.exec_()
        else:
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setText("Unknown user type. Cannot load home page.")
            error_msg.setWindowTitle("Home Page Error")
            error_msg.exec_()
    else:
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Warning)
        error_msg.setText(f"Error creating account: {result['message']}")
        error_msg.setWindowTitle("Account Creation Failed")
        error_msg.exec_()


btn_confirm.clicked.connect(save_profile)
# if we want to make the window size constant (no resize) uncomment this
window.setFixedSize(900, 575)
window.show()
sys.exit(app.exec_())