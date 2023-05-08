from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

client_inline_keyboard = InlineKeyboardMarkup(row_width=1)
button_electronic_cigarettes = InlineKeyboardButton(text='Электронные сигареты',
                                                    callback_data='electronic_cigarettes')
button_liquid = InlineKeyboardButton(text='Жидкости',
                                     callback_data='liquid')
client_inline_keyboard.row(button_electronic_cigarettes, button_liquid)

