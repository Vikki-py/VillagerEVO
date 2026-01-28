# <-- ИНЛАЙН-КЛАВИАТУРА -->

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
