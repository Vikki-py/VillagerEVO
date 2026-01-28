# <-- КОММАНДЫ И ЛОГИКА -->

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import random
from datetime import datetime
from keyboards import get_main_keyboard, get_back_keyboard, get_villagers_keyboard
import asyncio
from html import escape
from aiogram.types import InlineKeyboardButton

router = Router()

def calculate_villager_price(current_villagers):
    return 5 + (current_villagers - 1) * 2

@router.message(Command("start"))
async def cmd_start(message: Message, db):
    user = db.get_user(message.from_user.id)
    next_price = calculate_villager_price(user[2])
    name = escape(message.from_user.first_name)
    
    text = (
        f"<b>🏡 Добро пожаловать, {name}!</b>\n\n"
        f"👥 <b>Жители:</b> {user[2]}\n"
        f"🪵 <b>Древесина:</b> {user[3]}\n"
        f"🌞 <b>Солнечная энергия:</b> {user[4]}\n"
        f"👷 <b>Рабочие:</b> {user[5]}/{user[2]}\n"
        f"💰 <b>Следующий житель:</b> {next_price} 🌞\n\n"
        f"<i>Используй кнопки для управления</i>"
    )
    
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    next_price = calculate_villager_price(user[2])
    
    text = (
        f"<b>🏡 Главное меню</b>\n\n"
        f"👥 <b>Жители:</b> {user[2]}\n"
        f"🪵 <b>Древесина:</b> {user[3]}\n"
        f"🌞 <b>Солнечная энергия:</b> {user[4]}\n"
        f"👷 <b>Рабочие:</b> {user[5]}/{user[2]}\n"
        f"💰 <b>Следующий житель:</b> {next_price} 🌞"
    )
    
    await callback.message.edit_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "village")
async def show_village(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    workers_text = "🟢" * user[5] + "⚫" * (user[2] - user[5])
    
    text = (
        f"<b>🏡 Ваша деревня</b>\n\n"
        f"👥 <b>Население:</b> {user[2]} жителей\n"
        f"🪵 <b>Древесина:</b> {user[3]}\n"
        f"🌞 <b>Энергия:</b> {user[4]}\n\n"
        f"<b>Рабочие в поле:</b>\n{workers_text}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "villagers")
async def show_villagers(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    price = calculate_villager_price(user[2])
    
    text = (
        f"<b>👥 Управление жителями</b>\n\n"
        f"<b>Текущее население:</b> {user[2]}\n"
        f"<b>Стоимость нового жителя:</b> {price} 🌞\n\n"
        f"<i>Цена растет с каждым жителем!</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_villagers_keyboard(price), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "buy_villager")
async def buy_villager(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    price = calculate_villager_price(user[2])
    
    if user[4] >= price:
        db.update_user(
            callback.from_user.id,
            villagers=user[2] + 1,
            energy=user[4] - price
        )
        new_user = db.get_user(callback.from_user.id)
        new_price = calculate_villager_price(new_user[2])
        
        text = (
            f"<b>✅ Новый житель прибыл!</b>\n\n"
            f"👥 <b>Теперь жителей:</b> {new_user[2]}\n"
            f"🌞 <b>Осталось энергии:</b> {new_user[4]}\n"
            f"💰 <b>Следующий житель:</b> {new_price} 🌞"
        )
        
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    else:
        text = f"<b>❌ Недостаточно энергии!</b>\n\nНужно {price} 🌞, у вас только {user[4]} 🌞"
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    
    await callback.answer()

@router.callback_query(F.data == "harvest")
async def show_harvest(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    if user[6]:
        last_harvest = datetime.fromisoformat(user[6])
        time_since = datetime.now() - last_harvest
        can_harvest = time_since.total_seconds() >= 60
        
        if can_harvest:
            harvest_btn = InlineKeyboardButton(text="🔄 Собрать урожай", callback_data="collect")
        else:
            time_left = 60 - int(time_since.total_seconds())
            harvest_btn = InlineKeyboardButton(text=f"⏳ {time_left} сек", callback_data="wait")
    else:
        harvest_btn = InlineKeyboardButton(text="🔄 Собрать урожай", callback_data="collect")
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    row = []
    if user[5] > 0:
        row.append(InlineKeyboardButton(text="➖ Убрать", callback_data="worker_remove"))
    row.append(InlineKeyboardButton(text=f"{user[5]}/{user[2]}", callback_data="none"))
    if user[5] < user[2]:
        row.append(InlineKeyboardButton(text="➕ Добавить", callback_data="worker_add"))
    
    keyboard.row(*row)
    keyboard.add(harvest_btn)
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    
    text = (
        f"<b>🪵 Добыча ресурсов</b>\n\n"
        f"👷 <b>Рабочие:</b> {user[5]}/{user[2]}\n\n"
        f"<b>Добыча за 1 минуту:</b>\n"
        f"• 🪵 Древесина: 1-3 на рабочего\n"
        f"• 🌞 Энергия: 2-5 на рабочего"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "worker_add")
async def add_worker(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    if user[5] < user[2]:
        db.update_user(callback.from_user.id, workers=user[5] + 1)
        await show_harvest(callback, db)
    
    await callback.answer()

@router.callback_query(F.data == "worker_remove")
async def remove_worker(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    if user[5] > 0:
        db.update_user(callback.from_user.id, workers=user[5] - 1)
        await show_harvest(callback, db)
    
    await callback.answer()

@router.callback_query(F.data == "collect")
async def collect_resources(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    if user[6]:
        last_harvest = datetime.fromisoformat(user[6])
        time_since = datetime.now() - last_harvest
        if time_since.total_seconds() < 60:
            time_left = 60 - int(time_since.total_seconds())
            await callback.answer(f"⏳ Жди еще {time_left} секунд!", show_alert=True)
            return
    
    if user[5] == 0:
        await callback.answer("❌ Нет рабочих на добыче!", show_alert=True)
        return
    
    wood_per_worker = random.randint(1, 3)
    energy_per_worker = random.randint(2, 5)
    
    total_wood = wood_per_worker * user[5]
    total_energy = energy_per_worker * user[5]
    
    db.update_user(
        callback.from_user.id,
        wood=user[3] + total_wood,
        energy=user[4] + total_energy,
        last_harvest=datetime.now().isoformat()
    )
    
    text = (
        f"<b>✅ Урожай собран!</b>\n\n"
        f"👷 <b>Работало:</b> {user[5]} жителей\n"
        f"🪵 <b>Добыто древесины:</b> +{total_wood}\n"
        f"🌞 <b>Добыто энергии:</b> +{total_energy}\n\n"
        f"<b>Итого:</b>\n"
        f"• 🪵 Древесина: {user[3] + total_wood}\n"
        f"• 🌞 Энергия: {user[4] + total_energy}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    price = calculate_villager_price(user[2])
    
    text = (
        f"<b>📊 Статистика</b>\n\n"
        f"👤 <b>Игрок:</b> {callback.from_user.first_name}\n"
        f"👥 <b>Жителей:</b> {user[2]}\n"
        f"🪵 <b>Древесина:</b> {user[3]}\n"
        f"🌞 <b>Энергия:</b> {user[4]}\n"
        f"👷 <b>Рабочие:</b> {user[5]}/{user[2]}\n"
        f"💰 <b>Цена жителя:</b> {price} 🌞\n\n"
        f"<i>Продолжайте развивать деревню!</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await callback.answer()
