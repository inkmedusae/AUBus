import sys
import requests
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

key = "7a77199e48174a098bf174356251411"


class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = "7a77199e48174a098bf174356251411"  # Replace with your actual API key
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("3-Day Weather Forecast")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2C3E50;")
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Weather Forecast")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #ECF0F1;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Search section
        search_layout = QHBoxLayout()
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter city name (e.g., London, New York)")
        self.location_input.setFont(QFont("Arial", 12))
        self.location_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #34495E;
                border-radius: 5px;
                background-color: #ECF0F1;
                color: #2C3E50;
            }
        """)
        self.location_input.returnPressed.connect(self.get_weather)
        
        search_btn = QPushButton("Get Weather")
        search_btn.setFont(QFont("Arial", 12, QFont.Bold))
        search_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        search_btn.clicked.connect(self.get_weather)
        
        search_layout.addWidget(self.location_input)
        search_layout.addWidget(search_btn)
        main_layout.addLayout(search_layout)
        
        # Current weather display
        self.current_weather_label = QLabel("Enter a location to see the weather")
        self.current_weather_label.setFont(QFont("Arial", 14))
        self.current_weather_label.setStyleSheet("color: #ECF0F1; padding: 20px;")
        self.current_weather_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.current_weather_label)
        
        # 3-day forecast container
        self.forecast_layout = QHBoxLayout()
        self.forecast_layout.setSpacing(15)
        main_layout.addLayout(self.forecast_layout)
        
        main_layout.addStretch()
    
    def get_weather(self):
        """Fetch weather data from WeatherAPI"""
        location = self.location_input.text().strip()
        
        if not location:
            QMessageBox.warning(self, "Error", "Please enter a location")
            return
        
        if self.api_key == "YOUR_API_KEY_HERE":
            QMessageBox.warning(self, "Error", "Please set your API key in the code")
            return
        
        try:
            # API request
            url = f"http://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={location}&days=3&aqi=no"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.display_weather(data)
            
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch weather data:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")
    
    def display_weather(self, data):
        """Display current weather and 3-day forecast"""
        # Clear previous forecast
        self.clear_forecast()
        
        # Display current weather
        location = data['location']
        current = data['current']
        
        current_text = f"""
        <h2>{location['name']}, {location['country']}</h2>
        <p style='font-size: 16px;'>
            <b>Temperature:</b> {current['temp_c']}°C ({current['temp_f']}°F)<br>
            <b>Condition:</b> {current['condition']['text']}<br>
            <b>Feels Like:</b> {current['feelslike_c']}°C<br>
            <b>Humidity:</b> {current['humidity']}%<br>
            <b>Wind:</b> {current['wind_kph']} km/h
        </p>
        """
        self.current_weather_label.setText(current_text)
        
        # Display 3-day forecast
        forecast_days = data['forecast']['forecastday']
        
        for day_data in forecast_days:
            day_widget = self.create_day_forecast(day_data)
            self.forecast_layout.addWidget(day_widget)
    
    def create_day_forecast(self, day_data):
        """Create a widget for a single day's forecast"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #34495E;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # Date
        date_label = QLabel(day_data['date'])
        date_label.setFont(QFont("Arial", 12, QFont.Bold))
        date_label.setStyleSheet("color: #3498DB;")
        date_label.setAlignment(Qt.AlignCenter)
        
        # Condition
        condition_label = QLabel(day_data['day']['condition']['text'])
        condition_label.setFont(QFont("Arial", 11))
        condition_label.setStyleSheet("color: #ECF0F1;")
        condition_label.setAlignment(Qt.AlignCenter)
        condition_label.setWordWrap(True)
        
        # Temperature
        temp_label = QLabel(f"Max: {day_data['day']['maxtemp_c']}°C\nMin: {day_data['day']['mintemp_c']}°C")
        temp_label.setFont(QFont("Arial", 11))
        temp_label.setStyleSheet("color: #ECF0F1;")
        temp_label.setAlignment(Qt.AlignCenter)
        
        # Additional info
        info_label = QLabel(
            f"Rain: {day_data['day']['daily_chance_of_rain']}%\n"
            f"Humidity: {day_data['day']['avghumidity']}%"
        )
        info_label.setFont(QFont("Arial", 9))
        info_label.setStyleSheet("color: #BDC3C7;")
        info_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(date_label)
        layout.addWidget(condition_label)
        layout.addWidget(temp_label)
        layout.addWidget(info_label)
        
        return frame
    
    def clear_forecast(self):
        """Clear previous forecast widgets"""
        while self.forecast_layout.count():
            item = self.forecast_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


def main():
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()