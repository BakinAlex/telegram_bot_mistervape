import pymysql
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.admin_keyboard import admin_keyboard
import re
from create_bot import bot
from aiogram.types import ParseMode
from datetime import datetime
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

host = os.getenv('HOST')
user = os.getenv('USER_DB')
password = os.getenv('PASSWORD_DB')
name_db = os.getenv('NAME_DB')


def connect_to_database():
    connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=name_db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return connection


try:

    category = ['electronic_cigarettes', 'liquid']
    subcategories = ['electronic_cigarettes_flavor', 'liquid_flavor']


    def sql_start():
        connection = connect_to_database()
        with connection.cursor() as cursor:
            for table in category:
                sql_table = f"""
                CREATE TABLE IF NOT EXISTS {table} (
                img varchar(255) NOT NULL, 
                name varchar(50) NOT NULL PRIMARY KEY, 
                description varchar(255), 
                price int NOT NULL
                )
                """
                cursor.execute(sql_table)
                for table_subcategories in subcategories:
                    if table_subcategories.split('_')[0] in table:
                        sql_table_sub = f"""
                        CREATE TABLE IF NOT EXISTS {table_subcategories} (
                        flavor char(50),
                        {table}_name char(50) REFERENCES {table}(name), 
                        PRIMARY KEY (flavor, {table}_name)
                        )
                        """
                        cursor.execute(sql_table_sub)
            sql_customers = """
            CREATE TABLE IF NOT EXISTS customers (
            id int NOT NULL PRIMARY KEY, 
            name char(50) NOT NULL, 
            user_name char(50) NOT NULL, 
            address char(255) NOT NULL
            )
            """
            cursor.execute(sql_customers)
            sql_orders = """
            CREATE TABLE IF NOT EXISTS orders (
            customers_id int NOT NULL, 
            date DATE NOT NULL, 
            total int NOT NULL
            )
            """
            cursor.execute(sql_orders)
            sql_orders_details = """
            CREATE TABLE IF NOT EXISTS order_details(
            customers_id char(50) NOT NULL, 
            product_name char(50) NOT NULL, 
            flavor char(50) NOT NULL, 
            quantity int NOT NULL, 
            price int NOT NULL)
            """
            cursor.execute(sql_orders_details)
        connection.commit()
except Exception as ex:
    print(f'Connection refused...\n{ex}')


async def sql_add_data(state, message):
    async with state.proxy() as data:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            try:
                sql_flavor = f'INSERT INTO {data["category"]}_flavor (flavor, {data["category"]}_name) VALUES (%s, %s)'
                cursor.execute(sql_flavor, (data['flavor'], data['name']))
                await message.answer(f'Позиция: {data["name"]}\n'
                                     f'Вкус: {data["flavor"]}\n'
                                     f'Данные добавлены!',
                                     reply_markup=admin_keyboard)
                connection.commit()
            except Exception as ex:
                match_one = re.search(r"'(\w+)", str(ex))
                match_two = re.search(r"-([^']+)'", str(ex))
                await message.answer(f'Возникла ошибка: {ex}')
                if "1062" in str(ex):
                    await message.answer(
                        f'Позиция: {match_two.group(1)} \n'
                        f'Вкус: {match_one.group(1)}\n'
                        f'Уже существует!'
                    )


async def sql_download_data(state, callback, message):
    async with state.proxy() as data:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            try:
                connection.begin()
                sql = f'INSERT INTO {callback} (img, name, description, price) VALUES (%s, %s, %s, %s)'
                cursor.execute(sql, tuple(data.values())[:4])
                sql_flavor = f'INSERT INTO {callback}_flavor (flavor, {callback}_name) VALUES (%s, %s)'
                cursor.execute(sql_flavor, (data['flavor'], data['name']))
                await message.answer('Данные загружены!',
                                     reply_markup=admin_keyboard)
                connection.commit()
            except Exception as ex:
                connection.rollback()
                try:
                    await message.answer(f'Возникла ошибка: {ex}')
                    sql_flavor = f'INSERT INTO {callback}_flavor (flavor, {callback}_name) VALUES (%s, %s)'
                    cursor.execute(sql_flavor, (data['flavor'], data['name']))
                    match = re.search(r"'([^']*)'", str(ex))
                    if "1062" in str(ex):
                        await message.answer(f'Позиция {match.group(1)} уже существует!\n'
                                             f'Для добавления новой позиции вкуса используйте кнопку "Добавить"')
                    await message.answer('Данные загружены!',
                                         reply_markup=admin_keyboard)
                    connection.commit()
                except Exception as ex:
                    match_one = re.search(r"'(\w+)", str(ex))
                    match_two = re.search(r"-([^']+)'", str(ex))
                    await message.answer(f'Возникла ошибка: {ex}')
                    if "1062" in str(ex):
                        await message.answer(
                            f'Позиция: {match_two.group(1)} \n'
                            f'Вкус: {match_one.group(1)}\n'
                            f'Уже существует!'
                        )


async def sql_name_output(callback):
    connection = connect_to_database()
    with connection.cursor() as cursor:
        print(callback.data)
        if '_admin' in callback.data:
            sql = f'SELECT name FROM {callback.data[:callback.data.find("_admin")]}'
        else:
            sql = f'SELECT name FROM {callback.data}'
        print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
    inline_keyboards = InlineKeyboardMarkup()
    for dic in result:
        button = InlineKeyboardButton(dic['name'], callback_data=f'{dic["name"]}_name')
        inline_keyboards.add(button)
    await bot.edit_message_text('Выберите позицию:',
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=inline_keyboards)


async def sql_flavor_output(callback, state, id=None):
    async with state.proxy() as data:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            sql = f'SELECT flavor ' \
                  f'FROM {data["category"]}_flavor ' \
                  f'WHERE {data["category"]}_name="{callback.data[:callback.data.find("_name"):]}"'
            cursor.execute(sql)
            result = cursor.fetchall()
    inline_keyboards = InlineKeyboardMarkup()
    for dic in result:
        button = InlineKeyboardButton(dic['flavor'], callback_data=f'{dic["flavor"]}_flavor')
        inline_keyboards.add(button)
    if id == callback.from_user.id:
        inline_keyboards.add(InlineKeyboardButton(text='Выбрать все', callback_data=f'all_flavor'))
    await bot.edit_message_text('Выберите вкус:',
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=inline_keyboards)


async def sql_delete_data(state, callback):
    async with state.proxy() as data:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            connection.begin()
            try:
                if callback.data != 'all_flavor':
                    sql = f'DELETE FROM {data["category"]}_flavor ' \
                          f'WHERE {data["category"]}_name="{data["name"]}" AND flavor="{data["flavor"]}"'
                    cursor.execute(sql)
                    await callback.answer(f'Позиция: {data["name"]}\n'
                                          f'Вкус: {data["flavor"]}\n'
                                          f'Данные удалены!', show_alert=True)
                else:
                    sql = f'SELECT flavor FROM {data["category"]}_flavor ' \
                          f'WHERE {data["category"]}_name="{data["name"]}"'
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for dic in result:
                        sql = f'DELETE FROM {data["category"]}_flavor ' \
                              f'WHERE {data["category"]}_name="{data["name"]}" AND flavor="{dic["flavor"]}"'
                        cursor.execute(sql)
                    sql = f'DELETE FROM {data["category"]} WHERE name="{data["name"]}";'
                    cursor.execute(sql)
                connection.commit()
            except Exception as ex:
                connection.rollback()


async def sql_product_output(callback, state):
    async with state.proxy() as data:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            sql = f"""
            SELECT img, name, description, flavor, price 
            FROM {data['category']} 
            JOIN {data['category']}_flavor 
            ON {data['category']}.name={data['category']}_flavor.{data['category']}_name 
            WHERE {data['category']}_flavor.flavor='{data['flavor']}'
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            keybord = InlineKeyboardMarkup().add(
                InlineKeyboardButton('Добавить в корзину ☑️',
                                     callback_data='add_to_cart')
            )
        data['price'] = result[0]['price']
        print(data)
    await bot.send_photo(callback.from_user.id,
                         result[0]['img'],
                         caption=f"Наименование: *{result[0]['name']}*\n"
                                 f"Описание: {result[0]['description']}\n"
                                 f"Вкус: _{result[0]['flavor']}_\n"
                                 f"Цена: *{result[0]['price']}₽*",
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=keybord
                         )


async def sql_adding_data_to_cart(message, state):
    user_id = message.from_user.id
    username = message.from_user.username
    connection = connect_to_database()
    with connection.cursor() as cursor:
        try:
            async with state.proxy() as data:
                sql = f"""
                SELECT * 
                FROM order_details 
                WHERE customers_id=%s AND product_name=%s AND flavor=%s
                """
                cursor.execute(sql, (user_id, data['name'], data['flavor']))
                result = cursor.fetchone()
                connection.begin()
                if result is not None:
                    quantity = result['quantity'] + data['quantity']
                    sql = """
                    UPDATE order_details 
                    SET quantity=%s
                    WHERE customers_id=%s AND product_name=%s AND flavor=%s
                    """
                    cursor.execute(
                        sql, (quantity, user_id, data['name'], data['flavor'])
                    )
                else:
                    sql = """
                    INSERT INTO order_details (customers_id, product_name, flavor, quantity, price)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        sql, (user_id, data['name'], data['flavor'], data['quantity'], data['price'])
                    )
            connection.commit()
            await message.answer('Товар добавлен в корзину!')
        except Exception as ex:
            print(datetime.now(), ex, username, user_id)
            connection.rollback()


async def content_basket(message):
    user_id = message.from_user.id
    username = message.from_user.username
    output = 'В Вашей корзине:\n'
    try:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            sql = f"""
            SELECT product_name, flavor, quantity
            FROM order_details
            WHERE customers_id=%s
            """
            cursor.execute(sql, user_id)
            result = cursor.fetchall()
        for line in result:
            output += f'- *{line["product_name"]}* (_{line["flavor"]}_) *х{line["quantity"]}*\n'
        await message.answer(
            output,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton('Очистить корзину 🗑', callback_data='empty_basket')
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as ex:
        print(datetime.now(), ex, username)


async def delete_data_basket(callback):
    username = callback.from_user.username
    user_id = callback.from_user.id
    message_id = callback.message.message_id
    chat_id = callback.message.chat.id
    try:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            connection.begin()
            sql = """
            DELETE
            FROM order_details
            WHERE customers_id=%s
            """
            cursor.execute(sql, user_id)
            connection.commit()
        await bot.edit_message_text(
            'Ваша корзина успешно очищена!', chat_id, message_id
        )
    except Exception as ex:
        print(datetime.now(), ex, username)


async def order_data(message):
    user_id = message.from_user.id
    output = 'Состав заказа:\n'
    total = 0
    connection = connect_to_database()
    with connection.cursor() as cursor:
        sql = """
        SELECT *
        FROM order_details
        WHERE customers_id=%s
        """
        cursor.execute(sql, user_id)
        result = cursor.fetchall()
    for line in result:
        output += f'- *{line["product_name"]}* (_{line["flavor"]}_) - {line["quantity"]} шт.\n'
        total += int(line['price']) * int(line['quantity'])
    output += f'\n*Итого к оплате: {total}₽*'
    await message.answer(
        f'{output}',
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('Оформить заказ 🗒', callback_data='place_order')
        ),
        parse_mode=ParseMode.MARKDOWN
    )


async def place_order_output_data(callback, state):
    username = callback.from_user.username
    user_id = callback.from_user.id
    async with state.proxy() as data:
        output = f'Уважаемый покупатель,\n\n' \
                 f'Спасибо за Ваш заказ в нашем интернет-магазине. ' \
                 f'Ваша покупка успешно оформлена и отгрузится в ближайшее время.\n\n' \
                 f'Детали заказа:\n\n' \
                 f'Дата заказа: {datetime.now().date()}\n\n' \
                 f'Информация о доставке:\n' \
                 f'Имя получателя: {data["recipient"]}\n' \
                 f'Адрес доставки: {data["address"]}\n\n' \
                 f'Состав заказа:\n'
        admin_output = f'Детали заказа:\n\n' \
                       f'Дата заказа: {datetime.now().date()}\n\n' \
                       f'Информация о доставке:\n' \
                       f'Никнейм получателя: @{username}\n' \
                       f'Имя получателя: {data["recipient"]}\n' \
                       f'Адрес доставки: {data["address"]}\n\n' \
                       f'Состав заказа:\n'

    total = 0
    connection = connect_to_database()
    with connection.cursor() as cursor:
        sql = """
        SELECT *
        FROM order_details
        WHERE customers_id=%s
        """
        cursor.execute(sql, str(user_id))
        result = cursor.fetchall()
    for line in result:
        output += f'- *{line["product_name"]}* (_{line["flavor"]}_) - {line["quantity"]} шт.\n'
        admin_output += f'- {line["product_name"]} ({line["flavor"]}) - {line["quantity"]} шт.\n'
        total += int(line['price']) * int(line['quantity'])
    output += f'\n*Итого к оплате: {total}₽*\n\n' \
              f'Спасибо, что выбрали нас!'
    admin_output += f'\nИтого к оплате: {total}₽.'
    await callback.message.answer(
        output,
        parse_mode=ParseMode.MARKDOWN
    )
    print(admin_output)
    await bot.send_message(
        1164009212,
        admin_output
    )
