import re
from aiogram import Router, F
from aiogram.types import Message

router = Router()

def is_valid_nickname(nickname):
    if not (3 <= len(nickname) <= 12):
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', nickname):
        return False
    return True

@router.message(F.text.lower().in_(["ник", "н"]))
async def show_nickname(message: Message, db):
    user = db.get_user(message.from_user.id)
    nickname = user[2]
    await message.answer(f"🍀 <b>Ваш никнейм:</b> <code>{nickname}</code>")

@router.message(F.text.lower().startswith("сменить ник "))
async def change_nickname_text(message: Message, db):
    new_nick = message.text[11:].strip()
    
    if not new_nick:
        await message.answer("❌ <b>Укажите новый никнейм после</b> '<code>сменить ник</code> '")
        return
    
    if not is_valid_nickname(new_nick):
        await message.answer("❌ <b>Никнейм должен быть 3-12 символов, только латиница, цифры и _</b>")
        return
    
    db.update_nickname(message.from_user.id, new_nick)
    await message.answer(f"✅ Никнейм изменен на: <code>{new_nick}</code>")
