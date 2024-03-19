from app import app
from flask import redirect, render_template, request
import users
import balance

@app.route("/")
def frontpage():
    return render_template("frontpage.html", credits=balance.get_balance(),
                                             user = users.get_username(),
                                             user_id = users.user_id(),
                                             seller = users.is_seller(),
                                             moderator = users.is_moderator())
    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        return render_template("login.html")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("register.html")
        if users.register(username, password1):
            return redirect("/")
        else:
            return render_template("register.html")

@app.route("/ratings", methods=["GET"])
def ratings(): # todo
    pass

@app.route("/library", methods=["GET"])
def library(): # todo
    pass

@app.route("/wishlist", methods=["GET"])
def wishlist(): # todo
    pass

@app.route("/cart", methods=["GET"])
def cart(): # todo
    pass

@app.route("/allgames", methods=["GET"])
def allgames(): # todo
    pass