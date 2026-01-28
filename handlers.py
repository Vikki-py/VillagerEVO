х# <-- КОМАНДЫ И ЛОГИКА -->

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import random
from datetime import datetime
from keyboards import get_main_keyboard, get_back_keyboard, get_villagers_keyboard
from html import escape

router = Router()

def calculate_villager_price(current_villagers):
    return 10 + (current_villagers - 1) * 3

@router.message(Command("start"))
async def cmd_start(message: Message, db):
    user = db.get_user(message.from_user.id)
    nickname = user[2]
    next_price = calculate_villager_price(user[3])
    level = user[10] if len(user) > 10 else 0
    mine_repaired = user[13] if len(user) > 13 else 0
    
    text = f"<b>🏡 Добро пожаловать, {nickname}!</b>\n\n👥 <b>Жители:</b> {user[3]}\n🪵 <b>Древесина:</b> {user[4]}\n🌞 <b>Солнечная энергия:</b> {user[5]}\n👷 <b>Рабочие:</b> {user[7]}/{user[3]}\n💰 <b>Следующий житель:</b> {next_price} 🌞\n\n<i>Используй кнопки для управления</i>"
    
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    
    if level >= 10 and mine_repaired == 0:
        await message.answer("<b>Хмм.. а что тут у нас?</b>\n\nЖители обнаружили заброшенную шахту!\n\nНапиши <b>шахта</b> чтобы осмотреть", parse_mode="HTML")
        
@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    next_price = calculate_villager_price(user[3])
    
    text = (
        f"<b>🏡 Главное меню</b>\n\n"
        f"👥 <b>Жители:</b> {user[3]}\n"
        f"🪵 <b>Древесина:</b> {user[4]}\n"
        f"🌞 <b>Солнечная энергия:</b> {user[5]}\n"
        f"👷 <b>Рабочие:</b> {user[6]}/{user[3]}\n"
        f"💰 <b>Следующий житель:</b> {next_price} 🌞"
    )
    
    await callback.message.edit_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "village")
async def show_village(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    workers_text = "🟢" * user[6] + "⚫" * (user[3] - user[6])
    
    text = (
        f"<b>🏡 Ваша деревня</b>\n\n"
        f"👥 <b>Население:</b> {user[3]} жителей\n"
        f"🪵 <b>Древесина:</b> {user[4]}\n"
        f"🌞 <b>Энергия:</b> {user[5]}\n\n"
        f"<b>Рабочие в поле:</b>\n{workers_text}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "villagers")
async def show_villagers(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    price = calculate_villager_price(user[3])
    
    text = (
        f"<b>👥 Управление жителями</b>\n\n"
        f"<b>Текущее население:</b> {user[3]}\n"
        f"<b>Стоимость нового жителя:</b> {price} 🌞\n\n"
        f"<i>Цена растет с каждым жителем!</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_villagers_keyboard(price), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "buy_villager")
async def buy_villager(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    price = calculate_villager_price(user[3])
    
    if user[5] >= price:
        db.update_user(
            callback.from_user.id,
            villagers=user[3] + 1,
            energy=user[5] - price
        )
        new_user = db.get_user(callback.from_user.id)
        new_price = calculate_villager_price(new_user[3])
        
        text = (
            f"<b>✅ Новый житель прибыл!</b>\n\n"
            f"👥 <b>Теперь жителей:</b> {new_user[3]}\n"
            f"🌞 <b>Осталось энергии:</b> {new_user[5]}\n"
            f"💰 <b>Следующий житель:</b> {new_price} 🌞"
        )
        
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    else:
        text = f"<b>❌ Недостаточно энергии!</b>\n\nНужно {price} 🌞, у вас только {user[5]} 🌞"
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    
    await callback.answer()

@router.callback_query(F.data == "harvest")
async def show_harvest(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    level = user[10] if len(user) > 10 else 0
    mine_repaired = user[13] if len(user) > 13 else 0
    
    harvest_btn = InlineKeyboardButton(text="🔄 Собрать урожай", callback_data="collect")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    row1 = []
    if user[7] > 0:
        row1.append(InlineKeyboardButton(text="➖", callback_data="worker_remove"))
    row1.append(InlineKeyboardButton(text=f"{user[7]}/{user[3]}", callback_data="none"))
    if user[7] < user[3]:
        row1.append(InlineKeyboardButton(text="➕", callback_data="worker_add"))
    
    keyboard.inline_keyboard.append(row1)
    
    if mine_repaired >= 2:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⚒️ Шахта", callback_data="mine")
        ])
    
    keyboard.inline_keyboard.append([harvest_btn])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")])
    
    text = f"<b>🪵 Добыча ресурсов</b>\n\n🏠 <b>Уровень деревни:</b> {level}\n👷 <b>Рабочие:</b> {user[7]}/{user[3]}\n\n<b>Добыча за 1 минуту:</b>\n• 🪵 Древесина: 1-3 на рабочего\n• 🌞 Энергия: 2-5 на рабочего"
    
    if mine_repaired >= 2:
        text += f"\n\n<b>⚒️ Шахта доступна!</b>"
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "worker_add")
async def add_worker(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    if user[6] < user[3]:
        db.update_user(callback.from_user.id, workers=user[6] + 1)
        user = db.get_user(callback.from_user.id)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        row = []
        if user[6] > 0:
            row.append(InlineKeyboardButton(text="➖", callback_data="worker_remove"))
        row.append(InlineKeyboardButton(text=f"{user[6]}/{user[3]}", callback_data="none"))
        if user[6] < user[3]:
            row.append(InlineKeyboardButton(text="➕", callback_data="worker_add"))
        keyboard.inline_keyboard.append(row)
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔄 Собрать урожай", callback_data="collect")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")])
        
        text = f"<b>🪵 Добыча ресурсов</b>\n\n👷 <b>Рабочие:</b> {user[6]}/{user[3]}\n\n<b>Добыча за 1 минуту:</b>\n• 🪵 Древесина: 1-3 на рабочего\n• 🌞 Энергия: 2-5 на рабочего"
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "worker_remove")
async def remove_worker(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    if user[6] > 0:
        db.update_user(callback.from_user.id, workers=user[6] - 1)
        user = db.get_user(callback.from_user.id)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        row = []
        if user[6] > 0:
            row.append(InlineKeyboardButton(text="➖", callback_data="worker_remove"))
        row.append(InlineKeyboardButton(text=f"{user[6]}/{user[3]}", callback_data="none"))
        if user[6] < user[3]:
            row.append(InlineKeyboardButton(text="➕", callback_data="worker_add"))
        keyboard.inline_keyboard.append(row)
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔄 Собрать урожай", callback_data="collect")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")])
        
        text = f"<b>🪵 Добыча ресурсов</b>\n\n👷 <b>Рабочие:</b> {user[6]}/{user[3]}\n\n<b>Добыча за 1 минуту:</b>\n• 🪵 Древесина: 1-3 на рабочего\n• 🌞 Энергия: 2-5 на рабочего"
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "collect")
async def collect_resources(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    if user[7]:
        last_harvest = datetime.fromisoformat(user[7])
        time_since = datetime.now() - last_harvest
        if time_since.total_seconds() < 60:
            time_left = 60 - int(time_since.total_seconds())
            await callback.answer(f"⏳ Жди еще {time_left} секунд!", show_alert=True)
            return
    
    if user[6] == 0:
        await callback.answer("❌ Нет рабочих на добыче!", show_alert=True)
        return
    
    base_wood_min, base_wood_max = 1, 3
    base_energy_min, base_energy_max = 2, 5
    
    level = user[8] if len(user) > 8 else 0
    level_bonus = level / 2
    
    wood_per_worker = random.randint(base_wood_min, base_wood_max) + level_bonus
    energy_per_worker = random.randint(base_energy_min, base_energy_max) + level_bonus
    
    wood_per_worker = max(1, int(wood_per_worker))
    energy_per_worker = max(2, int(energy_per_worker))
    
    total_wood = wood_per_worker * user[6]
    total_energy = energy_per_worker * user[6]
    
    db.update_user(
        callback.from_user.id,
        wood=user[4] + total_wood,
        energy=user[5] + total_energy,
        last_harvest=datetime.now().isoformat()
    )
    
    new_user = db.get_user(callback.from_user.id)
    
    text = (
        f"<b>✅ Урожай собран!</b>\n\n"
        f"🏠 <b>Уровень деревни:</b> {level}\n"
        f"👷 <b>Работало:</b> {user[6]} жителей\n"
        f"🪵 <b>Добыто с жителя:</b> {wood_per_worker} (база 1-3 + бонус {level_bonus:.1f})\n"
        f"🌞 <b>Энергии с жителя:</b> {energy_per_worker} (база 2-5 + бонус {level_bonus:.1f})\n\n"
        f"<b>Всего добыто:</b>\n"
        f"• 🪵 Древесина: +{total_wood}\n"
        f"• 🌞 Энергия: +{total_energy}\n\n"
        f"<b>Итого:</b>\n"
        f"• 🪵 {new_user[4]}\n"
        f"• 🌞 {new_user[5]}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    nickname = user[2]
    price = calculate_villager_price(user[3])
    
    text = (
        f"<b>📊 Статистика</b>\n\n"
        f"👤 <b>Игрок:</b> {nickname}\n"
        f"👥 <b>Жителей:</b> {user[3]}\n"
        f"🪵 <b>Древесина:</b> {user[4]}\n"
        f"🌞 <b>Энергия:</b> {user[5]}\n"
        f"👷 <b>Рабочие:</b> {user[6]}/{user[3]}\n"
        f"💰 <b>Цена жителя:</b> {price} 🌞\n\n"
        f"<i>Продолжайте развивать деревню!</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await callback.answer()
