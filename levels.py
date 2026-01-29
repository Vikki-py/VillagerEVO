# <-- УРОВНИ -->
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def calculate_upgrade_cost(level):
    wood_cost = 10 + (level * 4)
    energy_cost = 5 + (level * 3)
    return wood_cost, energy_cost

def get_max_level(user):
    base_max = 5
    territory = user[11] if len(user) > 11 else 0
    return base_max + territory

@router.callback_query(F.data == "upgrades")
async def show_upgrades(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    level = user[9] if len(user) > 9 else 0
    max_level = get_max_level(user)
    territory = user[11] if len(user) > 11 else 0
    
    wood_cost, energy_cost = calculate_upgrade_cost(level)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    if level < max_level:
        if user[3] >= wood_cost and user[4] >= energy_cost:
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
    
    text = f"<b>🏗️ Улучшения</b>\n\n🏠 <b>Уровень:</b> {level}/{max_level}\n🗺️ <b>Территории:</b> {territory}\n\n"
    
    if level < max_level:
        text += f"<b>Следующее:</b>\n• 🪵 {wood_cost}\n• 🌞 {energy_cost}\n\n<i>Улучшай деревню!</i>"
    else:
        text += f"<b>🎉 Максимум!</b>\n<i>Купите территорию в рынке</i>"
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "upgrade_village")
async def upgrade_village(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    level = user[9] if len(user) > 9 else 0
    max_level = get_max_level(user)
    
    if level >= max_level:
        await callback.answer("Нет территории!", show_alert=True)
        return
    
    wood_cost, energy_cost = calculate_upgrade_cost(level)
    
    wood = user[3] if len(user) > 3 else 10
    energy = user[4] if len(user) > 4 else 50
    
    if wood < wood_cost or energy < energy_cost:
        await callback.answer("Недостаточно!", show_alert=True)
        return
    
    db.update_user(
        callback.from_user.id,
        wood=wood - wood_cost,
        energy=energy - energy_cost,
        village_level=level + 1
    )
    
    new_user = db.get_user(callback.from_user.id)
    new_level = new_user[9] if len(new_user) > 9 else 0
    next_wood, next_energy = calculate_upgrade_cost(new_level)
    new_max_level = get_max_level(new_user)
    
    text = f"<b>✅ Улучшено!</b>\n\n🏠 <b>Уровень:</b> {new_level}/{new_max_level}\n🗺️ <b>Территории:</b> {new_user[11] if len(new_user) > 11 else 0}\n\n<b>Затрачено:</b>\n• 🪵 {wood_cost}\n• 🌞 {energy_cost}\n\n"
    
    if new_level < new_max_level:
        text += f"<b>Следующее:</b>\n• 🪵 {next_wood}\n• 🌞 {next_energy}"
    else:
        text += f"<b>🎉 Максимум!</b>\n<i>Купите территорию в рынке</i>"
    
    if new_level == 10 and user[12] == 0:
        text += f"\n\n<b>🎉 Открыта шахта!</b>\nНапиши <b>шахта</b> чтобы осмотреть"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()
