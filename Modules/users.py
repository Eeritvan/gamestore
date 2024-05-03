import os
import secrets
from random import choice
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import text
from Modules import balance, validation, images
from db import db

def login(username, password):
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(text(sql), {"username":username})
    user = result.fetchone()
    if not user:
        return False
    if check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["csrf_token"] = secrets.token_hex(16)
        return True
    return False

def logout():
    del session["user_id"]
    del session["csrf_token"]

def register(username, password):
    hashvalue = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password) VALUES (:username,:password) RETURNING id"
        userid = db.session.execute(text(sql), {"username":username,
                                                 "password":hashvalue}).fetchone()[0]
        db.session.commit()
    except:
        return False
    if not balance.add_initialbalance(userid, 0.00) or not link_profile(userid):
        return False
    return login(username, password)

def user_id():
    return session.get("user_id", 0)

def get_username():
    if user_id() != 0:
        sql = "SELECT username FROM users WHERE id=:id"
        result =  db.session.execute(text(sql), {"id":user_id()})
        return result.fetchone()[0]
    return False

def is_creator():
    if user_id() != 0:
        sql = "SELECT R.role FROM users U , roles R WHERE U.id=:id AND U.role=R.id"
        user_role = db.session.execute(text(sql), {"id":user_id()}).fetchone()[0]
        return user_role == "creator"
    return False

def is_moderator():
    if user_id() != 0:
        sql = "SELECT R.role FROM users U , roles R WHERE U.id=:id AND U.role=R.id"
        user_role = db.session.execute(text(sql), {"id":user_id()}).fetchone()[0]
        return user_role == "moderator"
    return False

def link_profile(userid):
    try:
        randomname = choice(os.listdir("static/default_profilepic/"))
        image_path = os.path.join("static/default_profilepic/", randomname)
        with open(image_path, "rb") as f:
            image_data = f.read()

        sql = """INSERT INTO profile_picture(picturename, picturedata)
                 VALUES (:picturename, :picturedata) RETURNING id"""
        image_id = db.session.execute(text(sql), {"picturename":randomname,
                                                  "picturedata":image_data}).fetchone()[0]
        sql = "INSERT INTO profile(user_id, picture_id) VALUES (:userid, :id)"
        db.session.execute(text(sql), {"userid":userid, "id":image_id})
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def get_profile(userid):
    try:
        sql = """
                SELECT
                  U.username, P.bio, U.joined, R.role, P.visible, U.id, P.picture_id
                FROM
                  users U, profile P, roles R
                WHERE
                  U.id=:id AND P.user_id = U.id AND R.id = U.role
              """
        result =  db.session.execute(text(sql), {"id":userid})
        return result.fetchall()[0]
    except:
        return False

def update_profile(userid, username, bio, visibility, role, image = None):
    visibility = True if visibility == "public" else False
    try:
        if image:
            imagename = secure_filename(image.filename)
            imagedata = image.read()
            if not validation.validate_profilepic(imagedata):
                return False
            compressed_imagedata = images.compress_image(imagedata)

            sql = "SELECT picture_id FROM profile WHERE user_id =:userid"
            picture_id = db.session.execute(text(sql), {"userid":userid}).fetchone()[0]
            sql = """
                     UPDATE profile_picture
                     SET picturename=:picturename, picturedata=:picturedata
                     WHERE id=:id
                  """
            db.session.execute(text(sql), {"id":picture_id,
                                           "picturename":imagename,
                                           "picturedata":compressed_imagedata})

        sql = "SELECT id FROM roles WHERE role=:role"
        roleid = db.session.execute(text(sql), {"role":role}).fetchone()[0]
        sql = "UPDATE users SET username=:username, role=:role WHERE id=:userid"
        db.session.execute(text(sql), {"userid":userid, "username":username, "role":roleid})
        sql = "UPDATE profile SET bio=:bio, visible=:visible WHERE user_id=:userid"
        db.session.execute(text(sql), {"userid":userid, "bio":bio, "visible":visibility})
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def del_user(userid):
    out = user_id() == userid
    try:
        picture_id = get_profile(userid)[6]
        sql = "DELETE FROM profile_picture WHERE id=:id"
        db.session.execute(text(sql), {"id":picture_id})
        sql = "DELETE FROM users WHERE id=:id"
        db.session.execute(text(sql), {"id":userid})
        db.session.commit()
        if out:
            logout()
        return True
    except:
        db.session.rollback()
        return False
