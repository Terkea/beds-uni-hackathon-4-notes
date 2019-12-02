from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# DATABASE CREDENTIALS
ENGINE = 'mysql'
USERNAME = 'test'
PASSWORD = 'testtest'
HOST = 'localhost'
PORT = '3306'
DATABASE = 'notes'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    ENGINE + "://" + USERNAME + ":" + \
    PASSWORD + "@" + HOST + ":" + \
    PORT + "/" + DATABASE

app.config['SECRET_KEY'] = 'SUPER_MEGA_SECURE_KEY'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from api import models
from api.endpoints import user
from api.endpoints import category
from api.endpoints import note
from api.endpoints.stand_alone_views import Login
from api.endpoints.stand_alone_views import Notes_by_Category
