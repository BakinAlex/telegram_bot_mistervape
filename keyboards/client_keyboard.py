from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

button_info = KeyboardButton('О нас и наших услугах')
button_product_catalog = KeyboardButton('Каталог товаров')
button_basket = KeyboardButton('Корзина')
button_ordering = KeyboardButton('Оформление заказа')
# button_req_contact = KeyboardButton('Предоставить номер телефона', request_contact=True)
# button_req_location = KeyboardButton('Показать геолокацию', request_location=True)

client_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True
)
rm_client_keyboard = ReplyKeyboardRemove()

client_keyboard.row(button_product_catalog, button_info).row(button_basket, button_ordering)
