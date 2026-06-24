from aiogram import Bot
from database import get_channels

async def check_force_join(bot: Bot, user_id: int) -> list:
    """Returns a list of channel tuples (id, username) that user has NOT joined."""
    channels = await get_channels()
    not_joined = []
    
    for ch_id, ch_username in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch_id, user_id=user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append((ch_id, ch_username))
        except Exception:
            # If bot cannot check (e.g. not admin in channel), flag it to protect system integrity
            not_joined.append((ch_id, ch_username))
            
    return not_joined
