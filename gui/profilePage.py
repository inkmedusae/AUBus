from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from stylinginfo import *



profilePage = QWidget()
main_layout = QVBoxLayout()

profile_title = QLabel("Create Your Profile")
profile_title.setFont(QFont('Arial', 24, QFont.Bold))
profile_title.setAlignment(Qt.AlignCenter)
main_layout.addWidget(profile_title)
main_layout.addSpacing(20)


profile_stack = QStackedWidget()
main_layout.addWidget(profile_stack)


user_type = {'value': None}
traveling_schedule = {'value': None}
location = {'value': None}

user_type_widget = QWidget()
ut_layout = QVBoxLayout()

ut_label = QLabel("What type of user are you?")
ut_label.setFont(QFont('Arial', 16, QFont.Bold))
ut_label.setAlignment(Qt.AlignCenter)
ut_layout.addWidget(ut_label)
ut_layout.addSpacing(30)

btn_row = QHBoxLayout()
btn_driver = QPushButton("Driver")
btn_driver.setMinimumHeight(60)
btn_driver.setFont(QFont('Arial', 14))
btn_passenger = QPushButton("Passenger")
btn_passenger.setMinimumHeight(60)
btn_passenger.setFont(QFont('Arial', 14))
btn_row.addWidget(btn_driver)
btn_row.addSpacing(30)
btn_row.addWidget(btn_passenger)
ut_layout.addLayout(btn_row)
ut_layout.addStretch()
user_type_widget.setLayout(ut_layout)


schedule_widget = QWidget()
schedule_layout = QVBoxLayout()
sch_label = QLabel("What time do you leave each day?")
sch_label.setFont(QFont('Arial', 16, QFont.Bold))
sch_label.setAlignment(Qt.AlignCenter)
schedule_layout.addWidget(sch_label)
schedule_layout.addSpacing(20)
sch_info = QLabel("Enter your departure time for each day of the week")
sch_info.setAlignment(Qt.AlignCenter)
schedule_layout.addWidget(sch_info)
schedule_layout.addSpacing(15)

# Create time pickers for each day of the week
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
schedule_inputs = {}
schedule_container = QWidget()
schedule_form = QGridLayout()

for i, day in enumerate(days_of_week):
    day_label = QLabel(day)
    day_label.setFont(QFont('Arial', 12))
    time_input = QTimeEdit()
    time_input.setDisplayFormat('HH:mm')
    time_input.setTime(QTime(8, 0))  # Default to 8:00 AM
    time_input.setMinimumHeight(35)
    schedule_inputs[day] = time_input
    schedule_form.addWidget(day_label, i, 0)
    schedule_form.addWidget(time_input, i, 1)

schedule_form.setColumnStretch(0, 1)
schedule_form.setColumnStretch(1, 2)
schedule_container.setLayout(schedule_form)
schedule_layout.addWidget(schedule_container)
schedule_layout.addStretch()
schedule_widget.setLayout(schedule_layout)


location_widget = QWidget()
location_layout = QVBoxLayout()
loc_label = QLabel("What is your location?")
loc_label.setFont(QFont('Arial', 16, QFont.Bold))
loc_label.setAlignment(Qt.AlignCenter)
location_layout.addWidget(loc_label)
location_layout.addSpacing(20)
loc_info = QLabel("Enter your pickup/dropoff location")
loc_info.setAlignment(Qt.AlignCenter)
location_layout.addWidget(loc_info)
location_layout.addSpacing(15)
location_input = QLineEdit()
location_input.setPlaceholderText("e.g., Beirut, Lebanon or specific address")
location_input.setMinimumHeight(40)
location_layout.addWidget(location_input)
location_layout.addSpacing(15)
location_details = QLineEdit()
location_details.setPlaceholderText("Additional location details (optional)")
location_details.setMinimumHeight(40)
location_layout.addWidget(location_details)
location_layout.addStretch()
location_widget.setLayout(location_layout)

# --- Step 4: Summary ---
summary_widget = QWidget()
summary_layout = QVBoxLayout()
sum_label = QLabel("Profile Summary")
sum_label.setFont(QFont('Arial', 16, QFont.Bold))
sum_label.setAlignment(Qt.AlignCenter)
summary_layout.addWidget(sum_label)
summary_layout.addSpacing(20)
summary_text = QTextEdit()
summary_text.setReadOnly(True)
summary_text.setMinimumHeight(250)
summary_layout.addWidget(summary_text)
summary_layout.addSpacing(20)
btn_confirm = QPushButton("Confirm & Save Profile")
btn_confirm.setMinimumHeight(50)
btn_confirm.setFont(QFont('Arial', 12, QFont.Bold))
summary_layout.addWidget(btn_confirm)
summary_layout.addStretch()
summary_widget.setLayout(summary_layout)

# Add screens to stack
profile_stack.addWidget(user_type_widget)
profile_stack.addWidget(schedule_widget)
profile_stack.addWidget(location_widget)
profile_stack.addWidget(summary_widget)


back_arrow_layout = QHBoxLayout()
btn_back = QToolButton()
btn_back.setIcon(btn_back.style().standardIcon(QStyle.SP_ArrowBack))
btn_back.setToolTip("Back")
btn_back.setFixedSize(36, 36)
back_arrow_layout.addWidget(btn_back, alignment=Qt.AlignLeft)
back_arrow_layout.addStretch()
main_layout.insertLayout(0, back_arrow_layout)

profilePage.setLayout(main_layout)

def update_summary():
    summary = f"<b>Profile Summary</b><br><br>"
    summary += f"<b>User Type:</b> {user_type['value'].capitalize()}<br>" if user_type['value'] else ""
    if user_type['value'] == "driver":
        summary += f"<b>Departure Schedule:</b><br>"
        for day, time_input in schedule_inputs.items():
            summary += f"{day}: {time_input.time().toString('HH:mm')}<br>"
        summary += "<br>"
    summary += f"<b>Location:</b> {location['value']}"
    if location_details.text():
        summary += f"<br><b>Details:</b> {location_details.text()}"
    summary_text.setHtml(summary)

def go_next():
    current_index = profile_stack.currentIndex()
    if current_index == 0:  # User Type -> Schedule (if driver) or Location (if passenger)
        if user_type['value'] == "driver":
            profile_stack.setCurrentIndex(1)
        else:
            profile_stack.setCurrentIndex(2)
    elif current_index == 1:  # Schedule -> Location
        # Capture schedule from time pickers
        traveling_schedule['value'] = {day: time_input.time().toString('HH:mm') for day, time_input in schedule_inputs.items()}
        profile_stack.setCurrentIndex(2)
    elif current_index == 2:  # Location -> Summary
        location['value'] = location_input.text()
        update_summary()
        profile_stack.setCurrentIndex(3)
    update_button_states()

def go_previous():
    current_index = profile_stack.currentIndex()
    if current_index == 3:  # Summary -> Location
        profile_stack.setCurrentIndex(2)
    elif current_index == 2:  # Location -> Schedule (if driver) or User Type (if passenger)
        if user_type['value'] == "driver":
            profile_stack.setCurrentIndex(1)
        else:
            profile_stack.setCurrentIndex(0)
    elif current_index == 1:  # Schedule -> User Type
        profile_stack.setCurrentIndex(0)
    update_button_states()

def update_button_states():
    current_index = profile_stack.currentIndex()
    # Only enable back arrow if not on the first screen
    btn_back.setEnabled(current_index > 0)
    btn_back.setVisible(current_index > 0)

def select_user_type_driver():
    user_type['value'] = "driver"
    go_next()
def select_user_type_passenger():
    user_type['value'] = "passenger"
    go_next()

btn_driver.clicked.connect(select_user_type_driver)
btn_passenger.clicked.connect(select_user_type_passenger)
btn_back.clicked.connect(go_previous)

# Add a button to proceed from schedule page since time pickers don't have return key
schedule_next_btn = QPushButton("Next")
schedule_next_btn.setMinimumHeight(50)
schedule_next_btn.setFont(QFont('Arial', 12, QFont.Bold))
schedule_layout.addWidget(schedule_next_btn)
schedule_next_btn.clicked.connect(go_next)

def on_location_enter():
    if location_input.text().strip():
        go_next()
location_input.returnPressed.connect(on_location_enter)



profile_stack.setCurrentIndex(0)
update_button_states()