from db import db
from sqlalchemy import text

def add_to_library(user_id, game_id): # todo error: database failure
    sql = "INSERT INTO library (user_id, game_id) VALUES (:user_id, :game_id)"
    db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    db.session.commit()

def get_library(user_id, query = None):
    sql = """
            SELECT
              COALESCE(G.title, L.deleted_title) as title, G.id 
            FROM
              library L 
            LEFT JOIN
              games G ON L.game_id=G.id 
            WHERE
              L.user_id=:user_id
          """
    parameters = {"user_id":user_id}
    if query:
        sql += " AND (LOWER(COALESCE(G.title, L.deleted_title)) LIKE LOWER(:query))"
        parameters["query"] = f"%{query}%"
    result = db.session.execute(text(sql), parameters)
    return result.fetchall()

def already_in_library(user_id, game_id):
    sql = "SELECT game_id FROM library WHERE user_id=:user_id AND game_id=:game_id"
    result = db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    return result.fetchone() != None