from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from scrol_label import ScrollLabel

class DetailsWindow(QMainWindow):
    def __init__(self, parent=None):
        super(DetailsWindow, self).__init__(parent)

        self.setWindowTitle('Описание фильма')

        self.movie_title = QLabel()
        self.movie_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie_title.setWordWrap(True)
        self.movie_title.setStyleSheet("font-weight: bold; color: black; font-size:36px;")

        self.movie_year = QLabel()
        self.movie_year.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie_year.setStyleSheet("font-weight: bold; color: black; font-size:25px;")

        self.movie_description = ScrollLabel()
        self.movie_description.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        #self.movie_description.label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)

        layout = QVBoxLayout()

        widget = QWidget()
        widget.setLayout(layout)

        layout.addWidget(self.movie_title)
        layout.addWidget(self.movie_year)
        layout.addWidget(self.movie_description)

        self.setCentralWidget(widget)

    def set_window_to_center(self):
        screen = QApplication.instance().primaryScreen().availableGeometry()
        self.resize_window()
        center_x = abs((self.geometry().width() - screen.width()) // 2)
        center_y = abs((self.geometry().height() - screen.height()) // 2)
        self.move(center_x, center_y)

    def resize_window(self):
        width, height = self.get_screen_size()
        self.setMinimumSize(int(width // 3), int(height // 1.4))

    def get_screen_size(self):
        screen = QApplication.instance().primaryScreen().availableGeometry()
        return int(screen.width()), int(screen.height())
