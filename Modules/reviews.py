from sqlalchemy import text
from db import db

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

def edit_review(user_id, game_id, edited, rating, review):
    sql = """
            UPDATE
              reviews
            SET 
              rating = :rating, edited = :edited, review = :review
            WHERE
              user_id = :user_id AND game_id = :game_id
          """
    db.session.execute(text(sql), {"user_id":user_id,
                                   "game_id":game_id,
                                   "edited":edited,
                                   "rating":rating,
                                   "review":review})
    db.session.commit()

def delete_review(user_id, game_id): # todo error: database failure
    sql = "DELETE FROM reviews WHERE user_id = :user_id AND game_id = :game_id"
    db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    db.session.commit()

def show_reviews(game_id): # todo error: database failure
    sql = """
            SELECT 
              U.id, U.username, date, edited, rating, review, P.picturedata
            FROM
              reviews R, users U, profile_picture P, profile Pr
            WHERE
              game_id = :game_id AND R.user_id = U.id AND Pr.user_id = U.id AND Pr.picture_id = P.id
          """
    result = db.session.execute(text(sql), {"game_id":game_id})
    return result.fetchall()

def already_reviewed(user_id, game_id): # todo error: database failure
    sql = """
            SELECT 
              U.id, U.username, date, edited, rating, review, P.picturedata
            FROM
              reviews R, users U, profile_picture P, profile Pr
            WHERE
              game_id = :game_id AND R.user_id = U.id AND R.user_id = :user_id AND Pr.user_id = U.id AND Pr.picture_id = P.id
          """
    result = db.session.execute(text(sql), {"user_id":user_id, "game_id":game_id})
    return result.fetchone()
