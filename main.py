from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from services import weather_service
import sqlite3
from datetime import datetime, timedelta
import atexit

updater = Updater("5440718277:AAFPwMvNactHwIkrZa00SAOicH2ddCbRyNs",
                  use_context=True)

con = None
cur = None


def close_connection():
    cur.close()
    con.close()


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello welcome to the weather bot", reply_markup=main_menu_keyboard())


def get_user_data(username):
    res = cur.execute(f"SELECT * FROM Location WHERE username='{username}'")
    return res.fetchone()


def message_handler(update: Update, context: CallbackContext):
    user_data = get_user_data(update.message.from_user.username)
    if not user_data:
        return update.message.reply_text("Send me your location.")
    match update.message.text:
        case "Today":
            data = weather_service.get_future_weather(user_data[1], user_data[2], 1)[0]
            text_for_user = f"{datetime.today().strftime('%Y-%m-%d')}\n Temp: {data['temp']}\n Maxtemp: {data['maxtemp']}\n Mintemp: {data['mintemp']}"
        case "Tomorrow":
            data = weather_service.get_future_weather(user_data[1], user_data[2], 2)[1]
            date = datetime.today() + timedelta(days=1)
            text_for_user = f"{date.strftime('%Y-%m-%d')}\n Temp: {data['temp']}\n Maxtemp: {data['maxtemp']}\n Mintemp: {data['mintemp']}"
        case "Next 5 days":
            temp_data = weather_service.get_future_weather(user_data[1], user_data[2], 5)
            text_for_user = ""
            for key, data in enumerate(temp_data):
                date = datetime.today() + timedelta(days=key+1)
                text_for_user += f"{date.strftime('%Y-%m-%d')}\n Temp: {data['temp']}\n Maxtemp: {data['maxtemp']}\n Mintemp: {data['mintemp']}\n"
        case _:
            return update.message.reply_text("I can't recognise that.")

    update.message.reply_text(text_for_user)


# --------------- Keyboard -------------
def main_menu_keyboard():
    buttons = [[KeyboardButton("Today")], [KeyboardButton("Tomorrow")], [KeyboardButton("Next 5 days")]]
    return ReplyKeyboardMarkup(buttons)


def location(update: Update, context: CallbackContext):
    current_pos = (update.message.location.latitude, update.message.location.longitude)
    cur.execute(f"INSERT INTO Location (username, lat, lon) VALUES ('{update.message.from_user.username}', {current_pos[0]}, {current_pos[1]})")
    print(current_pos, update.message.from_user.username)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.location, location))
updater.dispatcher.add_handler(MessageHandler(Filters.text, message_handler))


if __name__ == '__main__':
    con = sqlite3.connect("people_info.db", isolation_level=None, check_same_thread=False)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Location(username, lat, lon)")
    updater.start_polling()

    atexit.register(close_connection)


