from PyQt6.QtWidgets import QWidget
from PyQt6 import QtGui
from PyQt6.QtCore import Qt


class ImageWidget(QWidget):
    def __init__(self, image_path, width, height, parent):
        super(ImageWidget, self).__init__(parent)
        self.picture = QtGui.QPixmap(image_path).scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.picture)

