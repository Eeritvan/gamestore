from db import db
from sqlalchemy import text

def add_to_cart(user_id, game_id):
    try:
        sql = "INSERT INTO cart (user_id, game_id) VALUES (:user_id, :game_id)"
        db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
        db.session.commit()
        return True
    except:
        return False

def get_cart(user_id):
    sql = """SELECT
               G.title, G.price, G.id, -ROUND((1-G.discount)*100) as percentage, ROUND(FLOOR(G.price * G.discount * 100) / 100, 2) AS discountprice
             FROM
               games G, cart C 
             WHERE
               C.user_id=:user_id AND C.game_id=G.id
          """
    result = db.session.execute(text(sql), {"user_id":user_id})
    return result.fetchall()

def get_cart_total(user_id):
    sql = "SELECT SUM(ROUND(FLOOR(G.price * G.discount * 100) / 100, 2)) FROM games G, cart C WHERE C.user_id=:user_id AND C.game_id=G.id"
    result = db.session.execute(text(sql), {"user_id":user_id})
    return result.fetchone()[0]

def game_in_cart(user_id, game_id):
    sql = "SELECT game_id FROM cart WHERE user_id=:user_id AND game_id=:game_id"
    result = db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    return result.fetchone() != None

def remove_from_cart(user_id, game_id): # todo error: database failure
    sql = "DELETE FROM cart WHERE user_id=:user_id and game_id=:game_id"
    db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    db.session.commit()