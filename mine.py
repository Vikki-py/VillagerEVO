from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import random
import asyncio

router = Router()

def check_mine_discovery(user):
    level = user[10] if len(user) > 10 else 0
    mine_repaired = user[13] if len(user) > 13 else 0
    return level >= 10 and mine_repaired == 0

@router.message(F.text.lower().in_(["шахта", "шахту", "mine"]))
async def show_mine(message: Message, db):
    user = db.get_user(message.from_user.id)
    
    if not check_mine_discovery(user):
        await message.answer("Шахта еще не обнаружена!")
        return
    
    mine_repaired = user[13] if len(user) > 13 else 0
    pickaxes = user[14] if len(user) > 14 else 0
    
    if mine_repaired == 0:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔧 Починить шахту (250💰 300🪵 500🌞)", callback_data="repair_mine")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
        ])
        
        text = (
            f"<b>🏭 Заброшенная шахта</b>\n\n"
            f"🔍 <b>Обнаружено:</b> Заброшенная каменная шахта\n"
            f"🛠️ <b>Состояние:</b> Требуется ремонт\n\n"
            f"<b>Для ремонта нужно:</b>\n"
            f"• 250 🪙 монет\n"
            f"• 300 🪵 древесины\n"
            f"• 500 🌞 энергии\n\n"
            f"<i>После ремонта можно будет добывать камень!</i>"
        )
    else:
        wood_workers = user[15] if len(user) > 15 else 0
        stone_workers = user[16] if len(user) > 16 else 0
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🛒 Купить кирку (75💰)", callback_data="buy_pickaxe"),
                InlineKeyboardButton(text=f"⛏️ {pickaxes}", callback_data="none")
            ],
            [InlineKeyboardButton(text="⚒️ Управление рабочими", callback_data="manage_mine_workers")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
        ])
        
        text = (
            f"<b>🏭 Каменная шахта</b>\n\n"
            f"⛏️ <b>Кирок:</b> {pickaxes}\n"
            f"👷 <b>На добыче дерева:</b> {wood_workers}\n"
            f"👷 <b>На добыче камня:</b> {stone_workers}/{pickaxes}\n"
            f"🪨 <b>Камня:</b> {user[6] if len(user) > 6 else 0}\n\n"
            f"<b>Добыча камня:</b> раз в 5 минут\n"
            f"<i>Кирки нужны для добычи камня!</i>"
        )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "repair_mine")
async def repair_mine(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    if user[13] == 1:
        await callback.answer("✅ Шахта уже отремонтирована!", show_alert=True)
        return
    
    if user[9] < 250 or user[4] < 300 or user[5] < 500:
        await callback.answer("❌ Недостаточно ресурсов!", show_alert=True)
        return
    
    db.update_user(
        callback.from_user.id,
        coins=user[9] - 250,
        wood=user[4] - 300,
        energy=user[5] - 500,
        mine_repaired=1
    )
    
    await callback.answer("⏳ Начинаем ремонт шахты...", show_alert=True)
    
    repair_text = (
        f"<b>🔧 Начался ремонт шахты!</b>\n\n"
        f"⏱️ <b>Время ремонта:</b> 5 минут\n"
        f"📦 <b>Затрачено:</b>\n"
        f"• 250 🪙 монет\n"
        f"• 300 🪵 древесины\n"
        f"• 500 🌞 энергии\n\n"
        f"<i>Ожидайте завершения ремонта...</i>"
    )
    
    await callback.message.edit_text(repair_text, parse_mode="HTML")
    
    await asyncio.sleep(300)
    
    db.update_user(callback.from_user.id, mine_repaired=2)
    
    final_text = (
        f"<b>✅ Шахта отремонтирована!</b>\n\n"
        f"🏭 <b>Готова к работе!</b>\n"
        f"🪨 <b>Можно добывать камень</b>\n\n"
        f"<i>Купите кирки у торговца и начните добычу!</i>"
    )
    
    await callback.message.answer(final_text, parse_mode="HTML")

@router.callback_query(F.data == "buy_pickaxe")
async def buy_pickaxe(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    if user[9] < 75:
        await callback.answer("❌ Нужно 75 монет!", show_alert=True)
        return
    
    db.update_user(
        callback.from_user.id,
        coins=user[9] - 75,
        pickaxes=user[14] + 1
    )
    
    new_user = db.get_user(callback.from_user.id)
    
    text = (
        f"<b>✅ Куплена кирка!</b>\n\n"
        f"⛏️ <b>Теперь кирок:</b> {new_user[14]}\n"
        f"💰 <b>Потрачено:</b> 75 монет\n"
        f"💰 <b>Осталось:</b> {new_user[9]} монет\n\n"
        f"<i>Теперь можно отправлять рабочих на добычу камня!</i>"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "manage_mine_workers")
async def manage_mine_workers(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    total_villagers = user[3]
    wood_workers = user[15] if len(user) > 15 else 0
    stone_workers = user[16] if len(user) > 16 else 0
    pickaxes = user[14] if len(user) > 14 else 0
    free_workers = total_villagers - wood_workers - stone_workers
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🪵➖", callback_data="mine_wood_remove"),
            InlineKeyboardButton(text=f"Дерево: {wood_workers}", callback_data="none"),
            InlineKeyboardButton(text="🪵➕", callback_data="mine_wood_add")
        ],
        [
            InlineKeyboardButton(text="🪨➖", callback_data="mine_stone_remove"),
            InlineKeyboardButton(text=f"Камень: {stone_workers}/{pickaxes}", callback_data="none"),
            InlineKeyboardButton(text="🪨➕", callback_data="mine_stone_add")
        ],
        [InlineKeyboardButton(text="⚒️ Начать добычу", callback_data="start_mining")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="mine_back")]
    ])
    
    text = (
        f"<b>⚒️ Управление рабочими в шахте</b>\n\n"
        f"👥 <b>Всего жителей:</b> {total_villagers}\n"
        f"🆓 <b>Свободно:</b> {free_workers}\n\n"
        f"<b>Текущее распределение:</b>\n"
        f"• 🪵 Добыча дерева: {wood_workers}\n"
        f"• 🪨 Добыча камня: {stone_workers}/{pickaxes}\n\n"
        f"<i>Для добычи камня нужны кирки!</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()
