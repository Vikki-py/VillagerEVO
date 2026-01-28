# <-- ИНЛАЙН-КЛАВИАТУРА -->

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Жители", callback_data="villagers"),
            InlineKeyboardButton(text="🪵 Добыча", callback_data="harvest")
        ],
        [
            InlineKeyboardButton(text="🏠 Деревня", callback_data="village"),
            InlineKeyboardButton(text="🏗️ Улучшения", callback_data="upgrades")
        ],
        [
            InlineKeyboardButton(text="🏪 Рынок", callback_data="market"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
        ]
    ])
    return keyboard

def get_villagers_keyboard(price):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🛒 Купить жителя ({price} 🌞)", callback_data="buy_villager")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ])
    return keyboard

def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ])
    return keyboard
