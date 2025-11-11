# this page is used to quickyl change attributes to modify the gui 
# instead of going through the structure itself


user_pass_input_style = """
            QLineEdit {
                background-color: lightblue;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                margin-bottom: 100px;
            }
        """


loginbutton_style = """
            QPushButton {
                color: white;
                border: 2px solid #2196F3;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #2196F3;
            }
            QPushButton:hover {
                background-color: #2196F3;
                color: white;
            }
        """
# changing the cursor doesnt work through css
#ie cursor: pointer; on hover
signupbutton_style = """
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
        """

noAccount_ask = """
    QPushButton {     
        margin-bottom: 50px;
        text-align: left;
        text-decoration: none;
        background: none;
        border: none;
        margin: 10px;
    }
    QPushButton:hover {
        text-decoration: underline;
        color: blue;
    }
"""


homeSide_btn_style = """
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    border: none;
                    padding: 15px;
                    text-align: left;
                    margin-top: 10px;
                    margin-bottom: 10px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """