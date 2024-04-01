from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db import db

def get_categoryid(categoryname):
    sql = "SELECT id FROM categories WHERE category = :name"
    result = db.session.execute(text(sql), {"name":categoryname})
    return result.fetchone()[0]

def add_game_to_category(game_id, categoryid):
    try:
        sql = "INSERT INTO game_categories (game_id, category_id) VALUES (:gameid, :categoryid)"
        db.session.execute(text(sql), {"gameid":game_id, "categoryid":categoryid})
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def get_categories(game_id = None):
    sql = "SELECT DISTINCT C.id, C.category FROM categories C"
    parameters = {}
    if game_id:
        sql += ", game_categories G WHERE G.category_id = C.id AND G.game_id = :gameid"
        parameters["gameid"] = game_id
    sql += " ORDER BY C.category"
    result = db.session.execute(text(sql), parameters)
    return result.fetchall()

def del_gamecategories(game_id):
    try:
        sql = "DELETE FROM game_categories WHERE game_id=:game_id"
        db.session.execute(text(sql), {"game_id":game_id})
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False
