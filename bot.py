# <-- ГЛАВНЫЙ ФАЙЛ ЗАПУСКА -->

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from database import Database
import handlers
import os

async def main():
    bot = Bot(
        token="7840570452:AAHuaQo_3x_n3e878kLG1B2QRRSCmT26C9k",
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    db = Database()
    
    dp.include_router(handlers.router)
    dp.include_router(nickname.router)
    
    dp['db'] = db
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
