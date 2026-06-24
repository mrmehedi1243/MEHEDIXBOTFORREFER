import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import start, referral, panel, admin
from scheduler import setup_scheduler

# Core execution configurations
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def main():
    # Structural local database initialization 
    init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Registration pipelines
    dp.include_router(start.router)
    dp.include_router(referral.router)
    dp.include_router(panel.router)
    dp.include_router(admin.router)
    
    # Run routine lifecycle management workers
    setup_scheduler(bot)
    
    logging.info("BDX Telegram Core Server Initialization Complete. Starting pooling engine loops...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
