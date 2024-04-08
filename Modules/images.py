from base64 import b64encode, b64decode
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from Modules import validation, temporaryimages, users
from db import db

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
    except SQLAlchemyError:
        db.session.rollback()
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
    if isinstance(images[0], str):
        for i in images:
            selected = get_gameimages(None, i)
            imagename = secure_filename(selected[0][1])
            imagedata = b64encode(selected[0][2]).decode("utf-8")
            if validation.validate_imagesize(b64decode(imagedata)) is False:
                return False
            imagelist.append((imagename, imagedata))
            if not temporaryimages.add_temporary_image(users.user_id(), imagename, b64decode(imagedata)):
                return False
    else:
        for i in images:
            imagename = secure_filename(i.filename)
            imagedata = b64encode(i.read()).decode("utf-8")
            if validation.validate_imagesize(b64decode(imagedata)) is False:
                return False
            imagelist.append((imagename, imagedata))
            if not temporaryimages.add_temporary_image(users.user_id(), imagename, b64decode(imagedata)):
                return False
    return imagelist

def load_images_to_display(game_id):
    imagelist = []
    for image in get_gameimages(game_id):
        image_id = image[0]
        image_name = secure_filename(image[1])
        image_data = b64encode(image[2]).decode("utf-8")
        if image_data != "":
            imagelist.append((image_id, image_name, image_data))
    return imagelist

def del_images(game_id):
    try:
        sql = "DELETE FROM images WHERE game_id=:game_id"
        db.session.execute(text(sql), {"game_id":game_id})
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def get_profilepic(image_id, user_id = None):
    if image_id:
        sql = "SELECT picturename, picturedata FROM profile_picture WHERE id=:imageid"
        result = db.session.execute(text(sql), {"imageid":image_id}).fetchall()[0]
    else:
        if user_id == 0:
            return None, None
        sql = """
                SELECT 
                  picturename, picturedata
                FROM
                  profile_picture P, profile Pro
                WHERE
                  Pro.user_id=:user_id
              """
        result = db.session.execute(text(sql), {"user_id":user_id}).fetchall()[0]
    return (result[0], b64encode(result[1]).decode("utf-8"))

def encode_reviewpictures(allreviews):
    encoded_reviews = []
    for review in allreviews:
        review_list = list(review)
        image_data = review_list[-1]
        encoded_image = b64encode(image_data).decode('utf-8')
        review_list[-1] = encoded_image
        encoded_reviews.append(review_list)
    return encoded_reviews

def encode_image(image):
    return b64encode(image).decode('utf-8')
