import telebot
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import mysql.connector
import jwt
import time
import asyncio

#mysql connect
cnx = mysql.connector.connect(user = 'root', password = 'root5115', host = 'localhost', database = 'users')
cursor = cnx.cursor()
#bot token
token = "7430419581:AAFV5bZJrV04IjBnx7Gl3dcezE9Xn0xBbOA"
bot = telebot.TeleBot(token)
#необходимые переменные
arr = {}
ADMIN_ID = 630043071
s = []


# Секретный ключ для подписи токенов
with open("secret.key", "rb") as key_file:
    SECRET_KEY = key_file.read()
#ветка диалога
with open("json.json", 'r', encoding="UTF-8") as f:
    file = json.load(f)
#spam message
with open("spam_post.json", 'r', encoding="UTF-8") as f:
    spam = json.load(f)


def editFile():
    with open("json.json", 'w', encoding="UTF-8") as f:
        f.write(json.dumps(file))


def editSpamFile():
    with open("spam_post.json", 'w', encoding="UTF-8") as f:
        f.write(json.dumps(spam))


def encode(data):
    # Определение полезной нагрузки токена
    payload = {'data': data}
    # Создание токена
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def decode(token):
    try:
        # Расшифровка токена
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # Токен истёк
        return None
    except jwt.InvalidTokenError:
        # Невалидный токен
        return None


#start отработчик
@bot.message_handler(commands=["start"])
def start(msg):
    t = 'start'
    markup = InlineKeyboardMarkup()
    for i in file['start']['btns']:
        markup.add(InlineKeyboardButton(f"{file['start']['btns'][i][0]}", callback_data=f"{file['start']['btns'][i][1]}"))
    if msg.chat.id == ADMIN_ID:
        markup.add(InlineKeyboardButton(f"Изменить сообщение", callback_data=f"start_new"))


    bot.send_message(msg.chat.id, f"{file[t]['text']}", reply_markup=markup)
    bot.delete_message(msg.chat.id, msg.message_id)


#spam target and forms to generate
@bot.message_handler(commands=["help"])
def start(msg):
    if msg.chat.id == ADMIN_ID:
        t = 'start'
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"расслыка", callback_data=f"spam"))
    
    
        bot.send_message(msg.chat.id, f"Хотите начать расслыку?", reply_markup=markup)
        bot.delete_message(msg.chat.id, msg.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "spam")
def but(call: types.CallbackQuery):
    if call.message.chat.id == ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"Изменить текст", callback_data="ssspam_text"))
        markup.add(InlineKeyboardButton(f"Изменить изображение", callback_data="ssspam_photo"))
        markup.add(InlineKeyboardButton(f"Изменить кнопки", callback_data="ssspam_btns"))
        markup.add(InlineKeyboardButton(f"Опубликовать", callback_data="ssspam_start"))
        text = ''
        for i in spam['btns']:
            text += f"Внешний вид - {i.split('-')[0]}\nССылка - {i.split('-')[1]}\n------\n"
        bot.send_photo(call.message.chat.id, photo=open('test.png', 'rb'), caption=f'{spam["text"]}\n\n\nКнопки:\n{text}', reply_markup=markup)
        bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.message_handler(content_types=['photo'])
def get_photo(message: types.Message):
    if message.chat.id == ADMIN_ID:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        save_path = 'test.png'
        with open(save_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        editSpamFile()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"Показать пост", callback_data="spam"))
        bot.send_message(message.chat.id, 'Фотография сохранена.', reply_markup=markup)


def new_text(message):
    if message.chat.id == ADMIN_ID:
        spam["text"] = message.text
        markup = InlineKeyboardMarkup()
        editSpamFile()
        markup.add(InlineKeyboardButton(f"Показать пост", callback_data="spam"))
        bot.send_message(message.chat.id, 'Текст Сохранён', reply_markup=markup)


def new_btns(message):
    if message.chat.id == ADMIN_ID:
        spam["btns"] = message.text.split(',').strip()
        markup = InlineKeyboardMarkup()
        editSpamFile()
        markup.add(InlineKeyboardButton(f"Показать пост", callback_data="spam"))
        bot.send_message(message.chat.id, 'Кнопки сохранены', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == "ssspam")
def but(call: types.CallbackQuery):
    if call.message.chat.id == ADMIN_ID:
        if call.data.split('_')[1] == "text":
            bot.send_message(call.message.chat.id, "Введите новый текст:")
            bot.register_next_step_handler(call.message, new_text)
        elif call.data.split('_')[1] == "photo":
            bot.send_message(call.message.chat.id, "Пришлите новое изображение для рассылки:")
            bot.register_next_step_handler(call.message, get_photo)
        elif call.data.split('_')[1] == "btns":
            bot.send_message(call.message.chat.id, "Введите новые кнопки в формате название-ссылка, название-ссылка,... \nОбратите внимание что в таком случае название не должно содержать запятых:")
            bot.register_next_step_handler(call.message, new_btns)
        elif call.data.split('_')[1] == "start":
            markup = InlineKeyboardMarkup()
            for i in spam["btns"]:
                markup.add(InlineKeyboardButton(i.split("-")[0], url=i.split("-")[1]))
            cursor.execute(f"SELECT userid FROM users")
            for i in cursor.fetchall():
                try:
                    bot.send_photo(decode(str(i).split("'")[1])["data"], photo=open('test.png', 'rb'), caption=f"{spam['text']}", reply_markup=markup)
                except BaseException as ex:
                    pass
            bot.send_message(call.message.chat.id, "Отправка окончена!")







@bot.message_handler(commands=["id"])
def start(msg):
    bot.send_message(msg.chat.id, f"{msg.chat.id}")
    with open("test1.txt", 'w', encoding="UTF-8") as f:
        f.write(str(msg))


@bot.message_handler(commands=["id_db"])
def start(msg):
    cursor.execute(f"SELECT userid, name, phone, mail FROM users WHERE userid = '{encode(str(msg.chat.id))}'")
    for i in cursor.fetchone():
        print(decode(i))



# ["about", "shop-online", "kontakts", "sales", "extendWarr", "extendWarrSelf", "extendWarrHelp", "problem", "video", "helpspec"]
@bot.callback_query_handler(func=lambda call: call.data in ["start", "about", "shop-online", "kontakts", "sales", "extendWarr", "extendWarrSelf", "extendWarrHelp", "problem", "video", "helpSup", "ansTrue", "ansFalse"])
def but(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    for i in file[call.data]['btns']:
        if file[call.data]["type"] == "url":
            markup.add(InlineKeyboardButton(f"{file[call.data]['btns'][i][0]}", url=f"{file[call.data]['btns'][i][1]}"))
        else:
            markup.add(InlineKeyboardButton(f"{file[call.data]['btns'][i][0]}", callback_data=f"{file[call.data]['btns'][i][1]}"))

    if call.message.chat.id == ADMIN_ID:
        markup.add(InlineKeyboardButton(f"Изменить сообщение", callback_data=f"{call.data}_new"))
    markup.add(InlineKeyboardButton(f"главная", callback_data="start"))
    bot.send_message(call.message.chat.id, text=f"{file[call.data]['text']}", reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.message_id)

    if call.data == "video":
        time.sleep(20)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"Да", callback_data=f"ansTrue"))
        markup.add(InlineKeyboardButton(f"Нет", callback_data=f"ansFalse"))
        bot.send_message(call.message.chat.id, text=f"Нам удалось вам помочь?", reply_markup=markup)





@bot.callback_query_handler(func=lambda call: call.data == "ofStore")
def but(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"главная", callback_data="start"))
    bot.send_photo(call.message.chat.id, photo=open("images/123.png", "rb"), caption=f"{file[call.data]['text']}", reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.message_id)



#calls for remake text and urls
def edit(msg):
    global s
    if len(s) == 2:
        file[s[0]][s[1]] = f"{msg.text}"
    elif len(s) == 4:
        file[s[1]][s[2]][s[3]][0] = f"{msg.text}"

    elif len(s) == 5:
        file[s[1]][s[2]][s[3]][1] = f"{msg.text}"
    editFile()


@bot.callback_query_handler(func=lambda call: call.data.split("_")[-1] == "new")
def but(call: types.CallbackQuery):
    comm = call.data.split('_')[0]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"Текст", callback_data=f"{call.data.split('_')[0]}_text"))

    for i in file[comm]['btns']:
        if file[comm]["type"] == "url":
            markup.add(InlineKeyboardButton(f"текст кнопки - {file[comm]['btns'][i][0]}", callback_data=f"file_{comm}_btns_{i}"))
            markup.add(InlineKeyboardButton(f"путь - {file[comm]['btns'][i][1]}", callback_data=f"file_{comm}_btns_{i}_content"))
        else:
            markup.add(InlineKeyboardButton(f"текст кнопки - {file[comm]['btns'][i][0]}", callback_data=f"file_{comm}_btns_{i}"))
    markup.add(InlineKeyboardButton(f"главная/отменить изменения", callback_data="start"))
    bot.send_message(call.message.chat.id, text=f"{file[comm]['text']}\n\n\n Что хотите изменить?", reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "file" or call.data.split('_')[-1] == 'text')
def but(call: types.CallbackQuery):
    global s
    s = call.data.split("_")
    bot.send_message(call.message.chat.id, f"Введите новое значение")
    bot.register_next_step_handler(call.message, edit)
    bot.delete_message(call.message.chat.id, call.message.message_id)









###form
@bot.callback_query_handler(func=lambda call: call.data == "startForm")
def but(call: types.CallbackQuery):
    bot.send_message(call.message.chat.id, f"{file[call.data]['text']}")
    bot.register_next_step_handler(call.message, second_step)
    bot.delete_message(call.message.chat.id, call.message.message_id)


def second_step(msg):
    arr[msg.chat.id] = []
    arr[msg.chat.id].append(msg.text)
    bot.send_message(msg.chat.id, "ВВедите телефон")
    bot.register_next_step_handler(msg, third_step)


def third_step(msg):
    if msg.text[0] == '+' and len(msg.text) == 12:
        arr[msg.chat.id].append(msg.text)
        bot.send_message(msg.chat.id, "ВВедите почту")
        bot.register_next_step_handler(msg, foth_step)
    elif len(msg.text) == 11:
        arr[msg.chat.id].append(msg.text)
        bot.send_message(msg.chat.id, "ВВедите почту")
        bot.register_next_step_handler(msg, foth_step)
    else:
        bot.send_message(msg.chat.id, "Неправльный формат номера телефона!\nВведите его вновь:")
        bot.register_next_step_handler(msg, third_step)


def foth_step(msg):
    if '@' in msg.text:
        arr[msg.chat.id].append(msg.text)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"Подтвердить", callback_data=f"continueForm"))
        markup.add(InlineKeyboardButton(f"Заполнить заново", callback_data=f"startForm"))
        bot.send_message(msg.chat.id, f"Форма заполнена - проверьте\n{arr[msg.chat.id][0]}\n{arr[msg.chat.id][1]}\n{arr[msg.chat.id][2]}", reply_markup=markup)
    else:
        bot.send_message(msg.chat.id, 'Неправльный формат почты, введите снова:')
        bot.register_next_step_handler(msg, foth_step)

@bot.callback_query_handler(func=lambda call: call.data == "continueForm")
def but(call: types.CallbackQuery):

    try:
        cursor.execute(
            f"INSERT INTO users (`userid`, `name`, `phone`, `mail`) VALUES (  '{encode(str(call.message.chat.id))}', "
                                                                            f"'{encode(arr[call.message.chat.id][0])}', "
                                                                            f"'{encode(arr[call.message.chat.id][1])}', "
                                                                            f"'{encode(arr[call.message.chat.id][2])}');")
        cnx.commit()
    except BaseException as ex:
        print(ex)
    else:
        bot.send_message(call.message.chat.id, "Всё прошло успешно!")



if __name__ == '__main__':
    bot.infinity_polling()

