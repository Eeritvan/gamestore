from os import getenv
from flask_sqlalchemy import SQLAlchemy
from app import app

URL = getenv("DATABASE_URL")

app.config["SQLALCHEMY_DATABASE_URI"] = URL

db = SQLAlchemy(app)
