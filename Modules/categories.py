from db import db
from sqlalchemy import text

def get_categoryid(categoryname):
    sql = "SELECT id FROM categories WHERE category = :name"
    result = db.session.execute(text(sql), {"name":categoryname})
    return result.fetchone()[0]

def add_game_to_category(gameid, categoryid): # todo error: database failure
    sql = "INSERT INTO game_categories (game_id, category_id) VALUES (:gameid, :categoryid)"
    db.session.execute(text(sql), {"gameid":gameid, "categoryid":categoryid})
    db.session.commit()

def get_categories(gameid = None):
    sql = """
            SELECT DISTINCT
              C.id, C.category
            FROM
              categories C
          """
    parameters = {}
    if gameid:
        sql += ", game_categories G WHERE G.category_id = C.id AND G.game_id = :gameid"
        parameters["gameid"] = gameid
    sql += " ORDER BY C.category"
    result = db.session.execute(text(sql), parameters)
    return result.fetchall()

def del_gamecategories(gameid): # todo erro: database failure
    sql = "DELETE FROM game_categories WHERE game_id=:game_id"
    db.session.execute(text(sql), {"game_id":gameid})
    db.session.commit()