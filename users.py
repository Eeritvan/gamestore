from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text

def login(username, password):
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(text(sql), {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            return True
        else:
            return False

def logout():
    del session["user_id"]

def register(username, password):
    hash = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password) VALUES (:username,:password)"
        db.session.execute(text(sql), {"username":username, "password":hash})
        db.session.commit()
    except:
        return False
    return login(username, password)

def user_id():
    return session.get("user_id",0)