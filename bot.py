#  __  __      ____       __  __      _____       ______    ______      __  __      ____
# /\ \/\ \    /\  _`\    /\ \/\ \    /\  __`\    /\__  _\  /\__  _\    /\ \/\ \    /\  _`\
# \ \ `\\ \   \ \ \L\_\  \ \ \/'/'   \ \ \/\ \   \/_/\ \/  \/_/\ \/    \ \ `\\ \   \ \ \L\_\
#  \ \ , ` \   \ \  _\L   \ \ , <     \ \ \ \ \     \ \ \     \ \ \     \ \ , ` \   \ \  _\L
#   \ \ \`\ \   \ \ \L\ \  \ \ \\`\    \ \ \_\ \     \ \ \     \_\ \__   \ \ \`\ \   \ \ \L\ \
#    \ \_\ \_\   \ \____/   \ \_\ \_\   \ \_____\     \ \_\    /\_____\   \ \_\ \_\   \ \____/
#     \/_/\/_/    \/___/     \/_/\/_/    \/_____/      \/_/    \/_____/    \/_/\/_/    \/___/
#
# BOT BY AKD

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot import types
from telebot.apihelper import ApiTelegramException
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter, StateFilter, IsDigitFilter

import json
import sqlite3
import math
import asyncio


from config import token, adminlist, nekomanager, nekotineShop
import textbook


con = sqlite3.connect('users.db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users( userid TEXT PRIMARY KEY, refs INT );")
con.commit()
bot = AsyncTeleBot(token, state_storage=StateMemoryStorage())

class States(StatesGroup):
    user = State()
    userCatalog = State()
    adminka = State()
    adding_uid = State()
    adding_name = State()
    adding_desc = State()
    adding_quan = State()
    adding_price = State()
    adding_pic = State()
    seeking = State()
    deleting = State()
    selling = State()
    adding = State()
    banning = State()
    unbanning = State()

async def userExists(uid):
    cur.execute('SELECT COUNT (userid) FROM users WHERE userid = ?', (str(uid),))
    # print(cur.fetchone())
    if cur.fetchone()[0] == 0:
        cur.fetchall()
        return False
    else:
        print("user %s exists"%str(uid))
        cur.fetchall()
        return True


async def userReg(uid):
    print("user %s registered"%str(uid))
    cur.execute("INSERT INTO users VALUES (?, 0)", [str(uid)])
    con.commit()

async def checkSub(uid):
    try:
        await bot.get_chat_member(nekotineShop, uid)
        return True
    except ApiTelegramException as e:
        if e.result_json['description'] == 'Bad Request: user not found':
            return False

@bot.message_handler(commands=['start'])
async def start(msg):
    if " " in msg.text:
        print("space found")
        print(await userExists(msg.text.split()[1]), await userExists(msg.chat.id), await checkSub(msg.chat.id))
        if await userExists(msg.text.split()[1]) and not await userExists(msg.chat.id) and await checkSub(int(msg.from_user.id)):
            if not await userExists(msg.chat.id):
                await userReg(msg.chat.id)
            print("ref user exists")
            await addRef(msg.text.split()[1], 1)
            await addRef(msg.chat.id, 4)
            await bot.set_state(msg.from_user.id, States.user, msg.chat.id)
            await bot.send_message(msg.chat.id, textbook.refGood)
            await bot.send_message(msg.chat.id, textbook.greeting)
            await bot.send_photo(msg.chat.id, "AgACAgIAAxkBAAIC3WKXw7sbLPRAY53POp2JqmNaZ7a6AAL_vzEbekS5SMpX7N-w2loJAQADAgADcwADJAQ", "Ты в главном меню", reply_markup=mainMenu())
        else:
            await bot.send_message(msg.chat.id, textbook.refWrong)
    else:
        if not await userExists(msg.chat.id):
            await userReg(msg.chat.id)
        await bot.set_state(msg.from_user.id, States.user, msg.chat.id)
        await bot.send_message(msg.chat.id, textbook.greeting)
        await bot.send_photo(msg.chat.id, "AgACAgIAAxkBAAIC3WKXw7sbLPRAY53POp2JqmNaZ7a6AAL_vzEbekS5SMpX7N-w2loJAQADAgADcwADJAQ", "Ты в главном меню", reply_markup=mainMenu())



@bot.message_handler(commands=['menu'])
async def menu(msg):
    await bot.send_photo(msg.chat.id, "AgACAgIAAxkBAAIC3WKXw7sbLPRAY53POp2JqmNaZ7a6AAL_vzEbekS5SMpX7N-w2loJAQADAgADcwADJAQ", "Ты в главном меню", reply_markup=mainMenu())

async def getItem(uid):
    with open("prodDB.json", "r") as file:
        file_data = json.load(file)
        for i in range(len(file_data["prod"])):
            if uid == file_data["prod"][i]["uid"]:
                return file_data["prod"][i]
        return None

async def showItem(chatid, uid):
    # data = getItem(uid)
    with open("prodDB.json", "r") as file:
        file_data = json.load(file)
        data = None
        for i in range(len(file_data["prod"])):
            if uid == file_data["prod"][i]["uid"]:
                data = file_data["prod"][i]
    if data:
        await bot.send_photo(chatid, data["pic"], textbook.itemTemplate%(data["name"], data["desc"], str(data["quan"])), parse_mode='html')
    else:
        await bot.send_message(chatid, "Товар не найден")

#  __  __      ____        ____       ____
# /\ \/\ \    /\  _`\     /\  _`\    /\  _`\
# \ \ \ \ \   \ \,\L\_\   \ \ \L\_\  \ \ \L\ \
#  \ \ \ \ \   \/_\__ \    \ \  _\L   \ \ ,  /
#   \ \ \_\ \    /\ \L\ \   \ \ \L\ \  \ \ \\ \
#    \ \_____\   \ `\____\   \ \____/   \ \_\ \_\
#     \/_____/    \/_____/    \/___/     \/_/\/ /





async def isBanned(id):
    with open("user.json", "r") as file:
        file_data = json.load(file)
        if id in file_data["banned"]:
            return True
        else:
            return False

def mainMenu():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text='К каталогу ➡',
                    callback_data='catalog'
                )],
            [
                types.InlineKeyboardButton(
                    text='Рефералка 🤼',
                    callback_data='referalka'
                )],
            [
                types.InlineKeyboardButton(
                    text='Помощь ❓',
                    callback_data='help'
                )
            ]
        ]
    )

def retreiveProducts():
    keyboard = []
    with open("prodDB.json", "r") as file:
        file_data = json.load(file)
        for i in range(len(file_data["prod"])):
            if int(file_data["prod"][i]["quan"]) > 3:
                keyboard.append([
                    types.InlineKeyboardButton(
                        text='✅ %s'%file_data["prod"][i]["name"],
                        callback_data='buy%s'%file_data["prod"][i]["uid"]
                    )
                ])
            elif int(file_data["prod"][i]["quan"]) <= 3 and int(file_data["prod"][i]["quan"]) > 0:
                keyboard.append([
                    types.InlineKeyboardButton(
                        text='⚠️ %s'%file_data["prod"][i]["name"],
                        callback_data='buy%s'%file_data["prod"][i]["uid"]
                    )
                ])
            elif int(file_data["prod"][i]["quan"]) == 0:
                keyboard.append([
                    types.InlineKeyboardButton(
                        text='❌ %s'%file_data["prod"][i]["name"],
                        callback_data='buy%s'%file_data["prod"][i]["uid"]
                    )
                ])
            else:
                keyboard.append([
                    types.InlineKeyboardButton(
                        text='Неизвестный товар (ошибка)',
                        callback_data='catalog'
                    )
                ])
    keyboard.append([
        types.InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data='back'
        ),
        types.InlineKeyboardButton(
            text='Обновить 🔄',
            callback_data='updatecat'
        )
    ])
    return keyboard


def products():
    return types.InlineKeyboardMarkup(keyboard=retreiveProducts())

def buy(uid):
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text='📋 Оформить заказ',
                    callback_data='confirm' + uid
                )
            ],
            [
                types.InlineKeyboardButton(
                    text='⬅️ Назад',
                    callback_data='catalog'
                )
            ]
        ]
    )

def order():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text='⬅️ Назад',
                    callback_data='catalog'
                )
            ]
        ]
    )

def confirm(uid):
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text='✅ Согласен',
                    callback_data='order' + uid
                ),
                types.InlineKeyboardButton(
                    text='❌ Не согласен',
                    callback_data='catalog'
                )
            ]
        ]
    )

def faq():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text='⬅️ Назад',
                    callback_data='back'
                )
            ]
        ]
    )


# A minute of govnokod) --->
async def calcPrice(cid, price):
    data = await getRefs(cid)
    return str(int((1 - (math.ceil(math.sqrt(float(data[0])))) * 0.01) * float(price)))
# Govnokod ends here <---

async def findProduct(uid):
    with open("prodDB.json", "r") as file:
        file_data = json.load(file)
        for i in range(len(file_data["prod"])):
            if uid == file_data["prod"][i]["uid"]:
                return file_data["prod"][i]

async def userShowItem(cid, mid, uid):
    data = await findProduct(uid)
    await bot.edit_message_media(message_id=mid, chat_id=cid, media=types.InputMediaPhoto(data["pic"]))
    await bot.edit_message_caption(message_id=mid, chat_id=cid, caption=textbook.itemTemplate%(data["name"], data["desc"], str(data["quan"]), str(data["price"]), await calcPrice(cid, data["price"])), parse_mode='html', reply_markup=buy(uid))


@bot.callback_query_handler(func=lambda c: c.data == 'catalog' or c.data == 'updatecat')
async def catalog_callback(call: types.CallbackQuery):
    await bot.set_state(call.message.from_user.id, States.userCatalog, call.message.chat.id)
    await bot.edit_message_media(message_id=call.message.message_id, chat_id=call.message.chat.id, media=types.InputMediaPhoto("AgACAgIAAxkBAAICBGKXoYvnmX2qdfZikPmm1APVy6zjAAJcvzEbekS5SLD1c25_NVlkAQADAgADcwADJAQ"))
    await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption='Каталог продуктов:', reply_markup=products())


@bot.callback_query_handler(func=lambda c: c.data == 'back')
async def back_callback(call: types.CallbackQuery):
    await bot.edit_message_media(message_id=call.message.message_id, chat_id=call.message.chat.id, media=types.InputMediaPhoto("AgACAgIAAxkBAAIC3WKXw7sbLPRAY53POp2JqmNaZ7a6AAL_vzEbekS5SMpX7N-w2loJAQADAgADcwADJAQ"))
    await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          caption='Ты в главном меню', reply_markup=mainMenu())

@bot.callback_query_handler(func=lambda c: c.data == 'help')
async def help_callback(call: types.CallbackQuery):
    await bot.edit_message_media(message_id=call.message.message_id, chat_id=call.message.chat.id, media=types.InputMediaPhoto("AgACAgIAAxkBAAIDDmKXy3nuW9Fp543TXS1258TyN6wXAAIdwDEbekS5SGVfM01L1fsPAQADAgADcwADJAQ"))
    await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          caption=textbook.faq, reply_markup=faq(), parse_mode='html')
# TODO: Доделоть
@bot.callback_query_handler(func=lambda c: c.data[0:3] == 'buy')
async def buy_callback(call: types.CallbackQuery):
    await userShowItem(call.message.chat.id, call.message.message_id, call.data[3:])

@bot.callback_query_handler(func=lambda c: c.data[0:7] == 'confirm')
async def confirm_callback(call: types.CallbackQuery):
    # await bot.edit_message_media(message_id=call.message.message_id, chat_id=call.message.chat.id, media=types.InputMediaPhoto("AgACAgIAAxkBAAIDymKX5AaT20TZJN0z53oXNfsbOey3AAJiwTEbekS5SFMlXyL_QSFSAQADAgADcwADJAQ"))
    if not await isBanned(str(call.message.chat.id)):
        print("test")
        await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=textbook.orderConfirm, reply_markup=confirm(call.data[7:]))
    else:
        await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          caption=textbook.banned, reply_markup=order())

async def getPrice(cid, uid):
    data = await getRefs(cid)
    return data[0]

@bot.callback_query_handler(func=lambda c: c.data[0:5] == 'order')
async def order_callback(call: types.CallbackQuery):
    await bot.edit_message_media(message_id=call.message.message_id, chat_id=call.message.chat.id, media=types.InputMediaPhoto("AgACAgIAAxkBAAIDymKX5AaT20TZJN0z53oXNfsbOey3AAJiwTEbekS5SFMlXyL_QSFSAQADAgADcwADJAQ"))
    await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=textbook.orderReceived, reply_markup=order())
    await bot.send_message(nekomanager, textbook.nekomangerOrder%(call.from_user.first_name, call.data[5:], str(await getPrice(call.from_user.id, call.data[5:])), call.from_user.username, call.message.chat.id))
    print("test2")



#  ______      ____                   ______      __  __
# /\  _  \    /\  _`\     /'\_/`\    /\__  _\    /\ \/\ \
# \ \ \L\ \   \ \ \/\ \  /\      \   \/_/\ \/    \ \ `\\ \
#  \ \  __ \   \ \ \ \ \ \ \ \__\ \     \ \ \     \ \ , ` \
#   \ \ \/\ \   \ \ \_\ \ \ \ \_/\ \     \_\ \__   \ \ \`\ \
#    \ \_\ \_\   \ \____/  \ \_\\ \_\    /\_____\   \ \_\ \_\
#     \/_/\/_/    \/___/    \/_/ \/_/    \/_____/    \/_/\/_/
#


async def banUser(id):
    with open("user.json", "r+") as file:
        file_data = json.load(file)
        file_data["banned"].append(id)
        file.seek(0)
        json.dump(file_data, file, indent=4)

async def unbanUser(id):
    with open("user.json", "r") as file:
        file_data = json.load(file)
    with open("user.json", "w") as file:
        file_data["banned"].remove(str(id))
        # print("deleting %s with data:\n%s"%(str(pos), str(file_data["prod"][pos])))
        file.seek(0)
        json.dump(file_data, file, indent=4)


async def writeItem(data):
    print("Got %s"%str(data))
    with open("prodDB.json", "r+") as file:
        file_data = json.load(file)
        file_data["prod"].append(data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

async def deleteItem(uid):
    pos = -1
    with open("prodDB.json", "r") as file:
        file_data = json.load(file)
        for i in range(len(file_data["prod"]) - 1):
            if uid == file_data["prod"][i]["uid"]:
                pos = i
    if pos != -1:
        with open("prodDB.json", "w") as file:
            file_data["prod"].pop(pos)
            print("deleting %s with data:\n%s"%(str(pos), str(file_data["prod"][pos])))
            file.seek(0)
            json.dump(file_data, file, indent=4)

async def sellItem(data):
    pos = -1
    with open("prodDB.json", "r") as file:
        file_data = json.load(file)
        for i in range(len(file_data["prod"])):
            if data[0] == file_data["prod"][i]["uid"]:
                pos = i
    if pos != -1:
        with open("prodDB.json", "w") as file:
            file_data["prod"][pos]["quan"] = str(int(file_data["prod"][pos]["quan"]) - int(data[1]))
            print("selling %s by %s"%(data[0], data[1]))
            file.seek(0)
            json.dump(file_data, file, indent=4)

async def addItem(data):
    pos = -1
    with open("prodDB.json", "r") as file:
        file_data = json.load(file)
        for i in range(len(file_data["prod"])):
            if data[0] == file_data["prod"][i]["uid"]:
                pos = i
    if pos != -1:
        with open("prodDB.json", "w") as file:
            file_data["prod"][pos]["quan"] = str(int(file_data["prod"][pos]["quan"]) + int(data[1]))
            print("selling %s by %s"%(data[0], data[1]))
            file.seek(0)
            json.dump(file_data, file, indent=4)


@bot.message_handler(commands=['adminpanel'])
async def adminpanel(msg):
    if msg.from_user.id in adminlist:
        await bot.set_state(msg.from_user.id, States.adminka, msg.chat.id)
        await bot.send_message(msg.chat.id, textbook.adminGreeting)
    else:
        await bot.send_message(msg.chat.id, "¯\_(ツ)_/¯")
        await bot.send_message(msg.chat.id, str(msg.chat.id))

@bot.message_handler(state=States.adminka, commands=['adminexit'])
async def adminexit(msg):
    await bot.set_state(msg.from_user.id, States.user, msg.chat.id)
    await bot.send_message(msg.chat.id, textbook.adminExit)

@bot.message_handler(state=States.adminka, commands=['findbyuid'])
async def findbyuid(msg):
    await bot.set_state(msg.from_user.id, States.seeking, msg.chat.id)
    await bot.send_message(msg.chat.id, "Введите код товара")

@bot.message_handler(state=States.seeking)
async def seek(msg):
    await bot.set_state(msg.from_user.id, States.adminka, msg.chat.id)
    print("State is seeking")
    async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        await showItem(msg.chat.id, msg.text)

@bot.message_handler(state=States.adminka, commands=['delitem'])
async def delitem(msg):
    await bot.set_state(msg.from_user.id, States.deleting, msg.chat.id)
    await bot.send_message(msg.chat.id, "Введите код товара")

@bot.message_handler(state=States.deleting)
async def delstep(msg):
    await bot.set_state(msg.from_user.id, States.adminka, msg.chat.id)
    async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        await deleteItem(msg.text)
    await bot.send_message(msg.chat.id, "Товар с данным кодом удален")

@bot.message_handler(state=States.adminka, commands=['sellitem'])
async def sellitem(msg):
    await bot.set_state(msg.from_user.id, States.selling, msg.chat.id)
    await bot.send_message(msg.chat.id, "Введите код товара и сколько продано (напр. <hqdcuvie 2>)")

@bot.message_handler(state=States.selling)
async def sellstep(msg):
    await bot.set_state(msg.from_user.id, States.adminka, msg.chat.id)
    async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        await sellItem(msg.text.split())
    await bot.send_message(msg.chat.id, "Продано")

@bot.message_handler(state=States.adminka, commands=['additem'])
async def additem(msg):
    await bot.set_state(msg.from_user.id, States.adding, msg.chat.id)
    await bot.send_message(msg.chat.id, "Введите код товара и сколько нужно добавить (напр. <hqdcuvie 2>)")

@bot.message_handler(state=States.adding)
async def addstep(msg):
    await bot.set_state(msg.from_user.id, States.adminka, msg.chat.id)
    async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        await addItem(msg.text.split())
    await bot.send_message(msg.chat.id, "Добавлено")

@bot.message_handler(state=States.adminka, commands=['newitem'])
async def additem(msg):
    await bot.set_state(msg.from_user.id, States.adding_uid, msg.chat.id)
    await bot.send_message(msg.chat.id, "Введите уникальный код товара (без пробелов, на английском, напр hqd1200, elfbar3000)")

@bot.message_handler(state=States.adding_uid)
async def uidstep(msg):
    await bot.set_state(msg.from_user.id, States.adding_name, msg.chat.id)
    await bot.send_message(msg.chat.id, "Введите название товара")
    async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data['uid'] = msg.text

@bot.message_handler(state=States.adding_name)
async def namestep(msg):
    await bot.set_state(msg.from_user.id, States.adding_desc, msg.chat.id)
    await bot.send_message(msg.chat.id, "Введите описание товара")
    async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data['name'] = msg.text

@bot.message_handler(state=States.adding_desc)
async def descstep(msg):
    await bot.set_state(msg.from_user.id, States.adding_quan, msg.chat.id)
    await bot.send_message(msg.chat.id, "Введите количество товара")
    async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data['desc'] = msg.text

@bot.message_handler(state=States.adding_quan)
async def quanstep(msg):
    if msg.text.isdigit():
        await bot.set_state(msg.from_user.id, States.adding_price, msg.chat.id)
        await bot.send_message(msg.chat.id, "Введите цену (в рублях, ЦИФРОЙ БЛЯТЬ)")
        async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
            data['quan'] = msg.text
    else:
        await bot.send_message(msg.chat.id, "ТЫ БЛЯТЬ УЕБОК КОНЧЕНЫЙ, СУКА, ЧИСЛО БЛЯТЬ НАПИШИ, ЕБАНЫЙ ТВОЙ РОТЕШНИК")

@bot.message_handler(state=States.adding_price)
async def pricestep(msg):
    if msg.text.isdigit():
        await bot.set_state(msg.from_user.id, States.adding_pic, msg.chat.id)
        await bot.send_message(msg.chat.id, "Загрузите картинку товара")
        async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
            data['price'] = msg.text
    else:
        await bot.send_message(msg.chat.id, "ТЫ БЛЯТЬ УЕБОК КОНЧЕНЫЙ, СУКА, ЧИСЛО БЛЯТЬ НАПИШИ, ЕБАНЫЙ ТВОЙ РОТЕШНИК")

@bot.message_handler(state=States.adding_pic, content_types=["photo"])
async def picstep(msg):
    await bot.set_state(msg.from_user.id, States.adminka, msg.chat.id)
    await bot.send_message(msg.chat.id, "Товар добавлен")
    async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data['pic'] = msg.photo[0].file_id
    await writeItem(data)
    print("State is adding_pic")
    await showItem(msg.chat.id, data['uid'])

@bot.message_handler(state=States.adding_pic, content_types=["text"])
async def notpic(msg):
    await bot.send_message(msg.chat.id, "Это не фото")

@bot.message_handler(state=States.adminka, commands=['ban'])
async def ban(msg):
    await bot.set_state(msg.from_user.id, States.banning, msg.chat.id)
    await bot.send_message(msg.chat.id, "Введите айдишник пользователя (UserId)")

@bot.message_handler(state=States.banning)
async def banning_step(msg):
    await bot.set_state(msg.from_user.id, States.adminka, msg.chat.id)
    await bot.send_message(msg.chat.id, "Пользователь забанен")
    async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        await banUser(msg.text)

@bot.message_handler(state=States.adminka, commands=['unban'])
async def unban(msg):
    await bot.set_state(msg.from_user.id, States.unbanning, msg.chat.id)
    await bot.send_message(msg.chat.id, "Введите айдишник пользователя (UserId)")

@bot.message_handler(state=States.unbanning)
async def unbanning_step(msg):
    await bot.set_state(msg.from_user.id, States.adminka, msg.chat.id)
    await bot.send_message(msg.chat.id, "Пользователь разбанен")
    async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        await unbanUser(msg.text)

#  ________  _______   ________ _______   ________  ________  ___
# |\   __  \|\  ___ \ |\  _____\\  ___ \ |\   __  \|\   __  \|\  \
# \ \  \|\  \ \   __/|\ \  \__/\ \   __/|\ \  \|\  \ \  \|\  \ \  \
#  \ \   _  _\ \  \_|/_\ \   __\\ \  \_|/_\ \   _  _\ \   __  \ \  \
#   \ \  \\  \\ \  \_|\ \ \  \_| \ \  \_|\ \ \  \\  \\ \  \ \  \ \  \____
#    \ \__\\ _\\ \_______\ \__\   \ \_______\ \__\\ _\\ \__\ \__\ \_______\
#     \|__|\|__|\|_______|\|__|    \|_______|\|__|\|__|\|__|\|__|\|_______|

def createref():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text='⬅️ Назад',
                    callback_data='catalog'
                )
            ]
        ]
    )

async def addRef(userid, rcount):
    con.execute("UPDATE \"users\" SET \"refs\" = \"refs\" + ? WHERE \"userid\" = ?", (rcount, str(userid)))
    con.commit()

async def getRefs(userid):
    cur.execute("SELECT (refs) FROM users WHERE userid = ?", (str(userid),))
    return cur.fetchone()

async def refList(userid):
    data = await getRefs(userid)
    return ("https://t.me/NEKOTINE_BOT?start=%s"%str(userid), str(data[0]), str(math.ceil(math.sqrt(float(data[0])))))

@bot.callback_query_handler(func=lambda c: c.data == 'referalka')
async def referalka_callback(call: types.CallbackQuery):
    await bot.edit_message_media(message_id=call.message.message_id, chat_id=call.message.chat.id, media=types.InputMediaPhoto("AgACAgIAAxkBAAIBo2Kkafhz_lBlfYjmhm-vdFA34KM4AALfvDEbr9EgSTH-QVczjOK5AQADAgADcwADJAQ"))
    await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          caption=textbook.referalka%await refList(call.message.chat.id), reply_markup=faq(), parse_mode='html')


bot.add_custom_filter(StateFilter(bot))
bot.add_custom_filter(IsDigitFilter())
# bot.add_custom_filter(ProductsCallbackFilter())
print("Bot started")
asyncio.run(bot.polling())
