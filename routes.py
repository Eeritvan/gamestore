from app import app
from flask import redirect, render_template, request
from datetime import datetime
from werkzeug.utils import secure_filename
from base64 import b64encode, b64decode
from random import shuffle
import users
import balance
import games
import images
import validation
import reviews
import library
import wishlist
import cart
import history

@app.route("/")
def frontpage():
    return render_template("frontpage.html", credits=balance.get_balance(users.user_id()),
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
            # todo error: password mismatch
            return render_template("register.html")
        if users.register(username, password1):
            return redirect("/")
        else:
            # todo error: username already in use
            return render_template("register.html")

@app.route("/balance", methods=["GET", "POST"])
def balance_page():
    user_id = users.user_id()
    if request.method == "GET":
        return render_template("balance.html", balance = balance.get_balance(user_id))
    if request.method == "POST":
        amount = request.form.get("button")
        if amount == "own_value":
            amount = request.form.get("amount")
        amount = amount.split(".")[0]

        if balance.update_balance(user_id, amount): # todo: success message
            return redirect("/")
        else: # todo error: adding balance failed
            return redirect("/")

@app.route("/library", methods=["GET"])
def getlibrary():
    ownedgames = library.get_library(users.user_id())
    return render_template("library.html", ownedgames = ownedgames)

@app.route("/wishlist", methods=["GET", "POST"])
def getwishlist():
    user_id = users.user_id()
    if request.method == "POST":
        game_id = request.form["game_id"]
        if request.form["remove"] == "remove":
            wishlist.remove_from_wishlist(user_id, game_id)
        else:
            date = datetime.now().strftime("%Y-%m-%d")
            if wishlist.already_in_wishlist(user_id, game_id) != None:
                return redirect("/wishlist") # todo error: game already in wishlist
            elif not wishlist.add_to_wishlist(user_id, game_id, date):
                return redirect("/wishlist") # todo error: adding to wishlist failed

    wishlistgames = wishlist.get_wishlist(user_id)
    return render_template("wishlist.html", wishlistgames = wishlistgames)

@app.route("/cart", methods=["GET", "POST"])
def getcart():
    user_id = users.user_id()
    if request.method == "POST":
        game_id = request.form["game_id"]
        if request.form["remove"] == "remove":
            cart.remove_from_cart(user_id, game_id)
        else:
            if cart.game_in_cart(user_id, game_id) != None:
                return redirect("/cart") # todo error: game already in cart
            elif not cart.add_to_cart(user_id, game_id):
                return redirect("/cart") # todo error: adding to cart failed

    cartgames = cart.get_cart(user_id)
    total = cart.get_cart_total(user_id)
    userbalance = balance.get_balance(user_id)
    enough_balance = False
    try:
        if total <= userbalance:
            enough_balance = True
    except:
        pass
    return render_template("cart.html", cartgames = cartgames, total = total, balance = userbalance, enough_balance = enough_balance)

@app.route("/cart/checkout", methods=["POST"])
def checkout():
    user_id = users.user_id()

    for game in cart.get_cart(user_id):
        price = float(game[1])
        game_id = game[2]
        date = datetime.now().strftime("%Y-%m-%d")

        library.add_to_library(user_id, game_id)
        cart.remove_from_cart(user_id, game_id)
        balance.update_balance(user_id, -price)
        wishlist.remove_from_wishlist(user_id, game_id)
        history.add_game_to_history(user_id, game_id, date, price)

    return redirect("/")

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
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        date = request.form["release_date"]
        time = request.form["time"]
        price = validation.fix_price(request.form["euros"], request.form["cents"])
            
        global imagelist
        imagelist = []
        images = request.files.getlist("image")
        for image in images:
            imagename = secure_filename(image.filename)
            imagedata = b64encode(image.read()).decode("utf-8")
            if validation.validate_imagesize(b64decode(imagedata)) == False: # todo error: image too large
                return redirect("/")
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
def publish():
    try:
        title, description, price, date, time = validation.validate_gameinfo(request.form["title"],
                                                                         request.form["description"],
                                                                         request.form["price"],
                                                                         request.form["date"],
                                                                         request.form["time"])
    except: # todo error: invalid input
        return redirect("/")
    if games.add_newgame(title, description, price, date, time):
        if len(imagelist) > 0:
            game_id = games.get_game_id(title)
            for image in imagelist:
                images.add_gameimage(game_id, image[0], b64decode(image[1]))
        return redirect("/") # success message: game added successfully / redirect to the game's page
    else:
        return redirect("/") # todo error: adding game failed

@app.route("/game/<int:id>", methods=["GET", "POST"])
def game(id):
    user_id = users.user_id()
    game = games.get_game(id)
    if game == None: # todo error: game not found
        return redirect("/")
    
    if request.method == "GET":
        
        imagelist = []
        for image in images.get_gameimages(id):
            imagename = secure_filename(image[0])
            imagedata = b64encode(image[1]).decode("utf-8")
            imagelist.append((imagename, imagedata))
        
        allreviews = reviews.show_reviews(id)
        shuffle(allreviews)
        your_review = reviews.already_reviewed(user_id, id)
        if your_review != None:
            allreviews.remove(your_review)
        owned = library.already_in_library(user_id, id)

        return render_template("game.html", game_id = id,
                                            title = game[0],
                                            description = game[1],
                                            price = game[2],
                                            release_date = game[3],
                                            creator = game[4],
                                            imagelist = imagelist,
                                            reviews = allreviews,
                                            your_review = your_review,
                                            owned = owned)
    if request.method == "POST":
        game_id = id
        date = datetime.now().strftime("%Y-%m-%d")
        rating = request.form["rating"]
        review = request.form["review"]

        if request.form["edited"] == "False":
            reviews.add_review(user_id, game_id, date, rating, review)
        if request.form["edited"] == "True":
            reviews.edit_review(user_id, game_id, date, rating, review)
        
        return redirect(str(id))