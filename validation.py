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

def validate_imagesize(imagedata): # todo: check image size
    if len(imagedata) > 3*1024*1024:
        return False
    return True

def validate_balance(): # validate balance
    pass