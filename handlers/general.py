from aiogram import types, Dispatcher
import string
import json


# @dp.message_handler()
async def censored(message: types.Message):
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')}\
            .intersection(set(json.load(open('cenz.json')))) != set():
        await message.reply('Маты запрещены!!!')
        await message.delete()


def register_handler_general(dp: Dispatcher):
    dp.register_message_handler(censored)
