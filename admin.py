# <-- АДМИН ПАНЕЛЬ -->
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

ADMIN_ID = 7536945356

def is_admin(user_id):
    return user_id == ADMIN_ID

@router.message(Command("admin"))
async def admin_panel(message: Message, db):
    if not is_admin(message.from_user.id):
        return
    
    text = "<b>🔧 Админ панель</b>\n\n"
    text += "<b>Команды:</b>\n"
    text += "/add_resources [id] [wood] [energy] [stone] [coins]\n"
    text += "/set_resources [id] [wood] [energy] [stone] [coins]\n"
    text += "/add_villagers [id] [amount]\n"
    text += "/set_level [id] [level]\n"
    text += "/add_territory [id] [amount]\n"
    text += "/add_pickaxes [id] [amount]\n"
    text += "/repair_mine [id]\n"
    text += "/reset_user [id]\n"
    text += "/user_info [id]\n"
    
    await message.answer(text, parse_mode="HTML")

@router.message(Command("add_resources"))
async def add_resources(message: Message, db):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 6:
        await message.answer("❌ /add_resources [id] [wood] [energy] [stone] [coins]")
        return
    
    try:
        user_id = int(args[1])
        wood = int(args[2])
        energy = int(args[3])
        stone = int(args[4])
        coins = int(args[5])
    except:
        await message.answer("❌ Неверные аргументы")
        return
    
    user = db.get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    db.update_user(
        user_id,
        wood=user[3] + wood,
        energy=user[4] + energy,
        stone=user[5] + stone,
        coins=user[10] + coins
    )
    
    await message.answer(f"✅ Ресурсы добавлены пользователю {user_id}\n🪵 +{wood} 🌞 +{energy} 🪨 +{stone} 🪙 +{coins}")

@router.message(Command("set_resources"))
async def set_resources(message: Message, db):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 6:
        await message.answer("❌ /set_resources [id] [wood] [energy] [stone] [coins]")
        return
    
    try:
        user_id = int(args[1])
        wood = int(args[2])
        energy = int(args[3])
        stone = int(args[4])
        coins = int(args[5])
    except:
        await message.answer("❌ Неверные аргументы")
        return
    
    user = db.get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    db.update_user(
        user_id,
        wood=wood,
        energy=energy,
        stone=stone,
        coins=coins
    )
    
    await message.answer(f"✅ Ресурсы установлены для {user_id}\n🪵 {wood} 🌞 {energy} 🪨 {stone} 🪙 {coins}")

@router.message(Command("add_villagers"))
async def add_villagers(message: Message, db):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ /add_villagers [id] [amount]")
        return
    
    try:
        user_id = int(args[1])
        amount = int(args[2])
    except:
        await message.answer("❌ Неверные аргументы")
        return
    
    user = db.get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    db.update_user(user_id, villagers=user[2] + amount)
    await message.answer(f"✅ Добавлено {amount} жителей пользователю {user_id}")

@router.message(Command("set_level"))
async def set_level(message: Message, db):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ /set_level [id] [level]")
        return
    
    try:
        user_id = int(args[1])
        level = int(args[2])
    except:
        await message.answer("❌ Неверные аргументы")
        return
    
    user = db.get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    db.update_user(user_id, village_level=level)
    await message.answer(f"✅ Уровень установлен {level} для {user_id}")

@router.message(Command("add_territory"))
async def add_territory(message: Message, db):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ /add_territory [id] [amount]")
        return
    
    try:
        user_id = int(args[1])
        amount = int(args[2])
    except:
        await message.answer("❌ Неверные аргументы")
        return
    
    user = db.get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    db.update_user(user_id, territory=user[11] + amount)
    await message.answer(f"✅ Добавлено {amount} территорий для {user_id}")

@router.message(Command("add_pickaxes"))
async def add_pickaxes(message: Message, db):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ /add_pickaxes [id] [amount]")
        return
    
    try:
        user_id = int(args[1])
        amount = int(args[2])
    except:
        await message.answer("❌ Неверные аргументы")
        return
    
    user = db.get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    db.update_user(user_id, pickaxes=user[13] + amount)
    await message.answer(f"✅ Добавлено {amount} кирок для {user_id}")

@router.message(Command("repair_mine"))
async def repair_mine_admin(message: Message, db):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /repair_mine [id]")
        return
    
    try:
        user_id = int(args[1])
    except:
        await message.answer("❌ Неверный ID")
        return
    
    user = db.get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    db.update_user(user_id, mine_repaired=2)
    await message.answer(f"✅ Шахта отремонтирована для {user_id}")

@router.message(Command("reset_user"))
async def reset_user(message: Message, db):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /reset_user [id]")
        return
    
    try:
        user_id = int(args[1])
    except:
        await message.answer("❌ Неверный ID")
        return
    
    db.update_user(
        user_id,
        villagers=1,
        wood=10,
        energy=5,
        stone=0,
        workers=0,
        last_harvest=None,
        last_mine=None,
        village_level=0,
        coins=0,
        territory=0,
        mine_repaired=0,
        pickaxes=0,
        mine_wood_workers=0,
        mine_stone_workers=0
    )
    
    await message.answer(f"✅ Пользователь {user_id} сброшен")

@router.message(Command("user_info"))
async def user_info(message: Message, db):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /user_info [id]")
        return
    
    try:
        user_id = int(args[1])
    except:
        await message.answer("❌ Неверный ID")
        return
    
    user = db.get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    text = f"<b>📊 Информация о пользователе {user_id}</b>\n\n"
    text += f"👤 <b>Никнейм:</b> {user[1]}\n"
    text += f"👥 <b>Жители:</b> {user[2]}\n"
    text += f"🪵 <b>Древесина:</b> {user[3]}\n"
    text += f"🌞 <b>Энергия:</b> {user[4]}\n"
    text += f"🪨 <b>Камень:</b> {user[5]}\n"
    text += f"👷 <b>Рабочие:</b> {user[6]}/{user[2]}\n"
    text += f"🏠 <b>Уровень:</b> {user[9]}\n"
    text += f"🪙 <b>Монеты:</b> {user[10]}\n"
    text += f"🏞️ <b>Территории:</b> {user[11]}\n"
    text += f"🏭 <b>Шахта:</b> {user[12]}\n"
    text += f"⛏️ <b>Кирок:</b> {user[13]}\n"
    text += f"🪵 <b>В шахте на дереве:</b> {user[14] if len(user) > 14 else 0}\n"
    text += f"🪨 <b>В шахте на камне:</b> {user[15] if len(user) > 15 else 0}"
    
    await message.answer(text, parse_mode="HTML")
