from datetime import datetime
from random import shuffle
from flask import redirect, render_template, request, session, abort, flash
from app import app
from Modules import users, balance, games, images, validation, reviews, library, \
                    wishlist, cart, history, temporaryimages, categories

@app.route("/", methods=["GET"])
def frontpage():
    return render_template("frontpage.html", user = users.get_username(),
                                             user_id = users.user_id(),
                                             games = games.get_randomgames())

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    username = request.values.get("username")
    if request.method == "POST":
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        error = "Username and password didn't match"
    return render_template("login.html", errormessage = error if error != None else False,
                                         username = username)

@app.route("/logout", methods=["GET"])
def logout():
    users.logout()
    return redirect(request.referrer)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    username = request.values.get("username")
    if request.method == "POST":
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if not validation.validate_username(username):
            error = "Username must be between 3 and 25 characters long"
        elif password1 != password2:
            error = "Passwords didn't match"
        elif password1 == "":
            error = "Password must be at least 1 character long"
        elif users.register(username, password1):
            return redirect("/")
        else: 
            error = "This username is already in use"
    return render_template("register.html", errormessage = error if error != None else False,
                                            username = username)

@app.route("/balance", methods=["GET", "POST"])
def balance_page():
    user_id = users.user_id()
    if request.method == "GET":
        return render_template("balance.html", balance = balance.get_balance(user_id))
    check_csrf()
    amount = request.form["button"]
    if amount == "own_value":
        amount = request.form["amount"]
    amount = amount.split(".")[0]
    date = datetime.now().strftime("%Y-%m-%d")

    if not (amount and validation.validate_balance_amount(int(amount))):
        return render_template("error.html", message="Incorrect amount")
    if balance.update_balance(user_id, amount) and history.add_balance_to_history(user_id, date, amount):
        return redirect("/")
    return render_template("error.html", message="Adding balance failed")

@app.route("/library", methods=["GET"])
def library_page():
    query = request.args.get("query")
    ownedgames = library.get_library(users.user_id(), query)
    return render_template("library.html", ownedgames = ownedgames,
                                           searchtext = query or True)

@app.route("/wishlist", methods=["GET", "POST"])
def wishlist_page():
    user_id = users.user_id()
    if request.method == "POST":
        check_csrf()
        game_id = int(request.form["game_id"])
        if request.form["remove"] == "remove":
            if not wishlist.remove_from_wishlist(user_id, game_id):
                return render_template("error.html", message="Removing from wishlist failed")
        else:
            date = datetime.now().strftime("%Y-%m-%d")
            if wishlist.already_in_wishlist(user_id, game_id):
                return render_template("error.html", message="This game is already in wishlist")
            if not wishlist.add_to_wishlist(user_id, game_id, date):
                return render_template("error.html", message="Adding to wishlist failed")
        return redirect(request.referrer)

    onsale = request.args.get("onsale")
    query = request.args.get("query")
    wishlistgames = wishlist.get_wishlist(user_id, onsale, query)

    return render_template("wishlist.html", games = wishlistgames,
                                            searchtext = query or True,
                                            released = validation.get_releasedgames(wishlistgames),
                                            pressed = onsale,
                                            cart = [x[0] for x in cart.get_cart(user_id)])

@app.route("/cart", methods=["GET", "POST"])
def cart_page():
    user_id = users.user_id()
    if request.method == "POST":
        check_csrf()
        game_id = int(request.form["game_id"])
        if request.form["remove"] == "remove":
            if not cart.remove_from_cart(user_id, game_id):
                return render_template("error.html", message="Failed to remove item. Try again.")
        else:
            gameinfo = games.get_game(game_id)
            if not validation.is_released(gameinfo[3], gameinfo[4]):
                return render_template("error.html", message="This game isn't released yet")
            if cart.game_in_cart(user_id, game_id):
                return render_template("error.html", message="This game is already in cart")
            if not cart.add_to_cart(user_id, game_id):
                return render_template("error.html", message="Adding to cart failed")
        return redirect(request.referrer)

    cartgames = cart.get_cart(user_id)
    total = cart.get_cart_total(user_id)
    userbalance = balance.get_balance(user_id)
    enough_balance = total is not None and userbalance is not None and total <= userbalance
    return render_template("cart.html", cartgames = cartgames,
                                        total = total,
                                        balance = userbalance,
                                        enough_balance = enough_balance)

@app.route("/cart/checkout", methods=["POST"])
def checkout():
    user_id = users.user_id()
    check_csrf()
    for game in cart.get_cart(user_id):
        price = float(game[4])
        game_id = game[2]
        date = datetime.now().strftime("%Y-%m-%d")
        if price > balance.get_balance(user_id):
            return render_template("error.html", message="Not enough balance")

        if not all([library.add_to_library(user_id, game_id),
                    cart.remove_from_cart(user_id, game_id),
                    balance.update_balance(user_id, -price),
                    wishlist.remove_from_wishlist(user_id, game_id),
                    history.add_game_to_history(user_id, game_id, date, price)]):
            return render_template("error.html", message="An error occured. Try again.")
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
                                            searchtext = query or True,
                                            selectedcategories = [int(x) for x in categorieslist],
                                            wishlist = wished,
                                            owned = owned,
                                            cart = incart,
                                            selectedsort = selectedsort,
                                            released = validation.get_releasedgames(gamelist),
                                            newgamepermission = validation.createpermission())

@app.route("/newgame", methods=["GET"])
def newgame():
    if not users.is_creator() and not users.is_moderator():
        return render_template("error.html", message="No permission to create games")
    return render_template("newgame.html", current_date = datetime.now().strftime("%Y-%m-%d"),
                                           current_time = datetime.now().strftime("%H:%M"),
                                           categories = categories.get_categories())

@app.route("/game/preview", methods=["POST"])
def preview():
    check_csrf()
    if not users.is_creator() and not users.is_moderator():
        return render_template("error.html", message="No permission to create games")
    try:
        selectedcategories = request.form.getlist("categories")
        price = validation.fix_price(request.form["price"])
        title, description, price, date, time = validation.validate_gameinfo(request.form["title"],
                                                                             request.form["desc"],
                                                                             price,
                                                                             request.form["date"],
                                                                             request.form["time"])
    except TypeError:
        return render_template("error.html", message="Invalid input")
    edit = request.form["editing"] == "True"
    gameid = request.form["gameid"] if edit else False
    imagelist = []
    if not temporaryimages.empty_temporary_images(users.user_id()):
        return render_template("error.html", message="An error occured handling images. Try again.")

    if edit:
        selectedimages = request.form.getlist("image_ids")
        if len(selectedimages) != 0:
            imgs = images.load_images(selectedimages)
            imagelist += imgs

    loadedimages = request.files.getlist("loadedimages")
    imgs = images.load_images(loadedimages)
    if imgs == False:
        return render_template("error.html", message="Image was too large. \
                                                      Maximum size is 1600x900")
    imagelist += imgs
    if len(imagelist) > 5:
        return render_template("error.html", message="too many images")

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
    check_csrf()
    try:
        gamescategories = request.form.getlist("categories")
        title, description, price, date, time = validation.validate_gameinfo(request.form["title"],
                                                                             request.form["desc"],
                                                                             request.form["price"],
                                                                             request.form["date"],
                                                                             request.form["time"])
    except TypeError:
        return render_template("error.html", message="Invalid input")

    user_id = users.user_id()
    edit = request.form["edit"] == "True"
    game_id = request.form["gameid"] if edit else games.add_newgame(title, description, price,
                                                                    date, time, user_id)
    if edit and not all([games.update_game(game_id, title, description, price, date, time, user_id),
                        categories.del_gamecategories(game_id),
                        images.del_images(game_id)]):
        return render_template("error.html", message="An error occured. Try again.")

    imagelist = temporaryimages.get_temporary_images(user_id)
    if not temporaryimages.empty_temporary_images(user_id):
        return render_template("error.html", message="An error occured loading images.")
    if imagelist and not all(images.add_gameimage(game_id, img[0], img[1]) for img in imagelist):
        return render_template("error.html", message="Uploading images failed. Try again.")

    for category in gamescategories:
        category_id = categories.get_categoryid(category)
        if category_id is None or not categories.add_game_to_category(game_id, category_id):
            return render_template("error.html", message="Adding categories failed. \
                                                          Category not found")
    return redirect ("/")

@app.route("/game/<int:game_id>", methods=["GET", "POST"])
def game_page(game_id):
    user_id = users.user_id()
    game = games.get_game(game_id)
    if not game:
        return render_template("error.html", message="Game not found. It may have been deleted.")

    if request.method == "GET":
        allreviews = reviews.show_reviews(game_id)
        shuffle(allreviews)
        your_review = reviews.already_reviewed(user_id, game_id)
        if your_review:
            allreviews.remove(your_review)

        return render_template("game.html", game_id = game_id,
                                game = game,
                                price = games.get_price(game_id),
                                released = validation.is_released(game[3], game[4]),
                                releasing_in = validation.releasing_in(game[3], game[4]),
                                editpermission = (game[6] == user_id) or users.is_moderator(),
                                moderator = users.is_moderator(),
                                imagelist = images.load_images_to_display(game_id),
                                reviews = images.encode_reviewpictures(allreviews),
                                categories = categories.get_categories(game_id),
                                your_review = your_review,
                                owned = library.already_in_library(user_id, game_id),
                                cart = [x[0] for x in cart.get_cart(user_id)],
                                wishlist = [x[0] for x in wishlist.get_wishlist(user_id)])
    check_csrf()
    discount = request.form.get("discount")
    if discount and validation.validate_discount(discount):
        if not games.update_game_discount(game_id, 1-int(discount)*0.01):
            return render_template("error.html", message="Updating discount failed. Try again.")
    else:
        date = datetime.now().strftime("%Y-%m-%d")
        rating = request.form.get("rating")
        review = request.form.get("review")
        if review != None and validation.validate_rating(rating, review):
            if request.form.get("edited") == "False":
                if not reviews.add_review(user_id, game_id, date, rating, review):
                    return render_template("error.html", message="Adding review failed. Try again.")
            elif request.form.get("edited") == "True":
                if not reviews.edit_review(user_id, game_id, date, rating, review):
                    return render_template("error.html", message="Editing review failed. Try again")
    return redirect(str(game_id))

@app.route("/game/<int:game_id>/edit", methods=["GET"])
def editgame(game_id):
    gameinfo = games.get_game(game_id)
    if not (users.is_moderator() or users.user_id() == gameinfo[6]):
        return render_template("error.html", message="Permission denied to edit this game")

    return render_template("editgame.html", gameid = game_id,
                            game = gameinfo,
                            current_date = datetime.now().date(),
                            release_time = str(gameinfo[4])[:-3],
                            released = validation.is_released(gameinfo[3], gameinfo[4]),
                            categorieslist = categories.get_categories(),
                            selectedcategories = [x[1] for x in categories.get_categories(game_id)],
                            imagelist = images.load_images_to_display(game_id))

@app.route("/game/<int:game_id>/deletereview", methods=["GET"])
def deletereview(game_id):
    user_id = request.args.get("id") or users.user_id()
    if (users.is_moderator() or user_id == users.user_id()) and reviews.delete_review(user_id, game_id):
        return redirect(f"/game/{game_id}")
    return render_template("error.html", message="Deleting review failed.")

@app.route("/game/<int:game_id>/deletegame", methods=["GET", "POST"])
def deletegame(game_id):
    gameowner = games.get_game(game_id)[6]
    if not (users.is_moderator() or users.user_id() == gameowner):
        return render_template("error.html", message="Permission denied to delete this game.")
    if request.method == "GET":
        return render_template("deletion.html",
                                id = game_id,
                                message = "Are you sure about deleting this game:",
                                action = f"/game/{game_id}/deletegame")
    check_csrf()
    if not games.del_game(game_id):
        return render_template("error.html", message="Failed to delete game. Try again.")
    return redirect("/")

@app.route("/profile/<int:profile_id>", methods=["GET"])
def profile(profile_id):
    profileinfo = users.get_profile(profile_id)
    if not profileinfo or not (profileinfo[4] or users.is_moderator() or users.user_id() == profile_id):
        return render_template("error.html", message="No profile here... It might be private.")
    permission = True if users.user_id() == profile_id or users.is_moderator() else False
    name, data = images.get_profilepic(profileinfo[6])
    return render_template("profile.html", permission = permission,
                                           userid = profile_id,
                                           user = profileinfo,
                                           picturename = name,
                                           picturedata = data,
                                           games = library.get_library(profile_id),
                                           gamesmade = games.games_by_creator(profile_id))

@app.route("/profile/<int:profile_id>/edit", methods=["GET", "POST"])
def editprofile(profile_id):
    profileinfo = users.get_profile(profile_id)
    if not profileinfo or not (users.is_moderator() or users.user_id() == profileinfo[5]):
        return render_template("error.html", message="You don't have permission to \
                                                      edit this profile")
    if request.method == "GET":
        return render_template("editprofile.html", user = profileinfo)

    check_csrf()
    username = request.form["username"]
    bio = request.form["bio"]
    visibility = request.form["visibility"]
    image = request.files["profpicture"]
    role = request.form["role"]

    if not (validation.validate_username(username) and validation.validate_bio(bio)):
        return render_template("error.html", message="Invalid username / bio. Try something else.")
    if not users.update_profile(profile_id, username, bio, visibility, role, image):
        return render_template("error.html", message="Updating profile failed. Try again.")
    return redirect(f"/profile/{profile_id}")

@app.route("/profile/<int:profile_id>/history", methods=["GET"])
def profilehistory(profile_id):
    profile_info = users.get_profile(profile_id)
    if not profile_info or not (users.is_moderator() or users.user_id() == profile_info[5]):
        return render_template("error.html", message="Permission denied to view history")
    return render_template("history.html", history = history.get_history(profile_id),
                                           username = profile_info[0])

@app.route("/profile/<int:profile_id>/delete", methods=["GET", "POST"])
def del_profile(profile_id):
    profileinfo = users.get_profile(profile_id)
    if not profileinfo or not (users.is_moderator() or users.user_id() == profileinfo[5]):
        return render_template("error.html", message="Permission denied to delete user")
    if request.method == "GET":
        return render_template("deletion.html",
                                id = profile_id,
                                message = "Are you sure about deleting your account:",
                                action = f"/profile/{profile_id}/delete")
    check_csrf()
    if not users.del_user(profile_id):
        return render_template("error.html", message="Deletion failed. Try again.")
    return redirect("/")

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
