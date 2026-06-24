from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import get_all_panels, delete_panel
from api_client import delete_hosting_user
from aiogram import Bot
import logging

logger = logging.getLogger(__name__)

async def check_and_purge_expired_panels(bot: Bot):
    panels = await get_all_panels()
    now = datetime.now()

    for user_id, server_id, expires_at in panels:
        try:
            exp_date = datetime.strptime(expires_at.strip(), "%Y-%m-%d")

            if now > exp_date:
                removed = await delete_hosting_user(server_id)

                if removed:
                    await delete_panel(server_id)

                    try:
                        await bot.send_message(
                            user_id,
                            f"⚠️ Panel {server_id} expired and has been removed."
                        )
                    except:
                        pass

        except Exception as e:
            logger.error(f"Scheduler Error: {e}")

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_and_purge_expired_panels,
        "interval",
        hours=1,
        args=[bot]
    )
    scheduler.start()