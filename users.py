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
    balance.add_initialbalance(username, 0.00)
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
    
def add_to_cart(user_id, game_id):
    try:
        sql = "INSERT INTO cart (user_id, game_id) VALUES (:user_id, :game_id)"
        db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
        db.session.commit()
        return True
    except:
        return False

def get_cart(user_id):
    sql = "SELECT G.title, G.price, G.id FROM games G, cart C WHERE C.user_id=:user_id AND C.game_id=G.id"
    result = db.session.execute(text(sql), {"user_id":user_id})
    return result.fetchall()

def get_cart_total(user_id):
    sql = "SELECT SUM(G.price) FROM games G, cart C WHERE C.user_id=:user_id AND C.game_id=G.id"
    result = db.session.execute(text(sql), {"user_id":user_id})
    return result.fetchone()[0]

def game_in_cart(user_id, game_id):
    sql = "SELECT game_id FROM cart WHERE user_id=:user_id AND game_id=:game_id"
    result = db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    return result.fetchone()

def remove_from_cart(user_id, game_id): # todo error: database failure
    sql = "DELETE FROM cart WHERE user_id=:user_id and game_id=:game_id"
    db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    db.session.commit()

def add_to_library(user_id, game_id): # todo error: database failure
    sql = "INSERT INTO library (user_id, game_id) VALUES (:user_id, :game_id)"
    db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    db.session.commit()

def get_library(user_id):
    sql = "SELECT G.title, G.id FROM games G, library L WHERE L.user_id=:user_id AND L.game_id=G.id"
    result = db.session.execute(text(sql), {"user_id":user_id})
    return result.fetchall()

def already_in_library(user_id, game_id):
    sql = "SELECT game_id FROM library WHERE user_id=:user_id AND game_id=:game_id"
    result = db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    return result.fetchone() != None

def add_to_wishlist(user_id, game_id, date):
    try:  
        sql = "INSERT INTO wishlist (user_id, date, game_id) VALUES (:user_id, :date, :game_id)"
        db.session.execute(text(sql), {"user_id":user_id, "date":date, "game_id":game_id})
        db.session.commit()
        return True
    except:
        return False

def remove_from_wishlist(user_id, game_id):
    sql = "DELETE FROM wishlist WHERE user_id=:user_id and game_id=:game_id"
    db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    db.session.commit()

def get_wishlist(user_id):
    sql = "SELECT G.title, G.id, W.date FROM games G, wishlist W WHERE W.user_id=:user_id AND W.game_id=G.id"
    result = db.session.execute(text(sql), {"user_id":user_id})
    return result.fetchall()

def already_in_wishlist(user_id, game_id):
    sql = "SELECT game_id FROM wishlist WHERE user_id=:user_id AND game_id=:game_id"
    result = db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    return result.fetchone()