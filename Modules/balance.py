from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db import db

def add_initialbalance(user_id, amount):
    try:
        amount = "{:.2f}".format(amount)
        sql = "INSERT INTO balance (user_id, amount) VALUES (:user_id, :amount)"
        db.session.execute(text(sql), {"user_id":user_id, "amount":amount})
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def update_balance(user_id, amount):
    try:
        sql = "UPDATE balance SET amount = amount + :amount WHERE user_id=:id"
        db.session.execute(text(sql), {"amount":amount, "id":user_id})
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def get_balance(user_id):
    if user_id != 0:
        sql = "SELECT amount FROM balance WHERE user_id=:id"
        result = db.session.execute(text(sql), {"id":user_id})
        return result.fetchone()[0]
    return
