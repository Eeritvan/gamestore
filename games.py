from db import db
from sqlalchemy import text
import users

def add_newgame(title, description, price, date, time): # todo: add image, add genre, add timing
    try:
        sql = """
                INSERT INTO
                  games(title, description, price, release_date, release_time, creator_id)
                VALUES
                  (:title, :description, :price, :release_date, :release_time, :creator_id)
              """
        db.session.execute(text(sql), {"title":title, "description":description, "price":price, "release_date":date, "release_time":time, "creator_id":users.user_id()})
        db.session.commit()
        return True
    except:
        return False

def get_game_id(title):
    sql = """
            SELECT
              id
            FROM
              games
            WHERE
              title=:title
          """
    result = db.session.execute(text(sql), {"title":title})
    return result.fetchone()[0]

def get_game(id):
    sql = """
            SELECT
              G.title, G.description, G.price, G.release_date, U.username
            FROM
              games G, users U
            WHERE
              G.id=:id AND G.creator_id=U.id
          """
    result = db.session.execute(text(sql), {"id":id})
    return result.fetchone()

def all_games():
    sql = """
            SELECT
              G.title, G.description, G.price, G.release_date, U.username
            FROM
              games G, users U
            WHERE 
              G.creator_id=U.id
          """
    result = db.session.execute(text(sql))
    return result.fetchall()