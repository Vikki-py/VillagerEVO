# <-- ШАХТА -->
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import random
import asyncio

router = Router()

@router.message(F.text.lower() == "проверить шахту")
async def check_mine_status(message: Message, db):
    user = db.get_user(message.from_user.id)
    level = user[9]
    mine_repaired = user[12]
    
    status_text = "неизвестно"
    if mine_repaired == 0:
        status_text = "заброшена"
    elif mine_repaired == 1:
        status_text = "в ремонте"
    elif mine_repaired == 2:
        status_text = "работает"
    
    await message.answer(f"""
📊 Проверка шахты:
• Уровень игрока: {level}
• Состояние шахты: {status_text} ({mine_repaired})
• Требуется уровень: 10
• Доступна: {"✅ Да" if level >= 10 else "❌ Нет"}
""")
    
@router.message(F.text.lower().in_(["шахта", "mine"]))
async def mine_command(message: Message, db):
    user = db.get_user(message.from_user.id)
    level = user[9]
    mine_repaired = user[12]
    
    if level < 10:
        await message.answer("❌ Шахта с 10 уровня!")
        return
    
    if mine_repaired == 0:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔧 Починить шахту (250💰 300🪵 500🌞)", callback_data="repair_mine_start")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
        ])
        
        text = "<b>🏭 Заброшенная шахта</b>\n\n<b>Для ремонта:</b>\n• 250 🪙 монет\n• 300 🪵 древесины\n• 500 🌞 энергии\n\n<i>После ремонта можно добывать камень!</i>"
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    
    elif mine_repaired == 1:
        await message.answer("⏳ Шахта на ремонте... (5 минут)")
    
    else:
        pickaxes = user[13]
        wood_workers = user[14] if len(user) > 14 else 0
        stone_workers = user[15] if len(user) > 15 else 0
        stone = user[5]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚒️ Управление рабочими", callback_data="manage_mine")],
            [InlineKeyboardButton(text="🛒 Купить кирку (75💰)", callback_data="buy_pickaxe")],
            [InlineKeyboardButton(text="⚒️ Начать добычу", callback_data="start_mine_harvest")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
        ])
        
        text = f"<b>🏭 Каменная шахта</b>\n\n⛏️ <b>Кирок:</b> {pickaxes}\n👷 <b>На дереве:</b> {wood_workers}\n👷 <b>На камне:</b> {stone_workers}/{pickaxes}\n🪨 <b>Камня:</b> {stone}\n\n<b>Добыча камня:</b> раз в 5 минут\n<i>Кирки нужны для добычи камня!</i>"
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "repair_mine_start")
async def repair_mine(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    if user[10] < 250 or user[3] < 300 or user[4] < 500:
        await callback.answer("Недостаточно ресурсов!", show_alert=True)
        return
    
    db.update_user(
        callback.from_user.id,
        coins=user[10] - 250,
        wood=user[3] - 300,
        energy=user[4] - 500,
        mine_repaired=1
    )
    
    await callback.answer("Начинаем ремонт...", show_alert=True)
    await callback.message.edit_text("🔧 <b>Ремонт шахты начался!</b>\n⏱️ <b>Время:</b> 5 минут", parse_mode="HTML")
    
    await asyncio.sleep(300)
    
    db.update_user(callback.from_user.id, mine_repaired=2)
    await callback.message.answer("✅ <b>Шахта отремонтирована!</b>\n🏭 <b>Можно добывать камень!</b>", parse_mode="HTML")

@router.callback_query(F.data == "manage_mine")
async def manage_mine(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    villagers = user[2]
    wood_workers = user[14] if len(user) > 14 else 0
    stone_workers = user[15] if len(user) > 15 else 0
    pickaxes = user[13]
    free_workers = villagers - wood_workers - stone_workers
    
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
        [InlineKeyboardButton(text="🔙 Назад", callback_data="mine_back")]
    ])
    
    text = f"<b>⚒️ Управление рабочими</b>\n\n👥 <b>Всего жителей:</b> {villagers}\n🆓 <b>Свободно:</b> {free_workers}\n\n<b>Текущее:</b>\n• 🪵 Дерево: {wood_workers}\n• 🪨 Камень: {stone_workers}/{pickaxes}\n\n<i>Для камня нужны кирки!</i>"
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "mine_wood_add")
async def mine_wood_add(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    villagers = user[2]
    wood_workers = user[14] if len(user) > 14 else 0
    stone_workers = user[15] if len(user) > 15 else 0
    
    if wood_workers + stone_workers < villagers:
        db.update_user(callback.from_user.id, mine_wood_workers=wood_workers + 1)
        await manage_mine(callback, db)
    else:
        await callback.answer("Нет свободных рабочих!", show_alert=True)
    await callback.answer()

@router.callback_query(F.data == "mine_wood_remove")
async def mine_wood_remove(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    wood_workers = user[14] if len(user) > 14 else 0
    
    if wood_workers > 0:
        db.update_user(callback.from_user.id, mine_wood_workers=wood_workers - 1)
        await manage_mine(callback, db)
    await callback.answer()

@router.callback_query(F.data == "mine_stone_add")
async def mine_stone_add(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    villagers = user[2]
    wood_workers = user[14] if len(user) > 14 else 0
    stone_workers = user[15] if len(user) > 15 else 0
    pickaxes = user[13]
    
    if stone_workers >= pickaxes:
        await callback.answer(f"Недостаточно кирок! Есть {pickaxes}", show_alert=True)
        return
    
    if wood_workers + stone_workers < villagers:
        db.update_user(callback.from_user.id, mine_stone_workers=stone_workers + 1)
        await manage_mine(callback, db)
    else:
        await callback.answer("Нет свободных рабочих!", show_alert=True)
    await callback.answer()

@router.callback_query(F.data == "mine_stone_remove")
async def mine_stone_remove(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    stone_workers = user[15] if len(user) > 15 else 0
    
    if stone_workers > 0:
        db.update_user(callback.from_user.id, mine_stone_workers=stone_workers - 1)
        await manage_mine(callback, db)
    await callback.answer()

@router.callback_query(F.data == "start_mine_harvest")
async def start_mine_harvest(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    if user[8]:
        last_mine = datetime.fromisoformat(user[8])
        time_since = datetime.now() - last_mine
        if time_since.total_seconds() < 300:
            time_left = 300 - int(time_since.total_seconds())
            await callback.answer(f"⏳ Жди еще {time_left} секунд!", show_alert=True)
            return
    
    wood_workers = user[14] if len(user) > 14 else 0
    stone_workers = user[15] if len(user) > 15 else 0
    
    if wood_workers == 0 and stone_workers == 0:
        await callback.answer("Нет рабочих в шахте!", show_alert=True)
        return
    
    wood_per_worker = random.randint(1, 3)
    stone_per_worker = random.randint(1, 2)
    
    total_wood = wood_per_worker * wood_workers
    total_stone = stone_per_worker * stone_workers
    
    db.update_user(
        callback.from_user.id,
        wood=user[3] + total_wood,
        stone=user[5] + total_stone,
        last_mine=datetime.now().isoformat()
    )
    
    new_user = db.get_user(callback.from_user.id)
    
    text = f"<b>✅ Добыча завершена!</b>\n\n👷 <b>Работало:</b>\n• 🪵 На дереве: {wood_workers}\n• 🪨 На камне: {stone_workers}\n\n<b>Добыто:</b>\n• 🪵 Древесина: +{total_wood}\n• 🪨 Камень: +{total_stone}\n\n<b>Итого:</b>\n• 🪵 {new_user[3]}\n• 🪨 {new_user[5]}"
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ]), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "mine_back")
async def mine_back(callback: CallbackQuery, db):
    await mine_command(callback.message, db)
