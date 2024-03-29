from db import db
from sqlalchemy import text
from werkzeug.utils import secure_filename
from base64 import b64encode, b64decode
from Modules import validation, temporaryimages, users

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
    
def get_gameimages(game_id = None, imageid = None):
    try:
        sql = """
                SELECT
                  id, imagename, imagedata
                FROM
                  images
                WHERE
              """
        parameters = {}
        if game_id:
            sql += " game_id = :game_id"
            parameters["game_id"] = game_id
        elif imageid:
            sql += " id = :imageid"
            parameters["imageid"] = imageid
        result = db.session.execute(text(sql), parameters)
        return result.fetchall()
    except:
        return False
    
def load_images(images):
    imagelist = []
    if type(images[0]) == str:
        for i in images:
            selected = get_gameimages(None, i)
            imagename = secure_filename(selected[0][1])
            imagedata = b64encode(selected[0][2]).decode("utf-8")
            if validation.validate_imagesize(b64decode(imagedata)) == False: # todo error: image too large
                return False
            imagelist.append((imagename, imagedata))
            temporaryimages.add_temporary_image(users.user_id(), imagename, b64decode(imagedata))
    else:
        for i in images:
            imagename = secure_filename(i.filename)
            imagedata = b64encode(i.read()).decode("utf-8")
            if validation.validate_imagesize(b64decode(imagedata)) == False: # todo error: image too large
                return False
            imagelist.append((imagename, imagedata))
            temporaryimages.add_temporary_image(users.user_id(), imagename, b64decode(imagedata))
    return imagelist

def load_images_to_display(id):
    imagelist = []
    for image in get_gameimages(id):
        imageid = image[0]
        imagename = secure_filename(image[1])
        imagedata = b64encode(image[2]).decode("utf-8")
        if imagedata != "":
            imagelist.append((imageid, imagename, imagedata))
    return imagelist

def del_images(gameid):
    sql = "DELETE FROM images WHERE game_id=:game_id"
    db.session.execute(text(sql), {"game_id":gameid})
    db.session.commit()