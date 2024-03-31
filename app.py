"""
Creating app, linking to routes and getting session key
"""

from os import getenv
from flask import Flask

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

import routes
