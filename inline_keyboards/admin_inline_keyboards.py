from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

download_admin_inline_keyboard = InlineKeyboardMarkup(row_width=1)
button_electronic_cigarettes_download = InlineKeyboardButton(text='Электронные сигареты',
                                                             callback_data='electronic_cigarettes_admin_download')
button_liquid_download = InlineKeyboardButton(text='Жидкости',
                                              callback_data='liquid_admin_download')
download_admin_inline_keyboard.row(button_electronic_cigarettes_download, button_liquid_download)


delete_admin_inline_keyboard_category = InlineKeyboardMarkup(row_width=1)
button_electronic_cigarettes_delete = InlineKeyboardButton(text='Электронные сигареты',
                                                           callback_data='electronic_cigarettes_admin_delete')
button_liquid_delete = InlineKeyboardButton(text='Жидкости',
                                            callback_data='liquid_admin_delete')
delete_admin_inline_keyboard_category.row(button_electronic_cigarettes_delete, button_liquid_delete)


# delete_admin_inline_keyboard_model = InlineKeyboardMarkup(row_width=1)
# button_model = [InlineKeyboardButton(text=f'{data}',
#                                      callback_data=f'{data}')
#                 for data in sql_admin_deletion_category(FSMAdmin.delete_call_back['category'])]


