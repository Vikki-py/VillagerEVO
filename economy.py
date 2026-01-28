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
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Продать 1 🪵 (2 монеты)", callback_data="sell_wood_1"),
            InlineKeyboardButton(text="💰 Продать 5 🪵 (10 монет)", callback_data="sell_wood_5")
        ],
        [
            InlineKeyboardButton(text="💰 Продать 10 🪵 (20 монет)", callback_data="sell_wood_10"),
            InlineKeyboardButton(text="💰 Продать всё", callback_data="sell_wood_all")
        ],
        [
            InlineKeyboardButton(text="🏞️ Купить территорию", callback_data="buy_territory")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
        ]
    ])
    
    price = territory_price(user[10]) if len(user) > 10 else territory_price(0)
    
    text = (
        f"<b>🏪 Рынок</b>\n\n"
        f"🪵 <b>Древесина:</b> {user[4]}\n"
        f"🪙 <b>Монеты:</b> {user[9] if len(user) > 9 else 0}\n"
        f"🏞️ <b>Куплено территорий:</b> {user[10] if len(user) > 10 else 0}\n\n"
        f"<b>Торговец покупает:</b>\n"
        f"• 1 🪵 = 2 🪙 монеты\n\n"
        f"<b>Следующая территория:</b>\n"
        f"• Стоимость: {price} 🪙\n\n"
        f"<i>Продавай древесину за монеты и покупай новые земли!</i>"
    )
    
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
