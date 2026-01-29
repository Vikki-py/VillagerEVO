# <-- ЭКОНОМИКА -->
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def wood_to_coins(wood_amount):
    return wood_amount * 2

def territory_price(current_territory):
    base_price = 50
    return base_price + (current_territory * 10)

@router.callback_query(F.data == "market")
async def show_market(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    level = user[9] if len(user) > 9 else 0
    mine_repaired = user[12] if len(user) > 12 else 0
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="💰 1🪵=2🪙", callback_data="sell_wood_1"),
        InlineKeyboardButton(text="💰 5🪵=10🪙", callback_data="sell_wood_5")
    ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="💰 10🪵=20🪙", callback_data="sell_wood_10"),
        InlineKeyboardButton(text="💰 Всё", callback_data="sell_wood_all")
    ])
    
    if mine_repaired >= 2:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="💰 1🪨=3🪙", callback_data="sell_stone_1"),
            InlineKeyboardButton(text="💰 5🪨=15🪙", callback_data="sell_stone_5")
        ])
    
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
    
    stone = user[5] if len(user) > 5 else 0
    pickaxes = user[13] if len(user) > 13 else 0
    
    text = f"<b>🏪 Рынок</b>\n\n🪵 <b>Древесина:</b> {user[3]}\n🪙 <b>Монеты:</b> {user[10] if len(user) > 10 else 0}\n🏞️ <b>Территории:</b> {user[11] if len(user) > 11 else 0}"
    
    if mine_repaired >= 2:
        text += f"\n🪨 <b>Камень:</b> {stone}\n⛏️ <b>Кирок:</b> {pickaxes}"
    
    text += f"\n\n<b>Торговец покупает:</b>\n• 1 🪵 = 2 🪙"
    
    if mine_repaired >= 2:
        text += f"\n• 1 🪨 = 3 🪙"
    
    price = territory_price(user[11] if len(user) > 11 else 0)
    text += f"\n\n<b>Территория:</b>\n• Цена: {price} 🪙"
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("sell_wood_"))
async def sell_wood(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    wood_available = user[3]
    
    action = callback.data.split("_")[2]
    
    if action == "all":
        if wood_available == 0:
            await callback.answer("Нет древесины!", show_alert=True)
            return
        
        coins_gained = wood_to_coins(wood_available)
        db.update_user(
            callback.from_user.id,
            wood=0,
            coins=user[10] + coins_gained
        )
        
        text = f"<b>✅ Вся древесина продана!</b>\n\n🪵 <b>Продано:</b> {wood_available}\n🪙 <b>Получено:</b> +{coins_gained} монет"
    
    else:
        amount = int(action)
        if wood_available < amount:
            await callback.answer(f"Недостаточно! У вас {wood_available}", show_alert=True)
            return
        
        coins_gained = wood_to_coins(amount)
        db.update_user(
            callback.from_user.id,
            wood=wood_available - amount,
            coins=user[10] + coins_gained
        )
        
        text = f"<b>✅ Древесина продана!</b>\n\n🪵 <b>Продано:</b> {amount}\n🪙 <b>Получено:</b> +{coins_gained} монет"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("sell_stone_"))
async def sell_stone(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    stone_available = user[5] if len(user) > 5 else 0
    
    action = callback.data.split("_")[2]
    
    if action == "all":
        if stone_available == 0:
            await callback.answer("Нет камня!", show_alert=True)
            return
        
        coins_gained = stone_available * 3
        db.update_user(
            callback.from_user.id,
            stone=0,
            coins=user[10] + coins_gained
        )
        
        text = f"<b>✅ Весь камень продан!</b>\n\n🪨 <b>Продано:</b> {stone_available}\n🪙 <b>Получено:</b> +{coins_gained} монет"
    
    else:
        amount = int(action)
        if stone_available < amount:
            await callback.answer(f"Недостаточно! У вас {stone_available}", show_alert=True)
            return
        
        coins_gained = amount * 3
        db.update_user(
            callback.from_user.id,
            stone=stone_available - amount,
            coins=user[10] + coins_gained
        )
        
        text = f"<b>✅ Камень продан!</b>\n\n🪨 <b>Продано:</b> {amount}\n🪙 <b>Получено:</b> +{coins_gained} монет"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "buy_territory")
async def buy_territory(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    current_territory = user[11] if len(user) > 11 else 0
    current_coins = user[10] if len(user) > 10 else 0
    price = territory_price(current_territory)
    
    if current_coins < price:
        await callback.answer(f"Недостаточно! Нужно {price}, у вас {current_coins}", show_alert=True)
        return
    
    db.update_user(
        callback.from_user.id,
        territory=current_territory + 1,
        coins=current_coins - price
    )
    
    new_user = db.get_user(callback.from_user.id)
    next_price = territory_price(new_user[11])
    
    text = f"<b>✅ Территория куплена!</b>\n\n🏞️ <b>Теперь территорий:</b> {new_user[11]}\n💰 <b>Потрачено:</b> {price} монет\n💰 <b>Осталось:</b> {new_user[10]}\n\n<b>Следующая территория:</b>\n• Цена: {next_price} 🪙\n\n<i>Теперь можно улучшать деревню дальше!</i>"
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в рынок", callback_data="market")]
    ]), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "buy_pickaxe")
async def buy_pickaxe(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    
    if user[10] < 75:
        await callback.answer("Нужно 75 монет!", show_alert=True)
        return
    
    db.update_user(
        callback.from_user.id,
        coins=user[10] - 75,
        pickaxes=user[13] + 1
    )
    
    await callback.answer("✅ Куплена кирка!", show_alert=True)
    await show_market(callback, db)
