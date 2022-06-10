#!/usr/bin/env python

from PyQt6.QtCore import QDateTime, Qt, QTimer
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget, QTableView, QMainWindow, QMenu)
from table_widget import TableWidget
from details import DetailsWindow
import json


class AppWindow(QMainWindow):
    def exit_app(self):
        sys.exit()

    def __init__(self, parent=None):
        super(AppWindow, self).__init__(parent)

        with open('configs.json', encoding='utf-8') as json_file:
            self.configs = json.load(json_file)

        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.configs['DATABASE_PATH'])
        self.db.open()
        self.query = QSqlQuery()
        print(self.db.__str__())
        print(self.query)

        self.setCenterLocation()

        widget = QWidget(self)
        self.setCentralWidget(widget)

        self.originalPalette = QApplication.palette()

        menuBar = self.menuBar()
        fileMenu = QMenu('&Файл', self)
        exit_action = QAction('&Выход', self)
        exit_action.triggered.connect(self.exit_app)
        fileMenu.addAction(exit_action)
        menuBar.addMenu(fileMenu)

        disable_all_elements = QCheckBox("&Отключить все элементы")

        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomTabWidget()
        self.createProgressBar()

        self.statusBar().showMessage(self.configs['HINT_MESSAGE'])

        disable_all_elements.toggled.connect(self.topLeftGroupBox.setDisabled)
        disable_all_elements.toggled.connect(self.topRightGroupBox.setDisabled)
        disable_all_elements.toggled.connect(self.bottomTabWidget.setDisabled)

        top_layout = QHBoxLayout()
        top_layout.addWidget(disable_all_elements)

        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.topLeftGroupBox)
        middle_layout.addWidget(self.topRightGroupBox)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.bottomTabWidget)

        main_layout = QVBoxLayout()

        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(self.bottomTabWidget)
        main_layout.addLayout(bottom_layout)
        #main_layout.addWidget(self.progressBar)

        widget.setLayout(main_layout)
        self.bottomTabWidget.setMinimumHeight(500)
        self.setMinimumSize(1000, 600)

        self.filter = ''
        self.setWindowTitle("EnjoyMovie")
        QApplication.setStyle('Fusion')

    def setCenterLocation(self):
        screen = QApplication.instance().primaryScreen().availableGeometry()
        self.resizeWindow()
        center_x = abs((self.geometry().width() - screen.width()) // 2)
        center_y = abs((self.geometry().height() - screen.height()) // 2)
        self.move(center_x, center_y)

    def get_screen_size(self):
        screen = QApplication.instance().primaryScreen().availableGeometry()
        return int(screen.width()), int(screen.height())

    def resizeWindow(self):
        width, height = self.get_screen_size()
        self.setFixedSize(int(width // 1.7), int(height // 1.25))

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) // 100)

    def country_change(self, element_index):
        selected_country = self.country_cb.itemText(element_index)
        self.year_from_slider.setValue(self.configs['MINIMUM_YEAR'])
        self.year_to_slider.setValue(self.configs['MAXIMUM_YEAR'])

        if selected_country != 'Все страны':
            self.query.exec(f'SELECT id FROM countries WHERE name="{selected_country}"')
            self.query.first()
            country_id = self.query.value(0)

            self.filter = f'country_id = {country_id}'
            self.movies_model.setFilter(self.filter)
            self.movies_model.select()
        else:
            self.filter = ''
            self.movies_model.setFilter(self.filter)
            self.movies_model.select()

        self.tableWidget.setRowCount(0)

        self.tableWidget.setRowCount(self.movies_model.rowCount())
        for i in range(self.movies_model.rowCount()):
            columns = ['id', 'movie', 'country_id', 'rating_ball']
            for j in range(len(columns)):
                value = self.movies_model.record(i).value(columns[j])
                if columns[j] == 'country_id':
                    self.query.exec(f'SELECT id, name FROM countries where id={value}')
                    self.query.first()
                    value = self.query.value(1)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
            movie_id = self.movies_model.record(i).value('id')
            poster_pixmap = QPixmap(f'{self.configs["POSTERS_PATH"]}poster_{movie_id}.jpg')
            self.tableWidget.setImage(i, len(columns), poster_pixmap, 130, 180)

    def from_slider_change(self):
        current_min_year = self.year_from_slider.value()
        current_max_year = self.year_to_slider.value()
        if current_min_year > current_max_year:
            current_min_year = self.year_to_slider.value()
            self.year_from_slider.setValue(self.year_to_slider.value())
        self.year_from_label.setText(f'Выберите год (от): {str(current_min_year)}')

    def to_slider_change(self):
        current_max_year = self.year_to_slider.value()
        current_min_year = self.year_from_slider.value()
        if current_max_year < current_min_year:
            current_max_year = self.year_from_slider.value()
            self.year_to_slider.setValue(self.year_from_slider.value())
        self.year_to_label.setText(f'Выберите год (до): {str(current_max_year)}')

    def filter_movies(self):
        country = self.country_cb.currentText()
        min_year = str(self.year_from_slider.value())
        max_year = str(self.year_to_slider.value())

        print("CURRENT TEXT:", country)

        if country != 'Все страны':
            self.query.exec(f'SELECT id FROM countries WHERE name="{country}"')
            self.query.first()
            country_id = self.query.value(0)

            self.filter = f'country_id = {country_id} AND'
            self.movies_model.select()
        else:
            self.filter = ''
            self.movies_model.select()

        self.filter += f' year > {min_year} AND year < {max_year}'
        print(self.filter)

        self.movies_model.setFilter(self.filter)

        self.tableWidget.setRowCount(0)

        self.tableWidget.setRowCount(self.movies_model.rowCount())
        for i in range(self.movies_model.rowCount()):
            columns = ['id', 'movie', 'country_id', 'rating_ball']
            for j in range(len(columns)):
                value = self.movies_model.record(i).value(columns[j])
                if columns[j] == 'country_id':
                    self.query.exec(f'SELECT id, name FROM countries where id={value}')
                    self.query.first()
                    value = self.query.value(1)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
            movie_id = self.movies_model.record(i).value('id')
            poster_pixmap = QPixmap(f'{self.configs["POSTERS_PATH"]}poster_{movie_id}.jpg')
            self.tableWidget.setImage(i, len(columns), poster_pixmap, 130, 180)

    def search_text_change(self):
        movie_query_text = self.search_bar.toPlainText().upper()
        print(movie_query_text)
        if movie_query_text == '':
            return

        string_query = 'SELECT * FROM movies'
        if self.filter != '':
            string_query += f'WHERE {self.filter}'

        q = QSqlQuery(string_query)

        search_results = []
        while q.next():
            id = q.value('id')
            movie = q.value('movie')

            movie = movie.upper()
            if movie_query_text in movie:
                search_results.append(int(id))

        search_results.extend([1000, 10000]) # чтобы избавиться от запятой в одноэлементом tuple (кортеже)

        if self.filter == '':
            new_filter = f"id in {tuple(search_results)}"
        else:
            new_filter = f"{self.filter} AND id in {tuple(search_results)}%'"

        if len(search_results) > 0:
            self.movies_model.setFilter(new_filter)


        self.tableWidget.setRowCount(0)

        self.tableWidget.setRowCount(self.movies_model.rowCount())
        for i in range(self.movies_model.rowCount()):
            columns = ['id', 'movie', 'country_id', 'rating_ball']
            for j in range(len(columns)):
                value = self.movies_model.record(i).value(columns[j])
                if columns[j] == 'country_id':
                    self.query.exec(f'SELECT id, name FROM countries where id={value}')
                    self.query.first()
                    value = self.query.value(1)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
            movie_id = self.movies_model.record(i).value('id')
            poster_pixmap = QPixmap(f'{self.configs["POSTERS_PATH"]}poster_{movie_id}.jpg')
            self.tableWidget.setImage(i, len(columns), poster_pixmap, 130, 180)


    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Фильтрация")

        unique_countries_list = ['Все страны']
        self.query.exec(f'SELECT name FROM countries')

        while self.query.next():
            unique_countries_list.append(self.query.value(0))

        self.country_label = QLabel()
        self.country_label.setText('Выберите страну:')

        self.country_cb = QComboBox()
        self.country_cb.addItems(unique_countries_list)
        self.country_cb.currentIndexChanged.connect(self.country_change)

        self.year_from_label = QLabel()
        self.year_from_label.setText(f"Выберите год (от): {self.configs['MINIMUM_YEAR']}")

        self.year_from_slider = QSlider(Qt.Orientation.Horizontal)
        self.year_from_slider.setMinimum(self.configs['MINIMUM_YEAR'])
        self.year_from_slider.setMaximum(self.configs['MAXIMUM_YEAR'])
        self.year_from_slider.setValue(self.configs['MINIMUM_YEAR'])
        self.year_from_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.year_from_slider.setTickInterval(30)
        self.year_from_slider.valueChanged.connect(self.from_slider_change)

        self.year_to_label = QLabel()
        self.year_to_label.setText('Выберите год (до):')

        self.year_to_slider = QSlider(Qt.Orientation.Horizontal)
        self.year_to_slider.setMinimum(self.configs['MINIMUM_YEAR'])
        self.year_to_slider.setMaximum(self.configs['MAXIMUM_YEAR'])
        self.year_to_slider.setValue(self.configs['MAXIMUM_YEAR'])
        self.year_to_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.year_to_slider.setTickInterval(30)
        self.year_to_slider.valueChanged.connect(self.to_slider_change)

        self.filter_button = QPushButton('Отфильтровать')
        self.filter_button.clicked.connect(self.filter_movies)

        self.search_bar = QTextEdit()
        self.search_bar.setPlaceholderText('Введите название фильма здесь...')
        self.search_bar.setMinimumWidth(350)
        self.search_bar.textChanged.connect(self.search_text_change)

        layout = QVBoxLayout()

        layout.addWidget(self.search_bar)

        layout.addWidget(self.country_label)
        layout.addWidget(self.country_cb)

        layout.addWidget(self.year_from_label)
        layout.addWidget(self.year_from_slider)

        layout.addWidget(self.year_to_label)
        layout.addWidget(self.year_to_slider)

        layout.addWidget(self.filter_button)

        layout.addStretch(1)
        self.topLeftGroupBox.setLayout(layout)

    def sort_parameter_change(self, element_index):
        parameter = self.sort_cb.itemText(element_index)
        index_parameter = {
            'Номер в топ-250': 0,
            'Название фильма': 1,
            'Страна': 3,
            'Рейтинг': 4,
            'Год': 2
        }
        sort_type = Qt.SortOrder.DescendingOrder if self.sort_flag.checkState() == Qt.CheckState.Checked else\
            Qt.SortOrder.AscendingOrder

        self.movies_model.setSort(index_parameter[parameter], sort_type)
        self.movies_model.select()

        self.tableWidget.setRowCount(0)

        self.tableWidget.setRowCount(self.movies_model.rowCount())
        for i in range(self.movies_model.rowCount()):
            columns = ['id', 'movie', 'country_id', 'rating_ball']
            for j in range(len(columns)):
                value = self.movies_model.record(i).value(columns[j])
                if columns[j] == 'country_id':
                    self.query.exec(f'SELECT id, name FROM countries where id={value}')
                    self.query.first()
                    value = self.query.value(1)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
            movie_id = self.movies_model.record(i).value('id')
            poster_pixmap = QPixmap(f'{self.configs["POSTERS_PATH"]}poster_{movie_id}.jpg')
            self.tableWidget.setImage(i, len(columns), poster_pixmap, 130, 180)


    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox('Сортировка фильмов')


        self.sort_cb = QComboBox()
        self.sort_cb.addItems(['Номер в топ-250',
                         'Название фильма',
                         'Страна',
                         'Рейтинг',
                         'Год']
        )
        self.sort_cb.currentIndexChanged.connect(self.sort_parameter_change)

        self.sort_flag = QCheckBox()
        self.sort_flag.setText('По убыванию')
        self.sort_flag.stateChanged.connect(self.sort_parameter_change)

        layout = QVBoxLayout()
        layout.addWidget(self.sort_cb)
        layout.addWidget(self.sort_flag)

        layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)

    def show_movie_details(self, item):
        self.details_window.set_window_to_center()
        self.details_window.show()
        current_row = item.row()
        print(current_row)
        index = self.tableWidget.model().index(current_row, 0)
        movie_id = self.tableWidget.model().data(index)
        self.query.exec(f'SELECT movie, overview, year FROM movies where id={movie_id}')
        self.query.first()
        movie_name = self.query.value(0)
        movie_descr = self.query.value(1)
        movie_year = self.query.value(2)

        self.details_window.movie_title.setText(movie_name)
        self.details_window.movie_year.setText(str(movie_year))
        self.details_window.movie_description.setText("<center>" \
           f"<img src=./static/poster_images/poster_{movie_id}.jpg>" \
           "</center>" \
           f"<p>{movie_descr}<br/>")


    def createBottomTabWidget(self):
        self.bottomTabWidget = QTabWidget()

        tab1 = QWidget()

        self.movies_model = QSqlTableModel(None, self.db)
        self.movies_model.setTable("movies")
        self.movies_model.select()

        self.tableWidget = TableWidget(self.movies_model.rowCount(), 5)

        self.tableWidget.verticalHeader().setDefaultSectionSize(150)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidget.verticalHeader().setVisible(False)

        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem('Номер в топ-250'))
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem('Название фильма'))
        self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem('Страна'))
        self.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem('Рейтинг'))
        self.tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem('Постер'))

        for i in range(self.movies_model.rowCount()):
            columns = ['id', 'movie', 'country_id', 'rating_ball']
            for j in range(len(columns)):
                value = self.movies_model.record(i).value(columns[j])
                if columns[j] == 'country_id':
                    self.query.exec(f'SELECT id, name FROM countries where id={value}')
                    self.query.first()
                    value = self.query.value(1)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
            movie_id = self.movies_model.record(i).value('id')
            poster_pixmap = QPixmap(f'{self.configs["POSTERS_PATH"]}poster_{movie_id}.jpg')
            self.tableWidget.setImage(i, len(columns), poster_pixmap, 130, 180)

        self.details_window = DetailsWindow(self)

        self.tableWidget.itemDoubleClicked.connect(self.show_movie_details)
        self.tableWidget.show()

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(self.tableWidget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        textEdit = QTextEdit()

        textEdit.setPlainText("В этом сервисе\n"
                              "вы можете получить\n" 
                              "детальную информацию о\n"
                              "фильмах и\n"
                              "найти похожие по описанию фильмы!\n")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(textEdit)
        tab2.setLayout(tab2hbox)

        self.bottomTabWidget.addTab(tab1, "&Фильмы")
        self.bottomTabWidget.addTab(tab2, "&Информация")

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 1000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(10)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    gallery = AppWindow()
    gallery.show()
    sys.exit(app.exec())
