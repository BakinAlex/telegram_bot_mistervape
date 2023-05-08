from handlers import client, general, admin
from aiogram import executor
from create_bot import dp
from database import mysql_db


async def on_startup(_):
    print('Bot online!')
    mysql_db.sql_start()


admin.register_handler_admin(dp)
client.register_handler_client(dp)
general.register_handler_general(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
