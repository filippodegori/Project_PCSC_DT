# pip install python-telegram-bot  v13
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler, \
    CallbackContext
from secret import bot_token
from datetime import datetime
from requests import get, post

data = {
    "filippo": {
        "locations": [],
        "password": "filippo1",
        "logged": False,
        "recording": False
    },
    "lisa": {
        "locations": [],
        "password": "lisa1",
        "logged": False,
        "recording": False
    },
    "marco": {
        "locations": [],
        "password": "marco1",
        "logged": False,
        "recording": False
    },
}


base_url = 'https://europe-west1-project-pcsc-dt.cloudfunctions.net/save_data_to_bigquery'


def welcome(update, context):
    # messaggio di benvenuto
    msg = f'''Ciao {update.effective_user.first_name}, benvenuto in <b>DT-Chatbot</b>. Ecco l'elenco dei comandi:
    <b>- login [username] [password] </b> (ad esempio: login filippo 123456) per effettuare il login.
    <b>- start [username] </b> per iniziare a registrare le posizioni.
    <b>- stop [username] </b> per smettere di registrare le posizioni.
    <b>- logout [username] </b> per effettuare il logout.'''
    update.message.reply_text(msg, parse_mode='HTML')


def process_chat(update, context):
    # print(context)
    msg = update.message.text.lower()

    # comando di login
    if msg.startswith('login'):
        cmd, username, password = msg.split(' ')
        if username not in data:
            update.message.reply_text("Mi dispiace, questo username non è valido")
        else:
            if data[username]["logged"]:
                update.message.reply_text(f"{username} è già loggato")
            else:
                if password == data[username]["password"]:
                    data[username]["logged"] = True
                    context.user_data['username'] = username
                    update.message.reply_text(
                        f"Benvenuto {username}! Comincia a condividere la posizione in tempo reale")
                else:
                    update.message.reply_text("Mi dispiace, la password è errata")

    # comando di logout
    elif msg.startswith('logout'):
        cmd, username = msg.split(' ')
        if username not in data:
            update.message.reply_text("Mi dispiace, questo username non è valido")
        elif data[username]["logged"]:
            data[username]["logged"] = False
            update.message.reply_text(f"Logout di {username} effettuato con successo!")
        else:
            update.message.reply_text(f"Non si può fare il logout di {username}, poichè non è ancora loggato")

    # comando di inizio registrazione
    elif msg.startswith('start'):
        cmd, username = msg.split(' ')
        if username not in data:
            update.message.reply_text("Mi dispiace, questo username non è valido")
        elif data[username]["logged"]:
            data[username]["recording"] = True
            update.message.reply_text(f"Inizio registrazione delle posizioni di {username}")
        else:
            update.message.reply_text(f"Non si può inziare la registrazione delle posizioni di {username}, poichè non "
                                      f"è ancora loggato")

    # comando di fine registrazione
    elif msg.startswith('stop'):
        cmd, username = msg.split(' ')
        if username not in data:
            update.message.reply_text("Mi dispiace, questo username non è valido")
        elif data[username]["logged"]:
            if data[username]["recording"]:
                data[username]["recording"] = False
                update.message.reply_text(f"Fine della registrazione delle posizioni di {username}")
                start_loc = data[username]["locations"][0][1].strftime('%Y-%m-%d %H:%M:%S')
                end_loc = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                locations = data[username]["locations"]
                if locations:
                    route = 'LINESTRING('
                    for loc in locations:
                        route = route + f'{loc[0].longitude} {loc[0].latitude}, '
                    route = route + ')'
                    route = route.replace(', )', ')')
                    # print(route)
                    # print(start_loc)
                    # print(end_loc)
                    r = post(f'{base_url}',
                             json={'username': username, 'route': route, 'start_loc': start_loc, 'end_loc': end_loc})
                    print(r.text)
                else:
                    update.message.reply_text(f"Nessuna posizione registrata per {username}.")
            else:
                update.message.reply_text(f"Non si può terminare la registrazione per {username}, poichè non è ancora "
                                          f"iniziata")
        else:
            update.message.reply_text(
                f"Non si può terminare la registrazione delle posizioni di {username}, poichè non "
                f"è ancora loggato")

    # se nessuno dei comandi è stato digitato ridai il benvenuto
    else:
        welcome(update, context)


def get_location(update, context):
    message = None
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message

    username = context.user_data.get('username')
    if username:
        if data[username]["recording"]:
            data[username]["locations"].append((message.location, datetime.now()))


def main():
    print('bot started')
    upd = Updater(bot_token, use_context=True)
    disp = upd.dispatcher

    disp.add_handler(CommandHandler("start", callback=welcome))
    disp.add_handler(MessageHandler(Filters.regex('^.*$'), callback=process_chat))
    disp.add_handler(MessageHandler(Filters.location, callback=get_location))

    upd.start_polling()
    upd.idle()


if __name__ == '__main__':
    main()
