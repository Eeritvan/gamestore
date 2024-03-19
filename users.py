from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text
import balance

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
    balance.add_initialbalance(username, 0.0)
    return login(username, password)

def user_id():
    return session.get("user_id", 0)

def get_username():
    if user_id() != 0:
        sql = "SELECT username FROM users WHERE id=:id"
        return db.session.execute(text(sql), {"id":user_id()}).fetchone()[0]

def is_seller():
    if user_id() != 0:
        sql = "SELECT R.role FROM users U , roles R WHERE U.id=:id AND U.role=R.id"
        user_role = db.session.execute(text(sql), {"id":user_id()}).fetchone()[0]
        return user_role == "seller"

def is_moderator():
    if user_id() != 0:
        sql = "SELECT R.role FROM users U , roles R WHERE U.id=:id AND U.role=R.id"
        user_role = db.session.execute(text(sql), {"id":user_id()}).fetchone()[0]
        return user_role == "moderator"