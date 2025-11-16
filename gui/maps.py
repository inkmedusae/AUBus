# from pathlib import Path
# from PyQt5.QtWidgets import *
# from PyQt5.QtWebEngineWidgets import QWebEngineView
# from PyQt5.QtWebChannel import QWebChannel
# import json

# class LeafletMap(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.view = QWebEngineView(self)

#         html_path = Path(__file__).with_name("map.html")
#         self.view.setUrl(QUrl.fromLocalFile(str(html_path.resolve())))

#         layout = QVBoxLayout(self)
#         layout.addWidget(self.view)

#     def update_markers(self, rows):
#         payload = json.dumps(rows)
#         js = f"addMarkersFromJson({json.dumps(payload)});"
#         self.view.page().runJavaScript(js)

# def main():
#     app = QApplication(sys.argv)
#     window = LeafletMap()
#     window.show()
#     sys.exit(app.exec_())
