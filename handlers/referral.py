from aiogram import Router, F
from aiogram.types import Message
from database import get_user, get_referral_count

router = Router()

@router.message(F.text == "📈 Referrals")
async def referral_menu(message: Message):
    user_id = message.from_user.id
    bot_info = await message.bot.get_me()
    
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    total_refs = await get_referral_count(user_id)
    
    msg = (
        "👥 **BDX Referral Program**\n\n"
        f"🔗 *Your Invite Link:* `{ref_link}`\n\n"
        f"📊 *Total Referrals:* `{total_refs}`\n"
        "🎁 *Reward System:* Get **1 Hosting Credit** for every **3 referrals**!\n\n"
        "💡 _Share your link with friends to get free hosting services._"
    )
    await message.answer(msg, parse_mode="Markdown")
