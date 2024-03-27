from db import db
from sqlalchemy import text

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
    sql = "SELECT G.title, G.id, W.date, G.price FROM games G, wishlist W WHERE W.user_id=:user_id AND W.game_id=G.id"
    result = db.session.execute(text(sql), {"user_id":user_id})
    return result.fetchall()

def already_in_wishlist(user_id, game_id):
    sql = "SELECT game_id FROM wishlist WHERE user_id=:user_id AND game_id=:game_id"
    result = db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    return result.fetchone()