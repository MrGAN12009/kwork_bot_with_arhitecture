import telebot
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import mysql.connector
import csv
import time
import os



with open('conf_server.json', 'r') as f:
    conf = json.load(f)

#mysql connect
cnx = mysql.connector.connect(user = conf["user"], password = conf["password"], host = conf["host"], database = conf["database"])
cursor = cnx.cursor()

def check():
    global cnx, cursor
    if cnx.is_connected():
        return True
    try:
        cnx = mysql.connector.connect(user=conf["user"], password=conf["password"], host=conf["host"],
                                      database=conf["database"])
        cursor = cnx.cursor()
        return True
    except BaseException as ex:
        bot.send_message(ADMIN_ID, f"Произошла ошибка с подключением к базе данных:\n{ex}")
        return False


#bot token
token = conf["TOKEN"]
bot = telebot.TeleBot(token)
#необходимые переменные
arr = {}
ADMIN_ID = int(conf["ADMIN_ID"])
#513773161
s = []
stek = ''


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


#start отработчик
@bot.message_handler(commands = ["start", "about", "sales", "problem", "extendwarr"])
def start(message):
    if check() == False:
        return
    cursor.execute(f"SELECT userid FROM spam WHERE userid = '{message.chat.id}'")
    if cursor.fetchone() == None:
        cursor.execute(f"INSERT INTO spam (`userid`) VALUES ('{str(message.chat.id)}')")
        cnx.commit()
    markup = InlineKeyboardMarkup()
    for i in file[message.text[1::]]['btns']:
        if file[message.text[1::]]["type"] == "url":
            markup.add(InlineKeyboardButton(f"{file[message.text[1::]]['btns'][i][0]}", url=f"{file[message.text[1::]]['btns'][i][1]}"))
        else:
            markup.add(InlineKeyboardButton(f"{file[message.text[1::]]['btns'][i][0]}",
                                            callback_data=f"{file[message.text[1::]]['btns'][i][1]}"))

    if message.chat.id == ADMIN_ID:
        markup.add(InlineKeyboardButton(f"Изменить сообщение", callback_data=f"{message.text[1:]}_new"))
    if message.text != "/start":
        markup.add(InlineKeyboardButton(f"Главная", callback_data="start"))
    if f"{message.text[1:]}.png" in os.listdir("images"):
        bot.send_photo(message.chat.id, photo=open(f"images/{message.text[1:]}.png", 'rb'), caption=f"{file[message.text[1:]]['text']}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text=f"{file[message.text[1:]]['text']}", reply_markup=markup)



#spam target and forms to generate
@bot.message_handler(commands=["help"])
def help(msg):
    if msg.chat.id == ADMIN_ID:
        t = 'start'
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"расслыка", callback_data=f"spam"))
        markup.add(InlineKeyboardButton(f"данные пользователей", callback_data=f"getUserInfo"))
    
        bot.send_message(msg.chat.id, f"Хотите начать расслыку?", reply_markup=markup)


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


@bot.callback_query_handler(func=lambda call: call.data == "getUserInfo")
def but(call: types.CallbackQuery):
    if call.message.chat.id == ADMIN_ID:
        if not check():
            return
        with open('csv.csv', 'w', encoding="UTF-8") as csvfile:
            fieldnames = ['Имя', 'Телефон', 'Почта']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            cursor.execute(f"SELECT name, phone, mail FROM users")
            for i in cursor.fetchall():
                writer.writerow({'Имя': f'{i[0]}', 'Телефон': f'{i[1]}', 'Почта': f'{i[2]}'})

        bot.send_document(ADMIN_ID, open('csv.csv', 'rb'))



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
            if not check():
                return
            markup = InlineKeyboardMarkup()
            for i in spam["btns"]:
                markup.add(InlineKeyboardButton(i.split("-")[0], url=i.split("-")[1]))
            cursor.execute(f"SELECT userid FROM spam")
            for i in cursor.fetchall():
                try:
                    bot.send_photo(str(i).split("'")[1], photo=open('test.png', 'rb'), caption=f"{spam['text']}", reply_markup=markup)
                except BaseException as ex:
                    pass
            bot.send_message(call.message.chat.id, "Отправка окончена!")


@bot.message_handler(commands=["id"])
def id(msg):
    bot.send_message(msg.chat.id, f"{msg.chat.id}")


# ["about", "shop-online", "kontakts", "sales", "extendwarr", "extendWarrSelf", "extendWarrHelp", "problem", "video", "helpspec"]
@bot.callback_query_handler(func=lambda call: call.data in ["start", "about", "shop-online", "kontakts", "sales", "extendwarr", "extendWarrSelf", "extendWarrHelp", "problem", "video", "ansTrue", "ansFalse", "ofStore"])
def but(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    for i in file[call.data]['btns']:
        if file[call.data]["type"] == "url":
            markup.add(InlineKeyboardButton(f"{file[call.data]['btns'][i][0]}", url=f"{file[call.data]['btns'][i][1]}"))
        else:
            markup.add(InlineKeyboardButton(f"{file[call.data]['btns'][i][0]}", callback_data=f"{file[call.data]['btns'][i][1]}"))

    if call.message.chat.id == ADMIN_ID:
        markup.add(InlineKeyboardButton(f"Изменить сообщение", callback_data=f"{call.data}_new"))
        markup.add(InlineKeyboardButton(f"Изменить фото", callback_data=f"{call.data}_newPh"))
        markup.add(InlineKeyboardButton(f"Удалить фото", callback_data=f"{call.data}_removePh"))

        ####back btn
        if call.data in ["ofStore", "shop-online", "kontakts"]:
            markup.add(InlineKeyboardButton("Назад", callback_data="about"))
        elif call.data in ["extendWarrSelf", "extendWarrHelp"]:
            markup.add(InlineKeyboardButton("Назад", callback_data="extendwarr"))
        elif call.data in ["helpSup", "video"]:
            markup.add(InlineKeyboardButton("Назад", callback_data="problem"))

    if call.data != "start":
        markup.add(InlineKeyboardButton(f"Главная", callback_data="start"))

    if f"{call.data}.png" in os.listdir("images"):
        bot.send_photo(call.message.chat.id, photo=open(f"images/{call.data}.png", 'rb'), caption=f"{file[call.data]['text']}", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, text=f"{file[call.data]['text']}", reply_markup=markup)

    if call.data == "video":
        time.sleep(600)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"Да", callback_data=f"ansTrue"))
        markup.add(InlineKeyboardButton(f"Нет", callback_data=f"ansFalse"))
        bot.send_message(call.message.chat.id, text=f"Нам удалось вам помочь?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "helpSup")
def but(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    for i in file[call.data]['btns']:
        if file[call.data]["type"] == "url":
            markup.add(InlineKeyboardButton(f"{file[call.data]['btns'][i][0]}", url=f"{file[call.data]['btns'][i][1]}"))
        else:
            markup.add(InlineKeyboardButton(f"{file[call.data]['btns'][i][0]}", callback_data=f"{file[call.data]['btns'][i][1]}"))
    markup.add(InlineKeyboardButton("политика конфиденциальности", url='https://stoewer.ru/politika-konfidenczialnosti/'))
    if call.message.chat.id == ADMIN_ID:
        markup.add(InlineKeyboardButton(f"Изменить сообщение", callback_data=f"{call.data}_new"))

    markup.add(InlineKeyboardButton("Назад", callback_data="problem"))
    markup.add(InlineKeyboardButton(f"Главная", callback_data="start"))
    bot.send_message(call.message.chat.id, text=f"{file[call.data]['text']}", reply_markup=markup)



@bot.message_handler(content_types=['photo'])
def get_photo_about(message: types.Message):
    if message.chat.id == ADMIN_ID:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(f"images/{stek}.png", 'wb') as new_file:
            new_file.write(downloaded_file)
        editSpamFile()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"Главная", callback_data="start"))
        bot.send_message(message.chat.id, 'Фотография сохранена.', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split("_")[-1] == "newPh")
def dut(call: types.CallbackQuery):
    global stek
    stek = call.data.split("_")[0]
    bot.send_message(ADMIN_ID, "Скиньте новое фото")
    bot.register_next_step_handler(call.message, get_photo_about)
    return


@bot.callback_query_handler(func=lambda call: call.data.split("_")[-1] == "removePh")
def dut(call: types.CallbackQuery):
    if call.message.chat.id == ADMIN_ID:
        os.remove(f"images/{call.data.split('_')[0]}.png")
        bot.send_message(call.message.chat.id, "Фото удалено")
        return


@bot.callback_query_handler(func=lambda call: call.data.split("_")[-1] == "new")
def but(call: types.CallbackQuery):
    # if call.data.split("_")[0] == "ofStorePhoto":
    #     bot.send_message(ADMIN_ID, "Скиньте новое изображение:")
    #     bot.register_next_step_handler(call.message, get_photo_about)
    #     return

    comm = call.data.split('_')[0]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"Текст", callback_data=f"{call.data.split('_')[0]}_text"))

    for i in file[comm]['btns']:
        if file[comm]["type"] == "url":
            markup.add(InlineKeyboardButton(f"текст кнопки - {file[comm]['btns'][i][0]}", callback_data=f"file_{comm}_btns_{i}"))
            markup.add(InlineKeyboardButton(f"путь - {file[comm]['btns'][i][1]}", callback_data=f"file_{comm}_btns_{i}_content"))
        else:
            markup.add(InlineKeyboardButton(f"текст кнопки - {file[comm]['btns'][i][0]}", callback_data=f"file_{comm}_btns_{i}"))
    markup.add(InlineKeyboardButton(f"Главная/отменить изменения", callback_data="start"))
    bot.send_message(call.message.chat.id, text=f"{file[comm]['text']}\n\n\n Что хотите изменить?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "file" or call.data.split('_')[-1] == 'text')
def but(call: types.CallbackQuery):
    global s
    s = call.data.split("_")
    bot.send_message(call.message.chat.id, f"Введите новое значение")
    bot.register_next_step_handler(call.message, edit)


#calls for remake text and urls
def edit(msg):
    if msg.text == "/start":
        start(msg)
        return
    global s
    if len(s) == 2:
        file[s[0]][s[1]] = f"{msg.text}"
    elif len(s) == 4:
        file[s[1]][s[2]][s[3]][0] = f"{msg.text}"

    elif len(s) == 5:
        file[s[1]][s[2]][s[3]][1] = f"{msg.text}"
    editFile()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Главная", callback_data="start"))
    bot.send_message(msg.chat.id, "Данные успешно изменены.", reply_markup=markup)


###form
@bot.callback_query_handler(func=lambda call: call.data == "startForm")
def but(call: types.CallbackQuery):
    if not check():
        return
    cursor.execute(f"SELECT userid FROM users WHERE userid = '{call.message.chat.id}'")
    if cursor.fetchone() != None:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Главная", callback_data="start"))
        markup.add(InlineKeyboardButton("Чат поддержки", url="t.me/stoewerhelp24"))
        bot.send_message(call.message.chat.id, "Ваша заявка отправлена специалисту Stoewer\nС Вами свяжутся в течение 2 рабочих дней\nТакже Вы можете написать нам в чат поддержки и рассказать о проблеме подробно\n", reply_markup=markup)

        cursor.execute(f"SELECT name, phone, mail FROM users WHERE userid = '{call.message.chat.id}'")
        i = cursor.fetchone()
        bot.send_message(ADMIN_ID, f"Поступила заявка!\nИмя : {i[0]}\nТелефон : {i[1]}\nMail : {i[2]}")
    else:
        bot.send_message(call.message.chat.id, f"{file[call.data]['text']}")
        bot.register_next_step_handler(call.message, second_step)


def second_step(msg):
    if msg.text == ('/start'):
        start(msg)
        return
    arr[msg.chat.id] = []
    arr[msg.chat.id].append(msg.text)
    bot.send_message(msg.chat.id, "Введите номер телефона в формате +79хххxxxxxx")
    bot.register_next_step_handler(msg, third_step)


def third_step(msg):
    if msg.text == ('/start'):
        start(msg)
        return
    if msg.text[0] == '+' and len(msg.text) == 12:
        arr[msg.chat.id].append(msg.text)
        bot.send_message(msg.chat.id, "Введите электронную почту в формате helpstoewer@yandex.ru:")
        bot.register_next_step_handler(msg, foth_step)
    elif len(msg.text) == 11:
        arr[msg.chat.id].append(msg.text)
        bot.send_message(msg.chat.id, "Введите электронную почту в формате helpstoewer@yandex.ru:")
        bot.register_next_step_handler(msg, foth_step)
    else:
        bot.send_message(msg.chat.id, "Неправльный формат номера телефона!\nВведите его вновь в формате +79хххxxxxxx:")
        bot.register_next_step_handler(msg, third_step)


def foth_step(msg):
    if msg.text == ('/start'):
        start(msg)
        return
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
    if not check():
        return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Главная", callback_data="start"))
    markup.add(InlineKeyboardButton("Чат поддержки", url="t.me/stoewerhelp24"))
    try:
        cursor.execute(
            f"INSERT INTO users (`userid`, `name`, `phone`, `mail`) VALUES (  '{str(call.message.chat.id)}', "
                                                                            f"'{arr[call.message.chat.id][0]}', "
                                                                            f"'{arr[call.message.chat.id][1]}', "
                                                                            f"'{arr[call.message.chat.id][2]}');")
        cnx.commit()
        bot.send_message(call.message.chat.id, "Ваша заявка отправлена специалисту Stoewer\nС Вами свяжутся в течение 2 рабочих дней\nТакже Вы можете написать нам в чат поддержки и рассказать о проблеме подробно\n", reply_markup=markup)
        bot.send_message(ADMIN_ID, f"Поступила заявка!\nИмя : {arr[call.message.chat.id][0]}\nТелефон : {arr[call.message.chat.id][1]}\nMail : {arr[call.message.chat.id][2]}")
    except BaseException as ex:
        print(ex)
        bot.send_message(call.message.chat.id, "Что-то пошло не так, попробуйте снова позже.", reply_markup=markup)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except BaseException as ex:
            print(ex)

