from datetime import datetime

def validate_gameinfo(title, description, price, date, time):
    def checkprice(price):
        split = price.split(".")
        if len(split) != 2:
            return False
        if not split[0].isdigit() or not split[1].isdigit():
            return False
        if int(split[0]) < 0 or int(split[1]) < 0 or len(split[1]) > 2:
            return False
        if int(split[0]) == 0 and len(split[0]) > 1:
            return False
        return True
    def checkdate(date):
        try:
            datetime.strptime(date, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    def checktime(time):
        split = time.split(":")
        if len(split) != 2:
            return False
        if len(split[0]) != 2 or len(split[1]) != 2:
            return False
        if not split[0].isdigit() or not split[1].isdigit():
            return False
        if int(split[0]) < 0 or int(split[0]) > 23:
            return False
        if int(split[1]) < 0 or int(split[1]) > 59:
            return False
        return True
    if not title or len(title) > 100:
        return False
    if not price or not checkprice(price):
        return False
    if not date or date < datetime.now().strftime("%Y-%m-%d") or not checkdate(date):
        return False
    if len(description) > 1000:
        return False
    if not time or not checktime(time):
        return False

    return title, description, price, date, time

def validate_imagesize(imagedata):
    if len(imagedata) > 3*1024*1024:
        return False
    return True

def fix_price(price):
    if price == "":
        price = "{:.2f}".format(0)
    else:
        price = "{:.2f}".format(float(price))
    split = price.split(".")
    euros = split[0]
    cents = split[1]

    if euros == "":
        euros = "0"
    if int(euros) == 0:
        euros = "0"

    if cents == "":
        cents = "00"
    if len(cents) > 2:
        cents = cents[:2]
    if int(cents) == 0:
        cents = "00"

    price = str(int(euros)) + "." + str(cents)
    return price

def is_released(game_date, game_time):
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    return current_date >= game_date and current_time >= game_time

def releasing_in(game_date, game_time):
    current = datetime.now()
    game = datetime.combine(game_date, game_time)
    delta = game-current
    units = [("year", 365), ("month", 30), ("week", 7), ("day", 1)]

    for unit, value in units:
        if delta.days >= value:
            count = delta.days // value
            return f"The game is releasing in {count} {unit}{'s' if count > 1 else ''}"

    hours = int(delta.total_seconds() // 3600)
    if hours != 0:
        return "The game is releasing in", hours, "hours"
    else:
        return "The game is releasing in an hour"