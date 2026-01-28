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
        token=os.getenv('BOT_TOKEN'),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    db = Database()
    
    dp.include_router(handlers.router)
    
    dp['db'] = db
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())