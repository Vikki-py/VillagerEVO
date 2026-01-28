# <-- ЭКОНОМИКА -->

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from html import escape

router = Router()

def wood_to_coins(wood_amount):
    return wood_amount * 2

def territory_price(current_territory):
    base_price = 50
    return base_price + (current_territory * 10)

@router.callback_query(F.data == "market")
async def show_market(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    level = user[10] if len(user) > 10 else 0
    mine_repaired = user[13] if len(user) > 13 else 0
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    wood_row = []
    wood_row.append(InlineKeyboardButton(text="💰 1🪵=2🪙", callback_data="sell_wood_1"))
    wood_row.append(InlineKeyboardButton(text="💰 5🪵=10🪙", callback_data="sell_wood_5"))
    keyboard.inline_keyboard.append(wood_row)
    
    wood_row2 = []
    wood_row2.append(InlineKeyboardButton(text="💰 10🪵=20🪙", callback_data="sell_wood_10"))
    wood_row2.append(InlineKeyboardButton(text="💰 Всё", callback_data="sell_wood_all"))
    keyboard.inline_keyboard.append(wood_row2)
    
    if mine_repaired >= 2:
        stone_row = []
        stone_row.append(InlineKeyboardButton(text="💰 1🪨=3🪙", callback_data="sell_stone_1"))
        stone_row.append(InlineKeyboardButton(text="💰 5🪨=15🪙", callback_data="sell_stone_5"))
        keyboard.inline_keyboard.append(stone_row)
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🏞️ Купить территорию", callback_data="buy_territory")
    ])
    
    if level >= 10 and mine_repaired >= 2:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⛏️ Купить кирку (75💰)", callback_data="buy_pickaxe")
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    ])
    
    stone = user[6] if len(user) > 6 else 0
    pickaxes = user[14] if len(user) > 14 else 0
    
    text = f"<b>🏪 Рынок</b>\n\n🪵 <b>Древесина:</b> {user[4]}\n🪙 <b>Монеты:</b> {user[9] if len(user) > 9 else 0}\n🏞️ <b>Территории:</b> {user[11] if len(user) > 11 else 0}"
    
    if mine_repaired >= 2:
        text += f"\n🪨 <b>Камень:</b> {stone}\n⛏️ <b>Кирок:</b> {pickaxes}"
    
    text += f"\n\n<b>Торговец покупает:</b>\n• 1 🪵 = 2 🪙"
    
    if mine_repaired >= 2:
        text += f"\n• 1 🪨 = 3 🪙"
    
    price = 50 + ((user[11] if len(user) > 11 else 0) * 10)
    text += f"\n\n<b>Территория:</b>\n• Цена: {price} 🪙"
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("sell_wood_"))
async def sell_wood(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    wood_available = user[4]
    
    action = callback.data.split("_")[2]
    
    if action == "all":
        if wood_available == 0:
            await callback.answer("❌ Нет древесины для продажи!", show_alert=True)
            return
        
        coins_gained = wood_to_coins(wood_available)
        db.update_user(
            callback.from_user.id,
            wood=0,
            coins=user[9] + coins_gained
        )
        
        text = (
            f"<b>✅ Вся древесина продана!</b>\n\n"
            f"🪵 <b>Продано:</b> {wood_available}\n"
            f"🪙 <b>Получено:</b> +{coins_gained} монет\n"
            f"💰 <b>Всего монет:</b> {user[9] + coins_gained}"
        )
    
    else:
        amount = int(action)
        if wood_available < amount:
            await callback.answer(f"❌ Недостаточно древесины! У вас {wood_available}", show_alert=True)
            return
        
        coins_gained = wood_to_coins(amount)
        db.update_user(
            callback.from_user.id,
            wood=wood_available - amount,
            coins=user[9] + coins_gained
        )
        
        text = (
            f"<b>✅ Древесина продана!</b>\n\n"
            f"🪵 <b>Продано:</b> {amount}\n"
            f"🪙 <b>Получено:</b> +{coins_gained} монет\n"
            f"💰 <b>Осталось древесины:</b> {wood_available - amount}\n"
            f"💰 <b>Всего монет:</b> {user[9] + coins_gained}"
        )
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в рынок", callback_data="market")]
    ]), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "buy_territory")
async def buy_territory(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    current_territory = user[10] if len(user) > 10 else 0
    current_coins = user[9] if len(user) > 9 else 0
    price = territory_price(current_territory)
    
    if current_coins < price:
        await callback.answer(f"❌ Недостаточно монет! Нужно {price}, у вас {current_coins}", show_alert=True)
        return
    
    db.update_user(
        callback.from_user.id,
        territory=current_territory + 1,
        coins=current_coins - price
    )
    
    new_user = db.get_user(callback.from_user.id)
    next_price = territory_price(new_user[10])
    
    text = (
        f"<b>✅ Территория куплена!</b>\n\n"
        f"🏞️ <b>Теперь территорий:</b> {new_user[10]}\n"
        f"💰 <b>Потрачено:</b> {price} монет\n"
        f"💰 <b>Осталось монет:</b> {new_user[9]}\n\n"
        f"<b>Следующая территория:</b>\n"
        f"• Стоимость: {next_price} 🪙\n\n"
        f"<i>Теперь можно улучшать деревню дальше!</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в рынок", callback_data="market")]
    ]), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("sell_stone_"))
async def sell_stone(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    stone_available = user[6] if len(user) > 6 else 0
    
    action = callback.data.split("_")[2]
    
    if action == "all":
        if stone_available == 0:
            await callback.answer("Нет камня!", show_alert=True)
            return
        
        coins_gained = stone_available * 3
        db.update_user(
            callback.from_user.id,
            stone=0,
            coins=user[9] + coins_gained
        )
        
        text = f"<b>✅ Весь камень продан!</b>\n\n🪨 <b>Продано:</b> {stone_available}\n🪙 <b>Получено:</b> +{coins_gained} монет"
    
    else:
        amount = int(action)
        if stone_available < amount:
            await callback.answer(f"Недостаточно камня! У вас {stone_available}", show_alert=True)
            return
        
        coins_gained = amount * 3
        db.update_user(
            callback.from_user.id,
            stone=stone_available - amount,
            coins=user[9] + coins_gained
        )
        
        text = f"<b>✅ Камень продан!</b>\n\n🪨 <b>Продано:</b> {amount}\n🪙 <b>Получено:</b> +{coins_gained} монет"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()
