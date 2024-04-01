from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db import db

def empty_temporary_images(user_id):
    try:
        sql = """
                DELETE FROM
                  temp_images
                WHERE
                  user_id = :user_id
              """
        db.session.execute(text(sql), {"user_id":user_id})
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def add_temporary_image(user_id, imagename, imagedata):
    try:
        sql = """
                INSERT INTO
                  temp_images(user_id, imagename, imagedata)
                VALUES
                  (:user_id, :name, :data)
              """
        db.session.execute(text(sql), {"user_id":user_id, "name":imagename, "data":imagedata})
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def get_temporary_images(user_id):
    sql = """
            SELECT
              imagename, imagedata
            FROM
              temp_images
            WHERE
              user_id = :user_id
          """
    result = db.session.execute(text(sql), {"user_id":user_id})
    return result.fetchall()
