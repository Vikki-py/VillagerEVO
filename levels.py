from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from html import escape

router = Router()

def calculate_upgrade_cost(level):
    wood_cost = 10 + (level * 4)
    energy_cost = 5 + (level * 3)
    return wood_cost, energy_cost

def can_upgrade(user, current_level):
    if current_level >= 5:
        return False
    
    wood_cost, energy_cost = calculate_upgrade_cost(current_level)
    return user[4] >= wood_cost and user[5] >= energy_cost

@router.callback_query(F.data == "upgrades")
async def show_upgrades(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    level = user[7] if len(user) > 7 else 0
    
    wood_cost, energy_cost = calculate_upgrade_cost(level)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    if level < 5:
        if can_upgrade(user, level):
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text=f"⬆️ Улучшить деревню ({wood_cost} 🪵, {energy_cost} 🌞)", callback_data="upgrade_village")
            ])
        else:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text=f"❌ Недостаточно ресурсов", callback_data="none")
            ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    ])
    
    text = (
        f"<b>🏗️ Улучшения деревни</b>\n\n"
        f"🏠 <b>Уровень деревни:</b> {level}/5\n"
        f"🗺️ <b>Свободная территория:</b> {5 - level} клеток\n\n"
    )
    
    if level < 5:
        text += (
            f"<b>Следующее улучшение:</b>\n"
            f"• 🪵 Древесина: {wood_cost}\n"
            f"• 🌞 Энергия: {energy_cost}\n\n"
            f"<i>Улучшай деревню, чтобы открывать новые постройки!</i>"
        )
    else:
        text += (
            f"<b>🎉 Максимальный уровень!</b>\n"
            f"<i>Купите дополнительную территорию для дальнейшего развития</i>"
        )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "upgrade_village")
async def upgrade_village(callback: CallbackQuery, db):
    user = db.get_user(callback.from_user.id)
    level = user[7] if len(user) > 7 else 0
    
    if level >= 5:
        await callback.answer("❌ Нет свободной территории!", show_alert=True)
        return
    
    wood_cost, energy_cost = calculate_upgrade_cost(level)
    
    if user[4] < wood_cost or user[5] < energy_cost:
        await callback.answer("❌ Недостаточно ресурсов!", show_alert=True)
        return
    
    db.update_user(
        callback.from_user.id,
        wood=user[4] - wood_cost,
        energy=user[5] - energy_cost,
        village_level=level + 1
    )
    
    new_level = level + 1
    next_wood, next_energy = calculate_upgrade_cost(new_level)
    
    text = (
        f"<b>✅ Деревня улучшена!</b>\n\n"
        f"🏠 <b>Новый уровень:</b> {new_level}/5\n"
        f"🗺️ <b>Свободная территория:</b> {5 - new_level} клеток\n\n"
        f"<b>Затрачено:</b>\n"
        f"• 🪵 Древесина: {wood_cost}\n"
        f"• 🌞 Энергия: {energy_cost}\n\n"
    )
    
    if new_level < 5:
        text += (
            f"<b>Следующее улучшение:</b>\n"
            f"• 🪵 Древесина: {next_wood}\n"
            f"• 🌞 Энергия: {next_energy}"
        )
    else:
        text += (
            f"<b>🎉 Достигнут максимальный уровень!</b>\n"
            f"<i>Для дальнейшего развития нужна дополнительная территория</i>"
        )
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ]), parse_mode="HTML")
    await callback.answer()
