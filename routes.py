from datetime import datetime
from random import shuffle
from flask import redirect, render_template, request, session
from werkzeug.exceptions import BadRequestKeyError
from app import app
from Modules import users, balance, games, images, validation, reviews, library, \
                    wishlist, cart, history, temporaryimages, categories

@app.route("/", methods=["GET"])
def frontpage():
    return render_template("frontpage.html", credits=balance.get_balance(users.user_id()),
                                             user = users.get_username(),
                                             user_id = users.user_id(),
                                             creator = users.is_creator(),
                                             moderator = users.is_moderator())

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET": # todo error: already logged in
        return render_template("login.html")
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
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if not validation.validate_username(username):
        return render_template("register.html") # todo error: invalid username
    if password1 != password2: # todo error: password mismatch
        return render_template("register.html")
    if users.register(username, password1):
        return redirect("/")
    return render_template("register.html") # todo error: username already in use

@app.route("/balance", methods=["GET", "POST"])
def balance_page():
    user_id = users.user_id()
    if request.method == "GET":
        return render_template("balance.html", balance = balance.get_balance(user_id))
    if session["csrf_token"] != request.form["csrf_token"]:
        return redirect("/")
    amount = request.form.get("button")
    if amount == "own_value":
        amount = request.form.get("amount")
    amount = amount.split(".")[0]
    if not validation.validate_balance_amount(int(amount)):
        return redirect("/") # todo error: amount not correct

    if balance.update_balance(user_id, amount):
        history.add_balance_to_history(user_id, datetime.now().strftime("%Y-%m-%d"), amount)
        return redirect("/")
    return redirect("/") # todo error: adding balance failed

@app.route("/library", methods=["GET"])
def library_page():
    query = request.args.get("query")
    ownedgames = library.get_library(users.user_id(), query)

    return render_template("library.html", ownedgames = ownedgames,
                                           searchtext = query if query else True)

@app.route("/wishlist", methods=["GET", "POST"])
def wishlist_page():
    user_id = users.user_id()
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            return redirect("/")
        game_id = int(request.form["game_id"])
        if request.form["remove"] == "remove":
            wishlist.remove_from_wishlist(user_id, game_id)
        else:
            date = datetime.now().strftime("%Y-%m-%d")
            if wishlist.already_in_wishlist(user_id, game_id):
                return redirect("/wishlist") # todo error: game already in wishlist
            if not wishlist.add_to_wishlist(user_id, game_id, date):
                return redirect("/wishlist") # todo error: adding to wishlist failed

    onsale = request.args.get("onsale")
    query = request.args.get("query")

    wishlistgames = wishlist.get_wishlist(user_id, onsale, query)
    releasedgames = []
    for game in wishlistgames:
        gameinfo = games.get_game(game[1])
        if validation.is_released(gameinfo[3], gameinfo[4]):
            releasedgames.append(game)

    return render_template("wishlist.html", games = wishlistgames,
                                            searchtext = query if query else True,
                                            released = releasedgames,
                                            pressed = onsale,
                                            cart = [x[0] for x in cart.get_cart(user_id)])

@app.route("/cart", methods=["GET", "POST"])
def cart_page():
    user_id = users.user_id()
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            return redirect("/")
        game_id = int(request.form["game_id"])
        if request.form["remove"] == "remove":
            cart.remove_from_cart(user_id, game_id)
        else:
            gameinfo = games.get_game(game_id)
            if not validation.is_released(gameinfo[3], gameinfo[4]):
                return redirect("/cart") # todo error: game is not released yet
            if cart.game_in_cart(user_id, game_id):
                return redirect("/cart") # todo error: game already in cart
            if not cart.add_to_cart(user_id, game_id):
                return redirect("/cart") # todo error: adding to cart failed

    cartgames = cart.get_cart(user_id)
    total = cart.get_cart_total(user_id)
    userbalance = balance.get_balance(user_id)
    enough_balance = False
    try:
        if total <= userbalance:
            enough_balance = True
    except TypeError:
        pass
    return render_template("cart.html", cartgames = cartgames,
                                        total = total,
                                        balance = userbalance,
                                        enough_balance = enough_balance)

@app.route("/cart/checkout", methods=["POST"])
def checkout():
    user_id = users.user_id()
    if session["csrf_token"] != request.form["csrf_token"]:
        return redirect("/")

    for game in cart.get_cart(user_id):
        price = float(game[4])
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
    user_id = users.user_id()
    query = request.args.get("query")
    categorieslist = request.args.getlist("categories")
    selectedsort = request.args.get("sort", "random")

    gamelist = games.search_games(query, categorieslist, selectedsort)
    wished = [game for game in gamelist if not wishlist.already_in_wishlist(user_id, game[5])]
    incart = [x[0] for x in cart.get_cart(user_id)]
    owned  = [game for game in gamelist if not library.already_in_library(user_id, game[5])]

    return render_template("allgames.html", games = gamelist,
                                            categories = categories.get_categories(),
                                            searchtext = query if query else True,
                                            selectedcategories = [int(x) for x in categorieslist],
                                            wishlist = wished,
                                            owned = owned,
                                            cart = incart,
                                            selectedsort = selectedsort)

@app.route("/newgame", methods=["GET"])
def newgame():
    if not users.is_creator() and not users.is_moderator():
        return redirect("/") # todo error: no permission to create games
    return render_template("newgame.html", current_date = datetime.now().strftime("%Y-%m-%d"),
                                           current_time = datetime.now().strftime("%H:%M"),
                                           categories = categories.get_categories())

@app.route("/game/preview", methods=["POST"])
def preview():
    if session["csrf_token"] != request.form["csrf_token"]:
        return redirect("/")
    if not users.is_creator() and not users.is_moderator():
        return redirect("/") # todo error: no permission to create games
    try:
        selectedcategories = request.form.getlist("categories")
        price = validation.fix_price(request.form["price"])
        title, description, price, date, time = validation.validate_gameinfo(request.form["title"],
                                                                             request.form["desc"],
                                                                             price,
                                                                             request.form["date"],
                                                                             request.form["time"])
    except TypeError:
        return redirect("/") # todo error: invalid input

    edit = False
    gameid = False
    imagelist = []
    temporaryimages.empty_temporary_images(users.user_id())

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
    if session["csrf_token"] != request.form["csrf_token"]:
        return redirect("/")
    try:
        title, description, price, date, time = validation.validate_gameinfo(request.form["title"],
                                                                             request.form["desc"],
                                                                             request.form["price"],
                                                                             request.form["date"],
                                                                             request.form["time"])
        gamescategories = request.form.getlist("categories")
    except TypeError: # todo error: invalid input
        return redirect("/")

    if request.form["edit"] == "True":
        gameid = request.form["gameid"]
        if not games.update_game(gameid, title, description, price, date, time):
            return redirect ("/") # todo error: something went wrong when adding games
        categories.del_gamecategories(gameid)
        images.del_images(gameid)
    else:
        gameid = games.add_newgame(title, description, price, date, time, users.user_id())

    imagelist = temporaryimages.get_temporary_images(users.user_id())
    temporaryimages.empty_temporary_images(users.user_id())
    if imagelist:
        for image in imagelist:
            if not images.add_gameimage(gameid, image[0], image[1]):
                pass # todo error: uploading image to db failed.

    for category in gamescategories:
        category_id = categories.get_categoryid(category)
        if category_id is not None:
            categories.add_game_to_category(gameid, category_id)
        else: # todo error: category not found
            pass
    return redirect ("/")

@app.route("/game/<int:gameid>", methods=["GET", "POST"])
def game_page(gameid):
    user_id = users.user_id()
    game = games.get_game(gameid)
    if not game: # todo error: game not found
        return redirect("/")

    if request.method == "GET":
        imagelist = images.load_images_to_display(gameid)

        allreviews = reviews.show_reviews(gameid)
        shuffle(allreviews)
        your_review = reviews.already_reviewed(user_id, gameid)
        your_image = 0
        if your_review:
            allreviews.remove(your_review)
            your_image = images.encode_image(your_review[-1])

        allreviews = images.encode_reviewpictures(allreviews)

        released = validation.is_released(game[3], game[4])
        releasing_in = validation.releasing_in(game[3], game[4])
        price, salepercentage, saleprice = games.get_price(gameid)
        editpermission = (game[6] == user_id) or users.is_moderator()

        return render_template("game.html", game_id = gameid,
                                            title = game[0],
                                            description = game[1],
                                            price = price,
                                            priceoff = salepercentage,
                                            saleprice = saleprice,
                                            release_date = game[3],
                                            released = released,
                                            releasing_in = releasing_in,
                                            creator = game[5],
                                            creatorid = game[6],
                                            editpermission = editpermission,
                                            moderator = users.is_moderator(),
                                            imagelist = imagelist,
                                            reviews = allreviews,
                                            categories = categories.get_categories(gameid),
                                            your_review = your_review,
                                            your_image = your_image,
                                            owned = library.already_in_library(user_id, gameid))
    if session["csrf_token"] != request.form["csrf_token"]:
        return redirect(str(gameid))
    try:
        discount = request.form["discount"]
        if discount == "" or not validation.validate_discount(discount):
            return redirect(str(gameid)) # todo error: no / invalid discount
        if not games.update_game_discount(gameid, 1-int(discount)*0.01):
            return redirect(str(gameid)) # todo error: updating database failed

    except BadRequestKeyError:
        date = datetime.now().strftime("%Y-%m-%d")
        rating = request.form["rating"]
        review = request.form["review"]
        if not validation.validate_rating(rating, review):
            return redirect(str(gameid))
        if request.form["edited"] == "False":
            reviews.add_review(user_id, gameid, date, rating, review)
        elif request.form["edited"] == "True":
            reviews.edit_review(user_id, gameid, date, rating, review)

    return redirect(str(gameid))

@app.route("/game/<int:gameid>/edit", methods=["GET"])
def editgame(gameid):
    gameinfo = games.get_game(gameid)
    if not (users.is_moderator() or users.user_id() == gameinfo[6]): # todo error: not permission
        return redirect("/")
    imagelist = images.load_images_to_display(gameid)
    selectedcategories = [x[1] for x in categories.get_categories(gameid)]

    return render_template("editgame.html", current_date = datetime.now().date(),
                                        title = gameinfo[0],
                                        description = gameinfo[1],
                                        price = gameinfo[2],
                                        release_date = gameinfo[3],
                                        release_time = str(gameinfo[4])[:-3],
                                        released = validation.is_released(gameinfo[3], gameinfo[4]),
                                        categorieslist = categories.get_categories(),
                                        selectedcategories = selectedcategories,
                                        imagelist = imagelist,
                                        gameid = gameid)

@app.route("/game/<int:gameid>/deletereview", methods=["GET"])
def deletereview(gameid):
    username = request.args.get("username")
    if username and users.is_moderator():
        reviews.delete_review(users.get_userid(username), gameid)
    else:
        reviews.delete_review(users.user_id(), gameid)
    return redirect(f"/game/{gameid}")

@app.route("/game/<int:gameid>/deletegame", methods=["GET", "POST"])
def deletegame(gameid):
    gameowner = games.get_game(gameid)[6]
    if not (users.is_moderator() or users.user_id() == gameowner): # todo error: not permission
        return redirect("/")
    if request.method == "GET":
        return render_template("deletion.html", 
                                id = gameid,
                                message = "Are you sure about deleting game:",
                                action = f"/game/{gameid}/deletegame")
    if session["csrf_token"] != request.form["csrf_token"]:
        return redirect("/")
    if not games.del_game(gameid): # todo error: game deletion failed
        pass
    return redirect("/")

@app.route("/profile/<int:profileid>", methods=["GET"])
def profile(profileid):
    profileinfo = users.get_profile(profileid)
    visible = profileinfo[0][4] or users.is_moderator() or users.user_id() == profileid
    if not profileinfo or not visible:
        return redirect("/") # todo error: profile not found / profile is private
    profileinfo = profileinfo[0]
    permission = True if users.user_id() == profileid or users.is_moderator() else False
    name, data = images.get_profilepic(profileinfo[6])
    return render_template("profile.html", permission = permission,
                                           userid = profileid,
                                           username = profileinfo[0],
                                           bio = profileinfo[1],
                                           joined = profileinfo[2],
                                           role = profileinfo[3],
                                           public = profileinfo[4],
                                           picturename = name,
                                           picturedata = data,
                                           games = library.get_library(profileid),
                                           gamesmade = games.games_by_creator(profileid))

@app.route("/profile/<int:profileid>/edit", methods=["GET", "POST"])
def editprofile(profileid):
    profileinfo = users.get_profile(profileid)
    if not profileinfo or not (users.is_moderator() or users.user_id() == profileinfo[0][5]):
        return redirect("/") # todo error: no permission
    if request.method == "GET":
        return render_template("editprofile.html", user_id = profileid,
                                                   username = profileinfo[0][0],
                                                   bio = profileinfo[0][1],
                                                   visibility = profileinfo[0][4])
    if session["csrf_token"] != request.form["csrf_token"]:
        return redirect("/")
    username = request.form["username"]
    bio = request.form["bio"]
    visibility = request.form["visibility"]
    image = request.files["profpicture"]

    if not (validation.validate_username(username) and validation.validate_bio(bio)):
        return redirect(f"/profile/{profileid}") # todo error: invalid bio / username

    if not users.update_profile(profileid, username, bio, visibility, image):
        pass # todo error: updating info failed
    return redirect(f"/profile/{profileid}")

@app.route("/profile/<int:profileid>/history", methods=["GET"])
def profilehistory(profileid):
    profileinfo = users.get_profile(profileid)
    if not profileinfo or not (users.is_moderator() or users.user_id() == profileinfo[0][5]):
        return redirect("/") # todo error: profile not found
    return render_template("history.html", history = history.get_history(profileid),
                                           username = profileinfo[0][0])

@app.route("/profile/<int:profileid>/delete", methods=["GET", "POST"])
def del_profile(profileid):
    profileinfo = users.get_profile(profileid)
    if not profileinfo or not (users.is_moderator() or users.user_id() == profileinfo[0][5]):
        return redirect("/") # todo error: no permission
    if request.method == "GET":
        return render_template("deletion.html",
                                id = profileid,
                                message = "Are you sure about deleting your account:",
                                action = f"/profile/{profileid}/delete")
    if session["csrf_token"] != request.form["csrf_token"]:
        return redirect("/")
    if not users.del_user(profileid): # todo error: user deletion failed
        pass
    return redirect("/")
