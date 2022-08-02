from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, 
                     KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)

def make_usual_keyboard(keys: dict, columns: int):
    if len(keys) == 0:
        keyboard=ReplyKeyboardRemove()
    else:
        tg_keys = []
        keys_row = []       
        col = columns
        for key in keys:
            col-=1
            keys_row.append(KeyboardButton(text=keys[key]))
            if col == 0:
                col = columns
                tg_keys.append(keys_row)
                keys_row = []
        if len(keys_row) > 0:
            tg_keys.append(keys_row)
        keyboard = ReplyKeyboardMarkup(tg_keys, resize_keyboard=True)
    return keyboard


def make_inline_keyboard(keys: dict, columns: int):
    pass


def make_keyboard(keys: dict, type: str="usual", columns: int=1):

    if type == "usual":
        keyboard = make_usual_keyboard(keys, columns)
    else:
        keyboard = make_inline_keyboard(keys, columns)
    return keyboard


