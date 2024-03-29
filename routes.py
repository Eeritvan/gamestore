from app import app
from flask import redirect, render_template, request
from datetime import datetime
from random import shuffle
import Modules.users as users
import Modules.balance as balance
import Modules.games as games
import Modules.images as images
import Modules.validation as validation
import Modules.reviews as reviews
import Modules.library as library
import Modules.wishlist as wishlist
import Modules.cart as cart
import Modules.history as history
import Modules.temporaryimages as tempimages
import Modules.categories as categories

@app.route("/", methods=["GET"])
def frontpage():
    return render_template("frontpage.html", credits=balance.get_balance(users.user_id()),
                                             user = users.get_username(),
                                             user_id = users.user_id(),
                                             seller = users.is_seller(),
                                             moderator = users.is_moderator())

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET": # todo error: already logged in
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
    if request.method == "GET": # todo error: already logged in
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2: # todo error: password mismatch
            return render_template("register.html")
        if users.register(username, password1):
            return redirect("/")
        else: # todo error: username already in use
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
            history.add_balance_to_history(user_id, datetime.now().strftime("%Y-%m-%d"), amount)
            return redirect("/")
        else: # todo error: adding balance failed
            return redirect("/")

@app.route("/library", methods=["GET"])
def library_page():
    query = request.args.get("query")

    searchtext = True
    if query != None or query == "":
        searchtext = query
    ownedgames = library.get_library(users.user_id(), query)
    return render_template("library.html", ownedgames = ownedgames,
                                           searchtext = searchtext,)

@app.route("/wishlist", methods=["GET", "POST"])
def wishlist_page():
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

    query = request.args.get("query") 

    searchtext = True
    if query != None or query == "":
        searchtext = query
    wishlistgames = wishlist.get_wishlist(user_id, query)
    return render_template("wishlist.html", games = wishlistgames,
                                            searchtext = searchtext)

@app.route("/cart", methods=["GET", "POST"])
def cart_page():
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

        if price > balance.get_balance(user_id): # todo error: not enough balance
            return redirect("/cart")

        library.add_to_library(user_id, game_id)
        cart.remove_from_cart(user_id, game_id)
        balance.update_balance(user_id, -price)
        wishlist.remove_from_wishlist(user_id, game_id)
        history.add_game_to_history(user_id, game_id, date, price)

    return redirect("/")

@app.route("/allgames", methods=["GET"])
def allgames():
    query = request.args.get("query")
    categorieslist = request.args.getlist("categories")
    gamelist = games.search_games(query, categorieslist)

    searchtext = True
    if query != None or query == "":
        searchtext = query

    return render_template("allgames.html", games = gamelist,
                                            categories = categories.get_categories(),
                                            searchtext = searchtext,
                                            selectedcategories = [int(x) for x in categorieslist])

@app.route("/newgame", methods=["GET"])
def newgame():
    if not users.is_seller() and not users.is_moderator(): # todo error: no permission to create games
        return redirect("/") 
    return render_template("newgame.html", current_date = datetime.now().strftime("%Y-%m-%d"),
                                           current_time = datetime.now().strftime("%H:%M"),
                                           categories = categories.get_categories())

@app.route("/game/preview", methods=["POST"])
def preview():
    if not users.is_seller() and not users.is_moderator(): # todo error: no permission to create games
        return redirect("/") 
    
    try:
        selectedcategories = request.form.getlist("categories")
        title, description, price, date, time = validation.validate_gameinfo(request.form["title"],
                                                                             request.form["description"],
                                                                             validation.fix_price(request.form["price"]),
                                                                             request.form["date"],
                                                                             request.form["time"])
    except: # todo error: invalid input
        return redirect("/")

    edit = gameid = False
    imagelist = []
    tempimages.empty_temporary_images(users.user_id())

    if request.form["editing"] == "True":
        gameid = request.form["gameid"]
        edit = True
        selectedimages = request.form.getlist("image_ids")
        if len(selectedimages) != 0:
            imgs = images.load_images(selectedimages)
            if not imgs: # todo error: some image was too large
                return redirect("/")
            imagelist += imgs

    loadedimages = request.files.getlist("loadedimages")
    imgs = images.load_images(loadedimages)
    if not imgs: # todo error: some image was too large
        return redirect("/")
    imagelist += imgs
    
    return render_template("preview.html", gameid = gameid,
                                           title = title,
                                           description = description,
                                           price = price,
                                           date = date,
                                           time = time,
                                           imagelist = imagelist,
                                           categories = selectedcategories,
                                           edit = edit)

@app.route("/game/publish", methods=["POST"])
def publish():
    try:
        title, description, price, date, time = validation.validate_gameinfo(request.form["title"],
                                                                             request.form["description"],
                                                                             request.form["price"],
                                                                             request.form["date"],
                                                                             request.form["time"])
        gamescategories = request.form.getlist("categories")
    except: # todo error: invalid input
        return redirect("/")
    
    if request.form["edit"] == "True":
        gameid = request.form["gameid"]
        if not games.update_game(gameid, title, description, price, date, time): # todo error: something went wrong when adding games
            return redirect ("/")
        categories.del_gamecategories(gameid)
        images.del_images(gameid)
    else:
        gameid = games.add_newgame(title, description, price, date, time, users.user_id())

    imagelist = tempimages.get_temporary_images(users.user_id())
    tempimages.empty_temporary_images(users.user_id())
    if len(imagelist) > 0:
        for image in imagelist:
            if not images.add_gameimage(gameid, image[0], image[1]):
                pass # todo error: uploading image to db failed.

    for category in gamescategories:
        category_id = categories.get_categoryid(category)
        if category_id != None:
            categories.add_game_to_category(gameid, category_id)
        else: # todo error: category not found
            pass
    return redirect ("/")

@app.route("/game/<int:id>", methods=["GET", "POST"])
def game(id):
    user_id = users.user_id()
    game = games.get_game(id)
    if game == None: # todo error: game not found
        return redirect("/")
    
    if request.method == "GET":
        imagelist = images.load_images_to_display(id)
        
        allreviews = reviews.show_reviews(id)
        shuffle(allreviews)
        your_review = reviews.already_reviewed(user_id, id)
        if your_review != None:
            allreviews.remove(your_review)

        return render_template("game.html", game_id = id,
                                            title = game[0],
                                            description = game[1],
                                            price = game[2],
                                            release_date = game[3],
                                            creator = game[5],
                                            editpermission = (game[6] == user_id) or users.is_moderator(),
                                            imagelist = imagelist,
                                            reviews = allreviews,
                                            categories = categories.get_categories(id),
                                            your_review = your_review,
                                            owned = library.already_in_library(user_id, id))
    if request.method == "POST":

        date = datetime.now().strftime("%Y-%m-%d")
        rating = request.form["rating"]
        review = request.form["review"]

        if request.form["edited"] == "False":
            reviews.add_review(user_id, id, date, rating, review)
        elif request.form["edited"] == "True":
            reviews.edit_review(user_id, id, date, rating, review)
        
        return redirect(str(id))
        
@app.route("/game/<int:id>/edit", methods=["GET"])
def editgame(id):
    gameinfo = games.get_game(id)
    if not (users.is_moderator() or users.user_id() == gameinfo[6]): # todo error: not permission
        return redirect("/") 

    imagelist = images.load_images_to_display(id)

    return render_template("edit.html", current_date = datetime.now().date(),
                                        title = gameinfo[0],
                                        description = gameinfo[1],
                                        price = gameinfo[2],
                                        release_date = gameinfo[3],
                                        release_time = str(gameinfo[4])[:-3],
                                        released = validation.is_released(gameinfo[3], gameinfo[4]),
                                        categorieslist = categories.get_categories(),
                                        selectedcategories = [x[1] for x in categories.get_categories(id)],
                                        imagelist = imagelist,
                                        gameid = id)

@app.route("/game/<int:id>/deletereview", methods=["GET"])
def deletereview(id):
    username = (request.args.get("username"))
    if username != None and users.is_moderator():
        reviews.delete_review(users.get_userid(username), id)
    else: 
        reviews.delete_review(users.user_id(), id)
    return redirect(f"/game/{id}")