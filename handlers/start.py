from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from database import add_user, add_referral
from untils.force_join import check_force_join
from keyboards.user import main_menu_keyboard, force_join_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    
    # Check for referral payloads
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
    
    # Save base user profile
    await add_user(user_id, username, referrer_id)
    
    if referrer_id and referrer_id != user_id:
        # Credit awarded via this helper operation asynchronously
        await add_referral(referrer_id, user_id)

    # Perform mandatory access control screening checks
    not_joined = await check_force_join(message.bot, user_id)
    if not_joined:
        await message.answer(
            "⚠️ **Access Blocked!** You must join our partner channels to unlock the bot features:",
            reply_markup=force_join_keyboard(not_joined),
            parse_mode="Markdown"
        )
        return

    await message.answer(
        f"👋 Welcome **{username}** to **BDX Hosting Bot**!\nDeploy environments dynamically right from Telegram.",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "verify_join")
async def verify_joining(callback: CallbackQuery):
    not_joined = await check_force_join(callback.bot, callback.from_user.id)
    if not_joined:
        await callback.answer("❌ Verification failed. You haven't joined all channels yet.", show_alert=True)
        return
        
    await callback.message.delete()
    await callback.message.answer(
        "✅ Verification Successful! Access granted.",
        reply_markup=main_menu_keyboard()
    )
