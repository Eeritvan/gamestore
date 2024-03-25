from app import app
from flask import redirect, render_template, request, make_response
from datetime import datetime
from werkzeug.utils import secure_filename
import users
import balance
import games
import images
import base64

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
        # todo error: already logged in
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # todo error: already logged in
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            # todo: error
            return render_template("register.html")
        if users.register(username, password1):
            return redirect("/")
        else:
            # todo error: username already in use
            return render_template("register.html")

@app.route("/balance", methods=["GET", "POST"])
def balance_page():
    if request.method == "GET":
        return render_template("balance.html", balance = balance.get_balance())
    if request.method == "POST": # todo: validate amount
        amount = request.form.get("button")
        if amount == "own_value":
            amount = request.form.get("amount")
        if balance.update_balance(amount): # todo: success message
            return redirect("/")
        else: # todo: error message
            return redirect("/")

@app.route("/ratings", methods=["GET"])
def ratings(): # todo rating system
    pass

@app.route("/library", methods=["GET"])
def library(): # todo user's library
    pass

@app.route("/wishlist", methods=["GET"])
def wishlist(): # todo wishlisting games
    pass

@app.route("/cart", methods=["GET"])
def cart(): # todo shopping cart
    pass

@app.route("/allgames", methods=["GET"])
def allgames():
    return render_template("allgames.html", games = games.all_games())

@app.route("/newgame", methods=["GET", "POST"])
def newgame():
    permission = False
    if users.is_seller() or users.is_moderator():
            permission = True
    if request.method == "GET":
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        return render_template("newgame.html", permission = permission,
                                               preview = False,
                                               current_date = current_date,
                                               current_time = current_time)
    if request.method == "POST": # todo: validate given information
        title = request.form["title"]
        description = request.form["description"]
        date = request.form["release_date"]
        time = request.form["time"]

        euros = request.form["euros"] # price / broken atm
        if int(euros) == 0:
            euros = "0"
        cents = request.form["cents"]
        if len(cents) > 2:
            cents = cents[:2]
        if int(cents) == 0:
            cents = "00"
        price = str(int(euros)) + "." + str(cents)
            
        global imagelist
        imagelist = []
        images = request.files.getlist("image")
        for image in images:
            imagename = secure_filename(image.filename)
            imagedata = base64.b64encode(image.read()).decode("utf-8")
            imagelist.append((imagename, imagedata))
        
        return render_template("newgame.html", permission = permission,
                                               preview = True,
                                               title = title,
                                               description = description,
                                               price = price,
                                               date = date,
                                               time = time,
                                               imagelist = imagelist)
    
@app.route("/newgame/publish", methods=["POST"])
def publish(): # todo: validate given information
    title = request.form["title"]
    description = request.form["description"]
    price = request.form["price"]
    date = request.form["date"]
    time = request.form["time"]

    if games.add_newgame(title, description, price, date, time):
        print("game added successfully")
        if len(imagelist) > 0:
            game_id = games.get_game_id(title)
            for image in imagelist:
                images.add_gameimage(game_id, image[0], base64.b64decode(image[1]))
        return redirect("/") # todo: success message / redirect to the game's page
    else: 
        print("adding game failed")
        return redirect("/") # todo: error message

@app.route("/game/<int:id>", methods=["GET"])
def game(id):
    game = games.get_game(id)
    if game == None: # error: game not found
        return redirect("/")
    imagelist = []
    for image in images.get_gameimages(id):
        imagename = secure_filename(image[0])
        imagedata = base64.b64encode(image[1]).decode("utf-8")
        imagelist.append((imagename, imagedata))
    return render_template("game.html", title = game[0],
                                        description = game[1],
                                        price = game[2],
                                        release_date = game[3],
                                        creator = game[4],
                                        imagelist = imagelist)