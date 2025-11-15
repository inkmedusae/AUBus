import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from stylinginfo import *

class LoginScreen(QWidget):
    def __init__(self, on_login_success, switch_to_signup):
        super().__init__()
        self.on_login_success = on_login_success
        self.switch_to_signup = switch_to_signup
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title = QLabel("Login")
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumWidth(300)
        self.username_input.setMinimumHeight(40)
        layout.addWidget(self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.returnPressed.connect(self.login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(10)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(45)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)
        
        layout.addSpacing(15)
        
        # Switch to signup
        signup_label = QLabel("Don't have an account?")
        signup_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(signup_label)
        
        signup_btn = QPushButton("Sign Up")
        signup_btn.setMinimumHeight(40)
        signup_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2196F3;
                border: 2px solid #2196F3;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2196F3;
                color: white;
            }
        """)
        signup_btn.clicked.connect(self.switch_to_signup)
        layout.addWidget(signup_btn)
        
        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        # Simple validation - just check if fields are filled
        self.on_login_success(username)

class SignupScreen(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        self.switch_to_login = switch_to_login
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title = QLabel("Sign Up")
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumWidth(300)
        self.username_input.setMinimumHeight(40)
        layout.addWidget(self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        layout.addWidget(self.password_input)
        
        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setMinimumHeight(40)
        self.confirm_password_input.returnPressed.connect(self.signup)
        layout.addWidget(self.confirm_password_input)
        
        layout.addSpacing(10)
        
        # Signup button
        signup_btn = QPushButton("Sign Up")
        signup_btn.setMinimumHeight(45)
        signup_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        signup_btn.clicked.connect(self.signup)
        layout.addWidget(signup_btn)
        
        layout.addSpacing(15)
        
        # Switch to login
        login_label = QLabel("Already have an account?")
        login_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(login_label)
        
        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(40)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
        """)
        login_btn.clicked.connect(self.switch_to_login)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
    
    def signup(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm = self.confirm_password_input.text()
        
        if not username or not password or not confirm:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
        
        QMessageBox.information(self, "Success", "Account created successfully!")
        self.switch_to_login()

class MainScreen(QWidget):
    def __init__(self, username, on_logout):
        super().__init__()
        self.username = username
        self.on_logout = on_logout
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Welcome message
        welcome = QLabel(f"Welcome, {self.username}!")
        welcome.setFont(QFont('Arial', 28, QFont.Bold))
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
        
        layout.addSpacing(20)
        
        # Content area
        content = QLabel("You have successfully logged in!")
        content.setFont(QFont('Arial', 16))
        content.setAlignment(Qt.AlignCenter)
        layout.addWidget(content)
        
        layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setMinimumHeight(45)
        logout_btn.setMaximumWidth(200)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        logout_btn.clicked.connect(self.on_logout)
        
        logout_layout = QHBoxLayout()
        logout_layout.addStretch()
        logout_layout.addWidget(logout_btn)
        logout_layout.addStretch()
        layout.addLayout(logout_layout)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Login System")
        self.setGeometry(100, 100, 500, 600)
        
        # Central widget with stacked layout
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create screens
        self.login_screen = LoginScreen(
            self.on_login_success, 
            lambda: self.stacked_widget.setCurrentIndex(1)
        )
        self.signup_screen = SignupScreen(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.signup_screen)
        
        # Start with login screen
        self.stacked_widget.setCurrentIndex(0)
    
    def on_login_success(self, username):
        self.current_user = username
        # Create and show main screen
        main_screen = MainScreen(username, self.on_logout)
        self.stacked_widget.addWidget(main_screen)
        self.stacked_widget.setCurrentWidget(main_screen)
    
    def on_logout(self):
        self.current_user = None
        # Remove main screen
        if self.stacked_widget.count() > 2:
            widget = self.stacked_widget.widget(2)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        # Return to login screen
        self.stacked_widget.setCurrentIndex(0)
        # Clear login fields
        self.login_screen.username_input.clear()
        self.login_screen.password_input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())