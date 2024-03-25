from db import db
from sqlalchemy import text
import users

def add_initialbalance(username, amount): # todo: possible error???
    sql = "SELECT id FROM users WHERE username=:username"
    id  = db.session.execute(text(sql), {"username":username}).fetchone()[0]
    sql = "INSERT INTO balance (user_id, amount) VALUES (:user_id, :amount)"
    db.session.execute(text(sql), {"user_id":id, "amount":amount})
    db.session.commit()

def update_balance(amount):
    try:
        sql = "UPDATE balance SET amount = amount + :amount WHERE user_id=:id"
        db.session.execute(text(sql), {"amount":amount, "id":users.user_id()})
        db.session.commit()
        return True
    except:
        return False

def get_balance():
    if users.user_id() != 0:
        sql = "SELECT amount FROM balance WHERE user_id=:id"
        result = db.session.execute(text(sql), {"id":users.user_id()})
        return result.fetchone()[0]