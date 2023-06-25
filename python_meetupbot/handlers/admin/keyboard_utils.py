import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .static_text import features_choose, admin_url


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def make_keyboard_with_admin_features() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(features_choose[0],
                              url=admin_url)],
        [InlineKeyboardButton(features_choose[1],
                              callback_data=1)],
        [InlineKeyboardButton(features_choose[2],
                              callback_data=2)],
        [InlineKeyboardButton(features_choose[3],
                              callback_data=3)]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    return reply_markup
