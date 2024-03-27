from db import db
from sqlalchemy import text
import Modules.users as users

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

def get_game_price(id):
    sql = """
            SELECT
              price
            FROM
              games
            WHERE
              id=:id
          """
    result = db.session.execute(text(sql), {"id":id})
    return result.fetchone()

def get_games(query=None, categorylist=None):
  sql = """
    SELECT DISTINCT
      G.title, G.description, G.price, G.release_date, U.username, G.id
    FROM
      games G, users U
    WHERE 
      G.creator_id=U.id
  """
  settings = {}
  if query:
    sql += " AND (LOWER(G.title) LIKE LOWER(:query))"
    settings["query"] = f"%{query}%"
  if categorylist:
    sql += """ AND G.id IN (
                 SELECT
                   game_id
                 FROM
                   game_categories
                 WHERE
                   category_id IN :categorylist
                 GROUP BY
                   game_id
                 HAVING
                   COUNT(DISTINCT category_id) = :category_count)
           """
    settings["categorylist"] = tuple(categorylist)
    settings["category_count"] = len(categorylist)

  result = db.session.execute(text(sql), settings)
  return result.fetchall()