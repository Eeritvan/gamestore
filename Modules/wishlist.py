from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db import db

def add_to_wishlist(user_id, game_id, date):
    try:
        sql = "INSERT INTO wishlist (user_id, date, game_id) VALUES (:user_id, :date, :game_id)"
        db.session.execute(text(sql), {"user_id":user_id, "date":date, "game_id":game_id})
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def remove_from_wishlist(user_id, game_id):
    try:
        sql = "DELETE FROM wishlist WHERE user_id=:user_id and game_id=:game_id"
        db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def get_wishlist(user_id, onsale = None, query = None):
    sql = """SELECT
               G.title, G.id, W.date, G.price, -ROUND((1-G.discount)*100) as percentage,
               ROUND(FLOOR(G.price * G.discount * 100) / 100, 2) AS discountprice
             FROM 
               games G, wishlist W 
             WHERE
               W.user_id=:user_id AND W.game_id=G.id
          """
    parameters = {"user_id":user_id}
    if onsale:
        sql += " AND G.discount != 1.0"
    if query:
        sql += " AND (LOWER(G.title) LIKE LOWER(:query))"
        parameters["query"] = f"%{query}%"
    result = db.session.execute(text(sql), parameters)
    return result.fetchall()

def already_in_wishlist(user_id, game_id):
    sql = "SELECT game_id FROM wishlist WHERE user_id=:user_id AND game_id=:game_id"
    result = db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    return result.fetchone() is not None
