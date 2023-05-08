from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

button_download = KeyboardButton('Загрузить')
button_delete = KeyboardButton('Удалить')
button_add = KeyboardButton('Добавить')
button_cancel = KeyboardButton('Отмена')
admin_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True
)
rm_admin_keyboard = ReplyKeyboardRemove()

admin_keyboard.row(button_download, button_add, button_delete).add(button_cancel)
