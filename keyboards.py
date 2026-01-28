# <-- ИНЛАЙН-КЛАВИАТУРА -->

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("👥 Жители", callback_data="villagers"),
        InlineKeyboardButton("🪵 Добыча", callback_data="harvest"),
        InlineKeyboardButton("🏠 Деревня", callback_data="village"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats")
    )
    return keyboard

def get_villagers_keyboard(price):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(f"🛒 Купить жителя ({price} 🌞)", callback_data="buy_villager"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_main")
    )
    return keyboard

def get_back_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_main"))
    return keyboard