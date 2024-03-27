from db import db
from sqlalchemy import text

def add_gameimage(game_id, imagename, imagedata):
    try:
        sql = """
                INSERT INTO
                  images(game_id, imagename, imagedata)
                VALUES
                  (:game_id, :name, :data)
              """
        db.session.execute(text(sql), {"game_id":game_id, "name":imagename, "data":imagedata})
        db.session.commit()
        return True
    except:
        return False
    
def get_gameimages(game_id):
    try:
        sql = """
                SELECT
                  imagename, imagedata
                FROM
                  images
                WHERE
                  game_id = :game_id
              """
        result = db.session.execute(text(sql), {"game_id":game_id})
        return result.fetchall()
    except:
        return False