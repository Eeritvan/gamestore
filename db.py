from os import getenv
from flask_sqlalchemy import SQLAlchemy
from app import app

URL = getenv("DATABASE_URL")

if getenv("on_fly"):
    URL = URL.replace("://", "ql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = URL

db = SQLAlchemy(app)
