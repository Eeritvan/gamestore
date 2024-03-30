from db import db
import os
from flask import session
from random import choice
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import text
from Modules import balance, validation

def login(username, password):
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(text(sql), {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            return True
        else:
            return False

def logout():
    del session["user_id"]

def register(username, password):
    hash = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password) VALUES (:username,:password) RETURNING id"
        id = db.session.execute(text(sql), {"username":username, "password":hash}).fetchone()[0]
        db.session.commit()
    except:
        return False
    balance.add_initialbalance(id, 0.00)
    link_profile(id)

    return login(username, password)

def user_id():
    return session.get("user_id", 0)

def get_username():
    if user_id() != 0:
        sql = "SELECT username FROM users WHERE id=:id"
        return db.session.execute(text(sql), {"id":user_id()}).fetchone()[0]

def get_userid(username):
    sql = "SELECT id FROM users WHERE username=:username"
    return db.session.execute(text(sql), {"username":username}).fetchone()[0]

def is_creator():
    if user_id() != 0:
        sql = "SELECT R.role FROM users U , roles R WHERE U.id=:id AND U.role=R.id"
        user_role = db.session.execute(text(sql), {"id":user_id()}).fetchone()[0]
        return user_role == "creator"

def is_moderator():
    if user_id() != 0:
        sql = "SELECT R.role FROM users U , roles R WHERE U.id=:id AND U.role=R.id"
        user_role = db.session.execute(text(sql), {"id":user_id()}).fetchone()[0]
        return user_role == "moderator"
    
def link_profile(userid):
    randomname = choice(os.listdir("static/default_profilepic/"))
    image_path = (os.path.join("static/default_profilepic/", randomname))
    with open(image_path, 'rb') as f:
        image_data = f.read()
    sql = "INSERT INTO profile_picture(picturename, picturedata) VALUES (:picturename, :picturedata) RETURNING id"
    id = db.session.execute(text(sql), {"picturename":randomname, "picturedata":image_data}).fetchone()[0]
    sql = "INSERT INTO profile(user_id, picture_id) VALUES (:userid, :id)"
    db.session.execute(text(sql), {"userid":userid, "id":id})
    db.session.commit()

def get_profile(userid):
    sql = """
            SELECT
              U.username, P.bio, U.joined, R.role, P.visible, U.id, P.picture_id
            FROM
              users U, profile P, roles R
            WHERE
              U.id=:id AND P.user_id = U.id AND R.id = U.role
          """ 
    result =  db.session.execute(text(sql), {"id":userid}).fetchall()
    return result

def update_profile(userid, username, bio, visibility, image = None):
    visibility = True if visibility == "public" else False
    try:
        if image:
            name = secure_filename(image.filename)
            data = image.read()
            if not validation.validate_profilepic(data):
                return False
            sql = "SELECT picture_id FROM profile WHERE user_id =:userid"
            id = db.session.execute(text(sql), {"userid":userid}).fetchone()[0]
            sql = "UPDATE profile_picture SET picturename=:picturename, picturedata=:picturedata WHERE id=:id"
            db.session.execute(text(sql), {"id":id, "picturename":name, "picturedata":data})
        sql = "UPDATE users SET username=:username WHERE id =:userid"
        db.session.execute(text(sql), {"userid":userid, "username":username})
        sql = "UPDATE profile SET bio=:bio, visible=:visible WHERE user_id =:userid"
        db.session.execute(text(sql), {"userid":userid, "bio":bio, "visible":visibility})
        db.session.commit()
        return True
    except:
        return False
    
def del_user(userid):
    try:
        id = get_profile(userid)[0][6]
        sql = "DELETE FROM profile_picture WHERE id=:id"
        db.session.execute(text(sql), {"id":id})
        sql = "DELETE FROM users WHERE id=:id"
        db.session.execute(text(sql), {"id":userid})
        db.session.commit()
        logout()
        return True
    except:
        return False