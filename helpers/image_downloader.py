from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
import urllib.request
from time import sleep
from random import randint
import json

STATIC_PATH = '../static/poster_images/'

with open('../configs.json') as data_file:
    configs = json.load(data_file)

db = QSqlDatabase.addDatabase('QSQLITE')
db.setDatabaseName(configs['database_path'])
db.open()
print(db.__str__())

model = QSqlTableModel(None, db)
model.setTable("movies")
model.select()

print(model.rowCount())

for i in range(model.rowCount()):
    poster_image_url = model.record(i).value('url_logo')
    movie_id = model.record(i).value('id')
    urllib.request.urlretrieve(poster_image_url, f"{STATIC_PATH}poster_{movie_id}.jpg")
    print(f'Постер для фильма {movie_id} выгружен!')
    sleep(randint(1, 3))
