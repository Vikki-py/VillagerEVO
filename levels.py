# <-- СИСТЕМА УРОВНЕЙ -->

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def calculate_upgrade_cost(level):
    if level is None:
        level = 0
    wood_cost = 10 + (level * 4)
    energy_cost = 5 + (level * 3)
    return wood_cost, energy_cost

def can_upgrade(user, current_level):
    if current_level is None:
        current_level = 0
    
    if current_level >= 5:
        return False
    
    wood_cost, energy_cost = calculate_upgrade_cost(current_level)
    wood = user[4] if len(user) > 4 else 10
    energy = user[5] if len(user) > 5 else 50
    return wood >= wood_cost and energy >= energy_cost

@router.callback_query(F.data == "upgrades")
async def show_upgrades(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    level = user[8] if len(user) > 8 else 0
    
    wood_cost, energy_cost = calculate_upgrade_cost(level)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    if level < 5:
        if can_upgrade(user, level):
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text=f"⬆️ Улучшить ({wood_cost}🪵, {energy_cost}🌞)", callback_data="upgrade_village")
            ])
        else:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text="❌ Недостаточно", callback_data="none")
            ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    ])
    
    text = (
        f"<b>🏗️ Улучшения</b>\n\n"
        f"🏠 <b>Уровень:</b> {level}/5\n"
        f"🗺️ <b>Свободно:</b> {5 - level}\n\n"
    )
    
    if level < 5:
        text += (
            f"<b>Следующее:</b>\n"
            f"• 🪵 {wood_cost}\n"
            f"• 🌞 {energy_cost}\n\n"
            f"<i>Улучшай деревню!</i>"
        )
    else:
        text += (
            f"<b>🎉 Максимум!</b>\n"
            f"<i>Купите территорию в рынке</i>"
        )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "upgrade_village")
async def upgrade_village(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    level = user[8] if len(user) > 8 else 0
    
    if level >= 5:
        await callback.answer("❌ Нет территории!", show_alert=True)
        return
    
    wood_cost, energy_cost = calculate_upgrade_cost(level)
    
    wood = user[4] if len(user) > 4 else 10
    energy = user[5] if len(user) > 5 else 50
    
    if wood < wood_cost or energy < energy_cost:
        await callback.answer("❌ Недостаточно!", show_alert=True)
        return
    
    db.update_user(
        callback.from_user.id,
        wood=wood - wood_cost,
        energy=energy - energy_cost,
        village_level=level + 1
    )
    
    new_level = level + 1
    next_wood, next_energy = calculate_upgrade_cost(new_level)
    
    text = (
        f"<b>✅ Улучшено!</b>\n\n"
        f"🏠 <b>Уровень:</b> {new_level}/5\n"
        f"🗺️ <b>Свободно:</b> {5 - new_level}\n\n"
        f"<b>Затрачено:</b>\n"
        f"• 🪵 {wood_cost}\n"
        f"• 🌞 {energy_cost}\n\n"
    )
    
    if new_level < 5:
        text += (
            f"<b>Следующее:</b>\n"
            f"• 🪵 {next_wood}\n"
            f"• 🌞 {next_energy}"
        )
    else:
        text += (
            f"<b>🎉 Максимум!</b>\n"
            f"<i>Купите территорию в рынке</i>"
        )
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ]), parse_mode="HTML")
    await callback.answer()
