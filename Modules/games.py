import math
from sqlalchemy import text
from db import db

def add_newgame(title, description, price, date, time, creator):
    try:
        sql = """
                INSERT INTO
                  games(title, description, price, release_date, release_time, creator_id)
                VALUES
                  (:title, :description, :price, :release_date, :release_time, :creator_id)
                RETURNING id
              """
        result = db.session.execute(text(sql), {"title":title, "description":description,
                                                "price":price, "release_date":date,
                                                "release_time":time, "creator_id":creator})
        db.session.commit()
        return result.fetchone()[0]
    except:
        return False

def get_game(game_id):
    sql = """
            SELECT
              G.title, G.description, G.price, G.release_date, G.release_time, COALESCE(U.username, 'None') AS username, U.id, G.discount
            FROM
              games G
            LEFT JOIN users U ON G.creator_id = U.id
            WHERE
              G.id = :id
          """
    result = db.session.execute(text(sql), {"id":game_id})
    return result.fetchone()

def search_games(query=None, categorylist=None, selectedsort = None):
    sql = """
            SELECT
              G.title, G.description, G.price, G.release_date, COALESCE(U.username, 'None') AS username,
              G.id, -ROUND((1-G.discount)*100) as percentage, ROUND(FLOOR(G.price * G.discount * 100) / 100, 2) AS discountprice
            FROM
              games G
            LEFT JOIN users U ON G.creator_id = U.id
            WHERE True
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
    if selectedsort:
        values = {"random":"RANDOM()",
                  "name":"LOWER(G.title)",
                  "release":"G.release_date",
                  "price":"discountprice"}
        sql += f" ORDER BY {values[selectedsort]}"

    result = db.session.execute(text(sql), parameters).fetchall()
    return result

def update_game(game_id, title, description, price, date, time):
    try:
        sql = """
              UPDATE 
                games
              SET
                title=:title, description=:description, price=:price, release_date=:date, release_time=:time
              WHERE
                id=:gameid
             """
        db.session.execute(text(sql), {"title":title,
                                       "description":description,
                                       "price":price,
                                       "date":date,
                                       "time":time,
                                       "gameid":game_id})
        db.session.commit()
        return True
    except:
        return False

def update_game_discount(game_id, discount):
    try:
        sql = "UPDATE games SET discount=:discount WHERE id=:gameid"
        db.session.execute(text(sql), {"gameid":game_id, "discount":discount})
        db.session.commit()
        return True
    except:
        return False

def get_price(game_id):
    sql = "SELECT price, discount FROM games WHERE id=:gameid"
    result = db.session.execute(text(sql), {"gameid":game_id}).fetchone()
    if result[1] != 1.0:
        percentage = -int((1-result[1])*100)
        sale_price = math.floor(result[0] * result[1] * 100) / 100
        sale_price = "{:.2f}".format(sale_price)
        return (result[0], f"{percentage}%", f"{sale_price}€")
    return (result[0], "False", "False")

def del_game(game_id):
    try:
        gamename = get_game(game_id)[0]

        for table in ["library", "history"]:
            sql = f"UPDATE {table} SET deleted_title=:name WHERE game_id=:id"
            db.session.execute(text(sql), {"name":gamename, "id":game_id})

        sql = "DELETE FROM games WHERE id=:gameid"
        db.session.execute(text(sql), {"gameid":game_id})
        db.session.commit()
        return True
    except:
        return False

def games_by_creator(user_id):
    sql = """
            SELECT 
              G.id, G.title
            FROM
              games G, users U
            WHERE
              G.creator_id = U.id AND U.id =:userid
          """
    result = db.session.execute(text(sql), {"userid":user_id})
    return result.fetchall()
