from db import db
from sqlalchemy import text

def get_all_categories():
    sql = "SELECT id, category FROM categories"
    result = db.session.execute(text(sql))
    return result.fetchall()

def get_categoryid(categoryname):
    sql = "SELECT id FROM categories WHERE category = :name"
    result = db.session.execute(text(sql), {"name":categoryname})
    return result.fetchone()

def add_game_to_category(gameid, categoryid): # todo error: database failure
    sql = "INSERT INTO game_categories (game_id, category_id) VALUES (:gameid, :categoryid)"
    db.session.execute(text(sql), {"gameid":gameid, "categoryid":categoryid})
    db.session.commit()

def get_categories_by_gameid(gameid):
    sql = """
            SELECT
              C.category
            FROM
              game_categories G, categories C
            WHERE
              G.game_id = :gameid AND G.category_id = C.id
          """
    result = db.session.execute(text(sql), {"gameid":gameid})
    return result.fetchall()