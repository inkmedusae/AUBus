from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from stylinginfo import *


class ProfileSetupWizard(QWidget):
    """Multi-step profile setup wizard using QStackedWidget.
    
    Flow:
    1. User Type Selection (Driver or Passenger)
    2. If Driver: Ask for traveling schedule
    3. Location (both driver and passenger)
    4. Summary/Confirmation
    """
    
    def __init__(self):
        super().__init__()
        self.user_type = None
        self.traveling_schedule = None
        self.location = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the main layout with stacked widget."""
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Create Your Profile")
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        main_layout.addSpacing(20)
        
        # Stacked widget to hold different screens
        self.stack = QStackedWidget()
        
        # Create all screens
        self.screen_user_type = self.create_user_type_screen()
        self.screen_traveling_schedule = self.create_traveling_schedule_screen()
        self.screen_location = self.create_location_screen()
        self.screen_summary = self.create_summary_screen()
        
        # Add screens to stack
        self.stack.addWidget(self.screen_user_type)
        self.stack.addWidget(self.screen_traveling_schedule)
        self.stack.addWidget(self.screen_location)
        self.stack.addWidget(self.screen_summary)
        
        main_layout.addWidget(self.stack)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        
        self.btn_previous = QPushButton("Previous")
        self.btn_previous.clicked.connect(self.go_previous)
        self.btn_previous.setEnabled(False)
        nav_layout.addWidget(self.btn_previous)
        
        self.btn_next = QPushButton("Next")
        self.btn_next.clicked.connect(self.go_next)
        nav_layout.addWidget(self.btn_next)
        
        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)
        
        self.setLayout(main_layout)
    
    def create_user_type_screen(self):
        """Screen 1: Ask if user is Driver or Passenger."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("What type of user are you?")
        label.setFont(QFont('Arial', 16, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        layout.addSpacing(30)
        
        # Driver button
        btn_driver = QPushButton("Driver")
        btn_driver.setMinimumHeight(60)
        btn_driver.setFont(QFont('Arial', 14))
        btn_driver.clicked.connect(lambda: self.select_user_type("driver"))
        layout.addWidget(btn_driver)
        
        layout.addSpacing(15)
        
        # Passenger button
        btn_passenger = QPushButton("Passenger")
        btn_passenger.setMinimumHeight(60)
        btn_passenger.setFont(QFont('Arial', 14))
        btn_passenger.clicked.connect(lambda: self.select_user_type("passenger"))
        layout.addWidget(btn_passenger)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_traveling_schedule_screen(self):
        """Screen 2 (Driver only): Ask for traveling schedule."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("What is your traveling schedule?")
        label.setFont(QFont('Arial', 16, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        layout.addSpacing(20)
        
        info_label = QLabel("Enter your travel days and times")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        layout.addSpacing(15)
        
        # Schedule input
        self.schedule_input = QTextEdit()
        self.schedule_input.setPlaceholderText(
            "Example:\nMonday-Friday: 8:00 AM - 5:00 PM\nSaturday: 10:00 AM - 2:00 PM"
        )
        self.schedule_input.setMinimumHeight(150)
        layout.addWidget(self.schedule_input)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_location_screen(self):
        """Screen 2/3: Ask for location (common for both)."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("What is your location?")
        label.setFont(QFont('Arial', 16, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        layout.addSpacing(20)
        
        info_label = QLabel("Enter your pickup/dropoff location")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        layout.addSpacing(15)
        
        # Location input (city/address)
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g., Beirut, Lebanon or specific address")
        self.location_input.setMinimumHeight(40)
        layout.addWidget(self.location_input)
        
        layout.addSpacing(15)
        
        # Optional: more detailed location
        self.location_details = QLineEdit()
        self.location_details.setPlaceholderText("Additional location details (optional)")
        self.location_details.setMinimumHeight(40)
        layout.addWidget(self.location_details)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_summary_screen(self):
        """Screen 4: Display summary of entered information."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("Profile Summary")
        label.setFont(QFont('Arial', 16, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        layout.addSpacing(20)
        
        # Summary display
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(250)
        layout.addWidget(self.summary_text)
        
        layout.addSpacing(20)
        
        # Confirm button
        btn_confirm = QPushButton("Confirm & Save Profile")
        btn_confirm.setMinimumHeight(50)
        btn_confirm.setFont(QFont('Arial', 12, QFont.Bold))
        btn_confirm.clicked.connect(self.save_profile)
        layout.addWidget(btn_confirm)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def select_user_type(self, user_type):
        """Handle user type selection."""
        self.user_type = user_type
        self.go_next()
    
    def go_next(self):
        """Navigate to next screen based on current state."""
        current_index = self.stack.currentIndex()
        
        if current_index == 0:  # User Type -> Schedule (if driver) or Location (if passenger)
            if self.user_type == "driver":
                self.stack.setCurrentIndex(1)  # Go to schedule
            else:  # passenger
                self.stack.setCurrentIndex(2)  # Skip schedule, go to location
        elif current_index == 1:  # Schedule -> Location
            self.traveling_schedule = self.schedule_input.toPlainText()
            self.stack.setCurrentIndex(2)
        elif current_index == 2:  # Location -> Summary
            self.location = self.location_input.text()
            self.update_summary()
            self.stack.setCurrentIndex(3)
        
        self.update_button_states()
    
    def go_previous(self):
        """Navigate to previous screen."""
        current_index = self.stack.currentIndex()
        
        if current_index == 3:  # Summary -> Location
            self.stack.setCurrentIndex(2)
        elif current_index == 2:  # Location -> Schedule (if driver) or User Type (if passenger)
            if self.user_type == "driver":
                self.stack.setCurrentIndex(1)
            else:
                self.stack.setCurrentIndex(0)
        elif current_index == 1:  # Schedule -> User Type
            self.stack.setCurrentIndex(0)
        
        self.update_button_states()
    
    def update_button_states(self):
        """Enable/disable navigation buttons based on current screen."""
        current_index = self.stack.currentIndex()
        
        # Disable previous on first screen
        self.btn_previous.setEnabled(current_index > 0)
        
        # Hide next on last screen
        self.btn_next.setEnabled(current_index < 3)
    
    def update_summary(self):
        """Update the summary screen with entered information."""
        summary = f"<b>Profile Summary</b><br><br>"
        summary += f"<b>User Type:</b> {self.user_type.capitalize()}<br>"
        
        if self.user_type == "driver":
            summary += f"<b>Traveling Schedule:</b><br>{self.traveling_schedule}<br><br>"
        
        summary += f"<b>Location:</b> {self.location}"
        if self.location_details.text():
            summary += f"<br><b>Details:</b> {self.location_details.text()}"
        
        self.summary_text.setHtml(summary)
    
    def save_profile(self):
        """Save the profile (placeholder for actual save logic)."""
        QMessageBox.information(
            self,
            "Profile Saved",
            f"Profile created successfully!\n\nUser Type: {self.user_type}\nLocation: {self.location}"
        )
        # TODO: Send data to backend/database


# Create the main profile page widget
profilePage = QWidget()
profile_creation_layout = QVBoxLayout()

wizard = ProfileSetupWizard()
profile_creation_layout.addWidget(wizard)

profilePage.setLayout(profile_creation_layout)