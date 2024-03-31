from sqlalchemy import text
from db import db

def add_game_to_history(user_id, game_id, date, price): # todo error: database failure
    sql = """INSERT INTO history (user_id, game_id, date, sum)
             VALUES (:user_id, :game_id, :date, :price)"""
    db.session.execute(text(sql), {"user_id":user_id,
                                   "game_id":game_id,
                                   "date":date,
                                   "price":(-price)})
    db.session.commit()

def add_balance_to_history(user_id, date, amount): # todo error: database failure
    sql = "INSERT INTO history (user_id, date, sum) VALUES (:user_id, :date, :sum)"
    db.session.execute(text(sql), {"user_id":user_id, "date":date, "sum":amount})
    db.session.commit()

def get_history(user_id):
    sql = """
            SELECT
              H.date, COALESCE(G.title, H.deleted_title) as title, ROUND(H.sum, 2) as sum
            FROM
              history H
            LEFT JOIN
              games G ON H.game_id = G.id
            WHERE
              H.user_id = :user_id
            ORDER BY 
              H.id
          """
    result =  db.session.execute(text(sql), {"user_id":user_id,})
    return result.fetchall()
