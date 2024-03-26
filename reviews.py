from db import db
from sqlalchemy import text

def add_review(user_id, game_id, date, rating, review): # todo error: database failure
    sql = """
            INSERT INTO 
              reviews (user_id, game_id, date, rating, review)
            VALUES
              (:user_id, :game_id, :date, :rating, :review)
          """
    db.session.execute(text(sql), {"user_id":user_id,
                                   "game_id":game_id,
                                   "date":date,
                                   "rating":rating,
                                   "review":review})
    db.session.commit()
 
def edit_review():
    pass

def delete_review():
    pass

def show_reviews(game_id): # todo error: database failure
    sql = """
            SELECT 
              U.username, date, rating, review
            FROM
              reviews R, users U
            WHERE
              game_id = :game_id AND R.user_id = U.id
          """
    result = db.session.execute(text(sql), {"game_id":game_id})
    return result.fetchall()

def review_ratio(): # return the ratio of positive and negative reviews
    pass

def already_reviewed(user_id, game_id): # for the store page
    sql = """
            SELECT
              user_id
            FROM
              reviews
            WHERE
              user_id = :user_id AND game_id = :game_id
          """
    result = db.session.execute(text(sql), {"user_id":user_id,
                                            "game_id":game_id})
    return result.fetchone() != None