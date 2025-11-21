# this page is used to quickyl change attributes to modify the gui 
# instead of going through the structure itself

# color palette
# cadet gray -> #9AADBF
# air superiority blue -> #6D98BA
#tan -> #D3B99F
#old rose -> #C17767
# this page is used to quickyl change attributes to modify the gui 
# instead of going through the structure itself

# color palette
# cadet gray -> #9AADBF
# air superiority blue -> #6D98BA
#tan -> #D3B99F
#old rose -> #C17767
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
user_pass_input_style = """
            QLineEdit {
                background-color: lightblue;
                border: none;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 35px;
                margin-left: 125px;
                font-size: 14px;
            }
        """


loginbutton_style = """
            QPushButton {
                color: white;
                border: 2px solid #2196F3;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                margin-left: 250px;
                margin-right: 250px;
                color: #2196F3;
            }
            QPushButton:hover {
                background-color: #2196F3;
                color: white;
            }
        """
# changing the cursor doesnt work through css
#ie cursor: pointer; on hover


noAccount_ask = """
    QPushButton {     
        text-align: left;
        background: none;
        border: none;
        padding: 4px 6px;
    }
    QPushButton:hover {
        color: blue;
    }
"""


homeSide_btn_style = """
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    border: none;
                    padding: 12px 15px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """

request_style = """
    QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 12px;
                }
    QPushButton:hover {
                    background-color: #34495e;
                }
"""

textBubble_style = "color: #222; background: #2c3e50; border-radius: 8px; padding: 4px 8px; color: white;"
recBubble_style = "color: #222; background: #BDD5EA; border-radius: 8px; padding: 4px 8px; color: white;"

driver_button_styling = """
        QPushButton {
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 6px 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #34495e;
        }
    """