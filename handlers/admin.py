from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.types import ParseMode
from create_bot import bot
from aiogram.dispatcher.filters import Text
from keyboards.admin_keyboard import admin_keyboard
from keyboards.client_keyboard import client_keyboard
from database.mysql_db import sql_download_data, sql_name_output, sql_flavor_output, \
    sql_delete_data, sql_add_data
from inline_keyboards.admin_inline_keyboards import download_admin_inline_keyboard, \
    delete_admin_inline_keyboard_category


# ID = 866208827
ID = None
CHAT_ID_ONE = '-800045983'
CHAT_ID_TWO = '-819963667'


class FSMAdmin(StatesGroup):

    photo = State()
    name = State()
    description = State()
    price = State()
    flavor = State()
    download_call_back = None


class FSMAdminDel(StatesGroup):

    category = State()
    name = State()
    flavor = State()


class FSMAdminAdd(StatesGroup):

    category = State()
    name = State()
    flavor = State()


# @dp.message_handler(Text(equals='модератор', ignore_case=True), is_chat_admin=True)
async def access_right(message: types.Message, state: FSMContext):
    global CHAT_ID_ONE, CHAT_ID_TWO
    if message.chat.id == CHAT_ID_ONE or CHAT_ID_TWO:
        global ID
        ID = message.from_user.id
        me = await bot.get_me()
        await bot.send_message(ID, '*Доступ разрешен!*\n'
                                   f'Бот, {me.full_name}, к вашим услугам!',
                                   reply_markup=admin_keyboard,
                                   parse_mode=ParseMode.MARKDOWN)
        await message.delete()
    else:
        await message.answer('Извините, но у вас нет доступа к данной функции.\n'
                             'Если вам необходим доступ к данной функции, обратитесь к владельцу бота.',
                             parse_mode=ParseMode.MARKDOWN)
        await message.delete()


# @dp.message_handler(Text(equals='снять', ignore_case=True), is_chat_admin=True,)
async def revocation_right(message: types.Message, state: FSMContext):
    if state:
        await state.finish()
    global ID
    ID = None
    await bot.send_message(message.from_user.id,
                           '*Уведомляю* вас о том, что ваши *права доступа были сняты!*',
                           reply_markup=client_keyboard,
                           parse_mode=ParseMode.MARKDOWN)
    await message.delete()


# @dp.message_handler(Text(equals='Загрузить', ignore_case=True))
async def selecting_download_category(message: types.Message):
    if message.from_user.id == ID:
        await message.answer('Выберите категорию:',
                             reply_markup=download_admin_inline_keyboard)
    else:
        await message.answer('Извините, но у вас нет доступа к данной функции.\n'
                             '*Данная функция доступна только администраторам.*\n'
                             'Если вам необходим доступ к данной функции, обратитесь к владельцу бота.',
                             parse_mode=ParseMode.MARKDOWN)
        await message.delete()


# @dp.callback_query_handler(text='electronic_cigarettes_admin_download')
# @dp.callback_query_handler(text='liquid_admin_download')
async def loading_product_data(callback: types.CallbackQuery):
    if callback.from_user.id == ID:
        FSMAdmin.download_call_back = callback.data[:callback.data.find("_admin")]
        await FSMAdmin.photo.set()
        await callback.message.answer('Загрузите фотографию позиции...')
        await callback.answer()


# @dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def loading_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        await FSMAdmin.next()
        await message.answer('Введите название позиции...')


# @dp.message_handler(state=FSMAdmin.name)
async def enter_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        # try:
        #     pass
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await message.answer('Введите описание позиции...')


# @dp.message_handler(state=FSMAdmin.description)
async def enter_description(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['description'] = message.text
        await FSMAdmin.next()
        await message.answer('Введите цену позиции...')


# @dp.message_handler(state=FSMAdmin.price)
async def enter_price(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['price'] = int(message.text)
        await FSMAdmin.next()
        await message.answer('Введите вкус позиции...')


# @dp.message_handler(state=FSMAdmin.flavor)
async def enter_flavor(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['flavor'] = message.text
        await sql_download_data(state, FSMAdmin.download_call_back, message)
        await state.finish()


# @dp.message_handler(commands=['отмена'], state='*')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_download(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            await message.answer('Операция с данными не производилась!')
            return
        await state.finish()
        await message.answer('Операция приостановлена!')


# @dp.message_handler(Text(equals='Добавить', ignore_case=True))
async def selecting_add_category(message: types.Message):
    if message.from_user.id == ID:
        await message.answer('Выберите категорию:',
                             reply_markup=download_admin_inline_keyboard)
        await FSMAdminAdd.category.set()
    else:
        await message.answer('Извините, но у вас нет доступа к данной функции.\n'
                             '*Данная функция доступна только администраторам.*\n'
                             'Если вам необходим доступ к данной функции, обратитесь к владельцу бота.',
                             parse_mode=ParseMode.MARKDOWN)
        await message.delete()


# @dp.callback_query_handler(text='electronic_cigarettes_admin_download', state=FSMAdminAdd.category)
# @dp.callback_query_handler(text='liquid_admin_download', state=FSMAdminAdd.category)
async def add_category_data(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id == ID:
        async with state.proxy() as data:
            data['category'] = callback.data[:callback.data.find("_admin")]
        await sql_name_output(callback)
        await FSMAdminAdd.next()
        await callback.answer()


# @dp.callback_query_handler(state=FSMAdminAdd.name)
async def add_name_data(callback: types.CallbackQuery, state: FSMContext):
    if '_name' in callback.data:
        if callback.from_user.id == ID:
            async with state.proxy() as data:
                data['name'] = callback.data[:callback.data.find("_name"):]
            await FSMAdminAdd.next()
            await callback.message.answer('Введите вкус позиции...')
            await callback.answer()


# @dp.message_handler(state=FSMAdminAdd.flavor)
async def add_flavor_data(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['flavor'] = message.text
        await sql_add_data(state, message)
        await state.finish()


# @dp.message_handler(Text(equals='Удалить', ignore_case=True))
async def selecting_delete_category(message: types.Message):
    if message.from_user.id == ID:
        await message.answer('Выберите категорию:',
                             reply_markup=delete_admin_inline_keyboard_category)
        await FSMAdminDel.category.set()
    else:
        await message.answer('Извините, но у вас нет доступа к данной функции.\n'
                             '*Данная функция доступна только администраторам.*\n'
                             'Если вам необходим доступ к данной функции, обратитесь к владельцу бота.',
                             parse_mode=ParseMode.MARKDOWN)
        await message.delete()


# @dp.callback_query_handler(text='electronic_cigarettes_admin_delete', state=FSMAdminDel.category)
# @dp.callback_query_handler(text='liquid_admin_delete', state=FSMAdminDel.category)
async def delete_category_data(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id == ID:
        async with state.proxy() as data:
            data['category'] = callback.data[:callback.data.find("_admin")]
        await sql_name_output(callback)
        await FSMAdminDel.next()
        await callback.answer()


# @dp.callback_query_handler(state=FSMAdminDel.name)
async def delete_name_data(callback: types.CallbackQuery, state: FSMContext):
    if '_name' in callback.data:
        if callback.from_user.id == ID:
            async with state.proxy() as data:
                data['name'] = callback.data[:callback.data.find("_name"):]
            await sql_flavor_output(callback, state, ID)
            await FSMAdminDel.next()
            await callback.answer()


# @dp.callback_query_handler(state=FSMAdminDel.flavor)
async def delete_flavor_data(callback: types.CallbackQuery, state: FSMContext):
    if '_flavor' in callback.data:
        if callback.from_user.id == ID:
            print(callback.data)
            if callback.data != 'all_flavor':
                async with state.proxy() as data:
                    data['flavor'] = callback.data[:callback.data.find("_flavor")]
                    print(callback.data)
            await sql_delete_data(state, callback)
            await state.finish()
            await callback.answer()


def register_handler_admin(dp: Dispatcher):
    dp.register_message_handler(access_right, Text(equals='модератор', ignore_case=True), is_chat_admin=True)
    dp.register_message_handler(revocation_right, Text(equals='снять', ignore_case=True), is_chat_admin=True)
    dp.register_message_handler(selecting_download_category, Text(equals='Загрузить', ignore_case=True), state='*')
    dp.register_message_handler(selecting_add_category, Text(equals='Добавить', ignore_case=True))
    dp.register_message_handler(selecting_delete_category, Text(equals='Удалить', ignore_case=True))
    dp.register_message_handler(cancel_download, commands=['отмена'], state='*')
    dp.register_message_handler(cancel_download, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_callback_query_handler(loading_product_data, text='electronic_cigarettes_admin_download')
    dp.register_callback_query_handler(loading_product_data, text='liquid_admin_download')
    dp.register_message_handler(loading_photo, content_types=['photo'], state=FSMAdmin.photo)
    dp.register_message_handler(enter_name, state=FSMAdmin.name)
    dp.register_message_handler(enter_description, state=FSMAdmin.description)
    dp.register_message_handler(enter_price, state=FSMAdmin.price)
    dp.register_message_handler(enter_flavor, state=FSMAdmin.flavor)
    dp.register_callback_query_handler(
        add_category_data, text='electronic_cigarettes_admin_download', state=FSMAdminAdd.category
    )
    dp.register_callback_query_handler(
        add_category_data, text='liquid_admin_download', state=FSMAdminAdd.category
    )
    dp.register_callback_query_handler(add_name_data, state=FSMAdminAdd.name)
    dp.register_message_handler(add_flavor_data, state=FSMAdminAdd.flavor)
    dp.register_callback_query_handler(
        delete_category_data, text='electronic_cigarettes_admin_delete', state=FSMAdminDel.category
    )
    dp.register_callback_query_handler(
        delete_category_data, text='liquid_admin_delete', state=FSMAdminDel.category
    )
    dp.register_callback_query_handler(delete_name_data, state=FSMAdminDel.name)
    dp.register_callback_query_handler(delete_flavor_data, state=FSMAdminDel.flavor)
