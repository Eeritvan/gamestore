from db import db
from sqlalchemy import text

def add_newgame(title, description, price, date, time, creator):
    try:
        sql = """
                INSERT INTO
                  games(title, description, price, release_date, release_time, creator_id)
                VALUES
                  (:title, :description, :price, :release_date, :release_time, :creator_id)
                RETURNING id
              """
        result = db.session.execute(text(sql), {"title":title, "description":description, "price":price, "release_date":date, "release_time":time, "creator_id":creator})
        db.session.commit()
        return result.fetchone()[0]
    except:
        return False

def get_game(id):
    sql = """
            SELECT
              G.title, G.description, G.price, G.release_date, G.release_time, U.username, U.id
            FROM
              games G, users U
            WHERE
              G.id=:id AND G.creator_id=U.id
          """
    result = db.session.execute(text(sql), {"id":id})
    return result.fetchone()

def search_games(query=None, categorylist=None):
  sql = """
    SELECT DISTINCT
      G.title, G.description, G.price, G.release_date, U.username, G.id
    FROM
      games G, users U
    WHERE 
      G.creator_id=U.id
  """
  parameters = {}
  if query:
    sql += " AND (LOWER(G.title) LIKE LOWER(:query))"
    parameters["query"] = f"%{query}%"
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
    parameters["categorylist"] = tuple(categorylist)
    parameters["category_count"] = len(categorylist)

  result = db.session.execute(text(sql), parameters)
  return result.fetchall()

def update_game(gameid, title, description, price, date, time):
    try:
        sql = """
              UPDATE 
                games
              SET
                title=:title, description=:description, price=:price, release_date=:date, release_time=:time
              WHERE
                id=:gameid
             """
        db.session.execute(text(sql), {"title":title, "description":description, "price":price, "date":date, "time":time, "gameid":gameid})
        db.session.commit()
        return True
    except:
        return False