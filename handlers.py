# <-- ОСНОВНАЯ ЛОГИКА -->
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import random
from datetime import datetime
from keyboards import get_main_keyboard, get_back_keyboard, get_villagers_keyboard
from html import escape

router = Router()

def calculate_villager_price(current_villagers):
    return 10 + (current_villagers * 3)

@router.message(Command("start"))
async def cmd_start(message: Message, db):
    user = db.get_user(message.from_user.id)
    nickname = user[1]
    villagers = user[2]
    wood = user[3]
    energy = user[4]
    stone = user[5]
    workers = user[6]
    level = user[9]
    coins = user[10]
    territory = user[11]
    mine_repaired = user[12]
    pickaxes = user[13]
    next_price = calculate_villager_price(villagers)
    
    text = f"<b>🏡 Добро пожаловать, {nickname}!</b>\n\n👥 <b>Жители:</b> {villagers}\n🪵 <b>Древесина:</b> {wood}\n🌞 <b>Энергия:</b> {energy}\n🪨 <b>Камень:</b> {stone}\n👷 <b>Рабочие:</b> {workers}/{villagers}\n🏠 <b>Уровень:</b> {level}\n🪙 <b>Монеты:</b> {coins}\n🏞️ <b>Территории:</b> {territory}\n💰 <b>Следующий житель:</b> {next_price} 🌞\n\n<i>Используй кнопки для управления</i>"
    
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    
    if level >= 10 and mine_repaired == 0:
        await message.answer("<b>Хмм.. а что тут у нас?</b>\n\nЖители обнаружили заброшенную шахту!\n\nНапиши <b>шахта</b> чтобы осмотреть", parse_mode="HTML")

@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    nickname = user[1]
    villagers = user[2]
    wood = user[3]
    energy = user[4]
    stone = user[5]
    workers = user[6]
    level = user[9]
    coins = user[10]
    territory = user[11]
    next_price = calculate_villager_price(villagers)
    
    text = f"<b>🏡 Главное меню</b>\n\n👥 <b>Жители:</b> {villagers}\n🪵 <b>Древесина:</b> {wood}\n🌞 <b>Энергия:</b> {energy}\n🪨 <b>Камень:</b> {stone}\n👷 <b>Рабочие:</b> {workers}/{villagers}\n🏠 <b>Уровень:</b> {level}\n🪙 <b>Монеты:</b> {coins}\n🏞️ <b>Территории:</b> {territory}\n💰 <b>Следующий житель:</b> {next_price} 🌞"
    
    await callback.message.edit_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    
    mine_repaired = user[12]
    if level >= 10 and mine_repaired == 0:
        await callback.message.answer("<b>Хмм.. а что тут у нас?</b>\n\nЖители обнаружили заброшенную шахту!\n\nНапиши <b>шахта</b> чтобы осмотреть", parse_mode="HTML")
    
    await callback.answer()
@router.callback_query(F.data == "village")
async def show_village(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    villagers = user[2]
    wood = user[3]
    energy = user[4]
    stone = user[5]
    workers = user[6]
    level = user[9]
    
    workers_text = "🟢" * workers + "⚫" * (villagers - workers)
    
    text = f"<b>🏡 Ваша деревня</b>\n\n👥 <b>Население:</b> {villagers}\n🪵 <b>Древесина:</b> {wood}\n🌞 <b>Энергия:</b> {energy}\n🪨 <b>Камень:</b> {stone}\n🏠 <b>Уровень:</b> {level}\n\n<b>Рабочие:</b>\n{workers_text}"
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "villagers")
async def show_villagers(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    villagers = user[2]
    price = calculate_villager_price(villagers)
    
    text = f"<b>👥 Управление жителями</b>\n\n<b>Текущее население:</b> {villagers}\n<b>Стоимость нового жителя:</b> {price} 🌞\n\n<i>Цена растет с каждым жителем!</i>"
    
    await callback.message.edit_text(text, reply_markup=get_villagers_keyboard(price), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "buy_villager")
async def buy_villager(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    villagers = user[2]
    energy = user[4]
    price = calculate_villager_price(villagers)
    
    if energy >= price:
        db.update_user(callback.from_user.id, villagers=villagers + 1, energy=energy - price)
        new_user = db.get_user(callback.from_user.id)
        new_price = calculate_villager_price(new_user[2])
        
        text = f"<b>✅ Новый житель прибыл!</b>\n\n👥 <b>Теперь жителей:</b> {new_user[2]}\n🌞 <b>Осталось энергии:</b> {new_user[4]}\n💰 <b>Следующий житель:</b> {new_price} 🌞"
        
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    else:
        text = f"<b>❌ Недостаточно энергии!</b>\n\nНужно {price} 🌞, у вас только {energy} 🌞"
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    
    await callback.answer()

@router.callback_query(F.data == "harvest")
async def show_harvest(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    villagers = user[2]
    workers = user[6]
    level = user[9]
    mine_repaired = user[12]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    row = []
    if workers > 0:
        row.append(InlineKeyboardButton(text="➖", callback_data="worker_remove"))
    row.append(InlineKeyboardButton(text=f"{workers}/{villagers}", callback_data="none"))
    if workers < villagers:
        row.append(InlineKeyboardButton(text="➕", callback_data="worker_add"))
    
    keyboard.inline_keyboard.append(row)
    
    if mine_repaired >= 2:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⚒️ Шахта", callback_data="mine_menu")
        ])
    
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔄 Собрать", callback_data="collect")])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")])
    
    text = f"<b>🪵 Добыча</b>\n\n👷 <b>Рабочие:</b> {workers}/{villagers}\n🏠 <b>Уровень:</b> {level}\n\n<b>Добыча за 1 минуту:</b>\n• 🪵 1-3 на рабочего\n• 🌞 2-5 на рабочего"
    
    if mine_repaired >= 2:
        text += f"\n\n<b>⚒️ Шахта доступна!</b>"
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()
    
@router.callback_query(F.data == "worker_add")
async def add_worker(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    villagers = user[2]
    workers = user[6]
    
    if workers < villagers:
        db.update_user(callback.from_user.id, workers=workers + 1)
        await show_harvest(callback, db)
    await callback.answer()

@router.callback_query(F.data == "worker_remove")
async def remove_worker(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    workers = user[6]
    
    if workers > 0:
        db.update_user(callback.from_user.id, workers=workers - 1)
        await show_harvest(callback, db)
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
    
    workers = user[6]
    
    if workers == 0:
        await callback.answer("❌ Нет рабочих на добыче!", show_alert=True)
        return
    
    wood_per_worker = random.randint(1, 3)
    energy_per_worker = random.randint(2, 5)
    
    level = user[9]
    level_bonus = level / 2
    
    wood_per_worker = max(1, int(wood_per_worker + level_bonus))
    energy_per_worker = max(2, int(energy_per_worker + level_bonus))
    
    total_wood = wood_per_worker * workers
    total_energy = energy_per_worker * workers
    
    db.update_user(
        callback.from_user.id,
        wood=user[3] + total_wood,
        energy=user[4] + total_energy,
        last_harvest=datetime.now().isoformat()
    )
    
    new_user = db.get_user(callback.from_user.id)
    
    text = f"<b>✅ Урожай собран!</b>\n\n🏠 <b>Уровень:</b> {level}\n👷 <b>Работало:</b> {workers} жителей\n\n<b>Добыто с жителя:</b>\n• 🪵 {wood_per_worker}\n• 🌞 {energy_per_worker}\n\n<b>Всего добыто:</b>\n• 🪵 +{total_wood}\n• 🌞 +{total_energy}\n\n<b>Итого:</b>\n• 🪵 {new_user[3]}\n• 🌞 {new_user[4]}"
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    nickname = user[1]
    villagers = user[2]
    wood = user[3]
    energy = user[4]
    stone = user[5]
    workers = user[6]
    level = user[9]
    coins = user[10]
    territory = user[11]
    mine_repaired = user[12]
    pickaxes = user[13]
    price = calculate_villager_price(villagers)
    
    text = f"<b>📊 Статистика</b>\n\n👤 <b>Игрок:</b> {nickname}\n👥 <b>Жителей:</b> {villagers}\n🪵 <b>Древесина:</b> {wood}\n🌞 <b>Энергия:</b> {energy}\n🪨 <b>Камень:</b> {stone}\n👷 <b>Рабочие:</b> {workers}/{villagers}\n🏠 <b>Уровень:</b> {level}\n🪙 <b>Монеты:</b> {coins}\n🏞️ <b>Территории:</b> {territory}\n⛏️ <b>Кирок:</b> {pickaxes}\n💰 <b>Цена жителя:</b> {price} 🌞\n\n<i>Продолжайте развивать деревню!</i>"
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await callback.answer()
