from PyQt6.QtWidgets import QApplication, QTableWidget
from image_widget import ImageWidget


class TableWidget(QTableWidget):
    def setImage(self, row, col, imagePath, imageWidth, imageHeight):
        image = ImageWidget(imagePath, imageWidth, imageHeight, self)
        self.setCellWidget(row, col, image)
