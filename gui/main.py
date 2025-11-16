# main.py
# stack index ordering (logical):
# login         -> 0
# signup        -> 1
# create profile -> 2
# home/driver   -> 3 (driver_home may be inserted dynamically)

import sys
import os
import hashlib

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QMessageBox,
)
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from stylinginfo import *

# ---------- IMPORT DB LAYER ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from db_api import (
    init_db,
    create_user,
    username_exists,
    get_user_for_login,
    current_timestamp,
    update_user_profile,
)

# ---------- QT APP ----------
app = QApplication(sys.argv)

# ---------- IMPORT PAGES (after QApplication) ----------
from profilePage import (
    profilePage,
    profile_stack,
    user_type,
    traveling_schedule,
    location,
    schedule_input,
    location_input,
    location_details,
    update_button_states,
    btn_confirm,
)
from login import (
    loginPage,
    username_input,
    password_input,
    login_btn,
    signlog_btn,
)
from signup import (
    signPage,
    username_input_signup,
    password_input_signup,
    sign_btn,
    logsign_btn,
)
from home import home, btn1, logout_btn  # btn1 = "Profile" button
from driver_home import driver_home, logout_btn_driver

# ---------- DB INIT ----------
init_db()

# ---------- STACKED WIDGET ----------
stack = QStackedWidget()
stack.addWidget(loginPage)    # index 0
stack.addWidget(signPage)     # index 1
stack.addWidget(profilePage)  # index 2
stack.addWidget(home)         # index 3

# ---------- MAIN WINDOW ----------
window = QWidget()
window_layout = QVBoxLayout(window)
window_layout.addWidget(stack)

window.setWindowTitle("AUBus")
window.setGeometry(100, 100, 500, 600)
window.setStyleSheet("background-color: #FFEAEC;")
window.setFixedSize(900, 550)

# ---------- CURRENT USER STATE ----------
# None if no one logged in yet; otherwise:
# {"id": int, "is_driver": bool, "area_code": str}
current_user = None

# ---------- HELPERS ----------

def reset_profile_form():
    """Reset profile page state when starting a new signup."""
    user_type['value'] = None
    traveling_schedule['value'] = None
    location['value'] = None
    schedule_input.clear()
    location_input.clear()
    location_details.clear()
    profile_stack.setCurrentIndex(0)
    update_button_states()

# ---------- NAVIGATION FUNCTIONS ----------

def go_sign():
    """Go to signup page from login."""
    reset_profile_form()
    stack.setCurrentWidget(signPage)

def go_login():
    """Go to login page from anywhere."""
    stack.setCurrentWidget(loginPage)

def go_profile():
    """Go to profile page (from signup or home)."""
    stack.setCurrentWidget(profilePage)

def go_home():
    """Go to passenger home page."""
    stack.setCurrentWidget(home)

def go_driver_home():
    """Go to driver home page."""
    stack.setCurrentWidget(driver_home)

# ---------- AUTH / DB LOGIC ----------

def save_profile():
    """
    Called when:
    - finishing profile in signup flow (no current_user yet)
    - editing profile from home (current_user is set)
    """
    global current_user

    # Common checks: type + location
    if user_type['value'] not in ('driver', 'passenger'):
        QMessageBox.warning(window, "Error", "Please select if you are a driver or passenger.")
        return

    if not location_input.text().strip():
        QMessageBox.warning(window, "Error", "Please select your location / area.")
        return

    is_driver_int = 1 if user_type['value'] == 'driver' else 0
    area_code = location_input.text().strip()

    # ---- CASE 1: NEW USER (SIGNUP FLOW) ----
    if current_user is None:
        username = username_input_signup.text().strip()
        password = password_input_signup.text()

        if not username or not password:
            QMessageBox.warning(
                window,
                "Error",
                "Please enter username and password on the signup page."
            )
            stack.setCurrentWidget(signPage)
            return

        if username_exists(username):
            QMessageBox.warning(
                window,
                "Error",
                "Username already exists. Please choose another or log in."
            )
            stack.setCurrentWidget(loginPage)
            return

        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        name = username
        email = f"{username}@example.com"
        created_at = current_timestamp()

        try:
            user_id = create_user(
                name,
                email,
                username,
                pwd_hash,
                is_driver_int,
                area_code,
                created_at
            )
        except Exception as e:
            QMessageBox.critical(window, "Error", f"Failed to create account:\n{e}")
            return

        # Set current_user now that we've created them
        current_user = {
            "id": user_id,
            "is_driver": bool(is_driver_int),
            "area_code": area_code,
        }

        QMessageBox.information(window, "Success", "Profile saved and account created!")

    # ---- CASE 2: EXISTING USER (EDIT PROFILE) ----
    else:
        try:
            update_user_profile(current_user["id"], is_driver_int, area_code)
        except Exception as e:
            QMessageBox.critical(window, "Error", f"Failed to update profile:\n{e}")
            return

        current_user["is_driver"] = bool(is_driver_int)
        current_user["area_code"] = area_code
        QMessageBox.information(window, "Success", "Profile updated!")

    # Route to correct home screen according to role
    if current_user["is_driver"]:
        go_driver_home()
    else:
        go_home()

    # For signup flow, clear signup fields & reset profile page
    username_input_signup.clear()
    password_input_signup.clear()
    reset_profile_form()

def handle_login():
    """
    Called when 'Login' button is clicked on the login page.
    Checks username + password against DB and routes to home/driver_home.
    """
    global current_user

    username = username_input.text().strip()
    password = password_input.text()

    if not username or not password:
        QMessageBox.warning(window, "Error", "Please enter username and password.")
        return

    user = get_user_for_login(username)
    if user is None:
        QMessageBox.warning(window, "Error", "Username not found.")
        return

    entered_hash = hashlib.sha256(password.encode()).hexdigest()
    if entered_hash != user["pwd_hash"]:
        QMessageBox.warning(window, "Error", "Incorrect password.")
        return

    is_driver = bool(user["is_driver"])

    # Set current_user from DB row
    current_user = {
        "id": user["id"],
        "is_driver": is_driver,
        "area_code": user["area_code"],
    }

    if is_driver:
        go_driver_home()
    else:
        go_home()

    QMessageBox.information(window, "Login successful", f"Welcome, {username}!")

# ---------- CONNECT BUTTONS ----------

# From login -> signup
signlog_btn.clicked.connect(go_sign)

# From signup -> login
logsign_btn.clicked.connect(go_login)

# From signup (sign button) -> profile
sign_btn.clicked.connect(go_profile)

# From home sidebar "Profile" -> profile page (edit mode)
btn1.clicked.connect(go_profile)   # btn1 = "Profile" button from home.py

# From driver_home sidebar "Profile" -> profile
from driver_home import btn1 as driver_profile_btn
driver_profile_btn.clicked.connect(go_profile)

# Login button -> DB-auth login handler
login_btn.clicked.connect(handle_login)

# Logout buttons -> back to login
logout_btn.clicked.connect(go_login)
logout_btn_driver.clicked.connect(go_login)

# Confirm on profile page -> create/update user and go to home/driver_home
btn_confirm.clicked.connect(save_profile)

# ---------- SHOW WINDOW ----------
stack.setCurrentWidget(loginPage)  # start at login
window.show()
sys.exit(app.exec_())
