from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.client_keyboard import client_keyboard
from aiogram.dispatcher.filters import Text
from inline_keyboards.client_inline_keyboards import client_inline_keyboard
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from create_bot import bot
from aiogram.types import ParseMode
from database.mysql_db import sql_name_output, sql_flavor_output, sql_product_output, \
    sql_adding_data_to_cart, content_basket, delete_data_basket, order_data, place_order_output_data


# import logging
# import time

class FSMClient(StatesGroup):
    category = State()
    name = State()
    flavor = State()
    quantity = State()
    price = None
    recipient = State()
    address = State()


# @dp.message_handler(commands=['start', 'help'])
async def start_handlers(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    print(user_name, user_id)
    # user_full_name = message.from_user.full_name
    # logging.info(f'{user_id} {user_full_name} {time.asctime()}')
    # await sql_adding_user_data_at_startup(user_id, user_name)
    await message.answer(f'Здравствуйте! Чем могу помочь?', reply_markup=client_keyboard)
    await message.delete()


# @dp.message_handler(Text(equals='О нас и наших услугах', ignore_case=True), state='*')
async def info(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.answer('Владелец: @ne_angel_reklama\n'
                         'Если вы нашли этого бота😎то вам очень 🍀\n'
                         'здесь вы найдете качественные сигареты по минимальной цене 🤠\n'
                         'доставка в пределах посёлка бесплатно.\n'
                         'Отправка в любую точку нашей необъятной родины ☺️',)
    await message.delete()


# @dp.message_handler(Text(equals='Каталог товаров', ignore_case=True), state='*')
async def product_catalog(message: types.Message):
    await message.answer('Выберите категорию:',
                         reply_markup=client_inline_keyboard)

    await FSMClient.category.set()


# @dp.callback_query_handler(text='electronic_cigarettes', state=FSMClient.category)
# @dp.callback_query_handler(text='liquid', state=FSMClient.category)
async def category(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = callback.data
    print(callback.data)
    await sql_name_output(callback)
    await FSMClient.next()
    await callback.answer()


# @dp.callback_query_handler(state=FSMClient.name)
async def name(callback: types.CallbackQuery, state: FSMContext):
    if '_name' in callback.data:
        async with state.proxy() as data:
            data['name'] = callback.data[:callback.data.find("_name"):]
        await sql_flavor_output(callback, state)
        await FSMClient.next()
        await callback.answer()


# @dp.callback_query_handler(state=FSMClient.flavor)
async def flavor(callback: types.CallbackQuery, state: FSMContext):
    if '_flavor' in callback.data:
        async with state.proxy() as data:
            data['flavor'] = callback.data[:callback.data.find("_flavor"):]
        await sql_product_output(callback, state)
    else:
        async with state.proxy() as data:
            await callback.message.answer(f'Вы выбрали:\n'
                                          f'Жидкость: *{data["name"]}*, вкус: _{data["flavor"]}_\n'
                                          f'Введите необходимое количество товара...',
                                          parse_mode=ParseMode.MARKDOWN)
        await FSMClient.next()
    await callback.answer()


# @dp.callback_query_handler(text='add_to_cart', state=FSMClient.quantity)
async def add_to_cart(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.message.answer(f'Вы выбрали жидкость: {data["name"]}, вкус: {data["flavor"]}\n'
                                      f'Введите необходимое количество товара...')
    await FSMClient.next()


# @dp.message_handler(state=FSMClient.quantity)
async def adding_data_to_cart(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            data['quantity'] = int(message.text)
            print(data)
        await sql_adding_data_to_cart(message, state)
        await state.finish()
    else:
        await message.answer('Вы ввели некорректные данные!\n'
                             'Введите необходимое количество товара...')


# @dp.message_handler(Text(equals='Корзина'), state='*')
async def basket(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        print(current_state)
        await state.finish()
    await content_basket(message)


# @dp.callback_query_handler(text='empty_basket')
async def empty_basket(callback: types.CallbackQuery):
    await delete_data_basket(callback)
    await callback.answer()


# @dp.message_handler(Text(equals='Оформление заказа', ignore_case=True), state='*')
async def ordering(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await order_data(message)


# @dp.callback_query_handler(text='place_order')
async def place_order(callback: types.CallbackQuery):
    await bot.edit_message_text(
        'Пожалуйста, введите ваше полное ФИО (фамилию, имя, отчество), '
        'для обеспечения более оперативной связи с вами, '
        'а также быстрой и корректной обработки информации о вашей оплате.',
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
    )
    await FSMClient.recipient.set()


# @dp.message_handler(state=FSMClient.recipient)
async def place_order_recipient(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['recipient'] = message.text
    await message.answer(
        'Также, пожалуйста, укажите адрес доставки для того, чтобы мы могли быстро и точно доставить ваш заказ.\n\n'
        'Пример адреса: г. Москва, ул. Большая Полянка, д.1, кв.10\n\n'
        'Спасибо за понимание!',

    )
    await FSMClient.next()


# @dp.message_handler(state='FSMClient.address')
async def place_order_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
    await message.answer(
        'Пожалуйста, оплатите свой заказ на следующий номер карты: *2202 2021 3226 7596* (*Денис Юрьевич Т.*) '
        'или по номеру телефона: *8 (928) 470-90-83*. '
        'Также, после оплаты, пожалуйста, нажмите на кнопку "Оплатил" для подтверждения оплаты и начала обработки '
        'Вашего заказа.\n\n'
        'Если у Вас возникнут какие-либо вопросы, пожалуйста, не стесняйтесь связаться с нами по телефону: '
        '8(928)470-90-83.\n\n'
        'Спасибо за Ваш заказ и доверие к нам!',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('Оплатил 💰', callback_data='paid')
        )
    )


# @dp.callback_query_handler(text='paid', state='FSMClient.address')
async def place_order_data(callback: types.CallbackQuery, state: FSMContext):
    await place_order_output_data(callback, state)
    await callback.answer()
    await state.finish()


def register_handler_client(dp: Dispatcher):
    dp.register_message_handler(start_handlers, commands=['start', 'help'])
    dp.register_message_handler(info, Text(equals='О нас и наших услугах', ignore_case=True), state='*')
    dp.register_message_handler(product_catalog, Text(equals='Каталог товаров', ignore_case=True), state='*')
    dp.register_callback_query_handler(category, text='electronic_cigarettes', state=FSMClient.category)
    dp.register_callback_query_handler(category, text='liquid', state=FSMClient.category)
    dp.register_callback_query_handler(name, state=FSMClient.name)
    dp.register_callback_query_handler(flavor, state=FSMClient.flavor)
    dp.register_callback_query_handler(add_to_cart, text='add_to_cart', state=FSMClient.flavor)
    dp.register_message_handler(adding_data_to_cart, state=FSMClient.quantity)
    dp.register_message_handler(basket, Text(equals='Корзина', ignore_case=True), state='*')
    dp.register_callback_query_handler(empty_basket, text='empty_basket')
    dp.register_message_handler(ordering, Text(equals='Оформление заказа', ignore_case=True), state='*')
    dp.register_callback_query_handler(place_order, text='place_order')
    dp.register_message_handler(place_order_recipient, state=FSMClient.recipient)
    dp.register_message_handler(place_order_address, state=FSMClient.address)
    dp.register_callback_query_handler(place_order_data, text='paid', state=FSMClient.address)


# @dp.message_handler(content_types=['contact'])
# async def contact(message: types.Message):
#     phone = message.contact.phone_number
#     await message.answer('PhoneNumber')
#     await message.answer(phone)

