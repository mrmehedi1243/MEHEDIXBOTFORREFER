from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import get_user, update_credits, add_panel, get_user_panels
from api_client import create_hosting_user
from untils.helpers import is_valid_username
from keyboards.user import main_menu_keyboard
from config import ADMIN_ID

router = Router()

class PanelCreationSR(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()


@router.message(F.text == "👤 Profile")
async def show_profile(message: Message):
    u_db = await get_user(message.from_user.id)
    panels = await get_user_panels(message.from_user.id)

    from database import get_referral_count
    total_refs = await get_referral_count(message.from_user.id)

    credits = "∞" if message.from_user.id == ADMIN_ID else (u_db["credits"] if u_db else 0)

    profile_text = (
        "👤 **BDX User Profile**\n\n"
        f"🆔 **User ID:** `{message.from_user.id}`\n"
        f"📈 **Total Referrals:** `{total_refs}`\n"
        f"🎫 **Panel Credits:** `{credits}`\n"
        f"📂 **Active Deployments:** `{len(panels)}`"
    )

    await message.answer(profile_text, parse_mode="Markdown")


@router.message(F.text == "📂 My Panels")
async def list_panels(message: Message):
    panels = await get_user_panels(message.from_user.id)

    if not panels:
        await message.answer(
            "❌ You don't have any active environments running."
        )
        return

    text = "📂 **Your Active Deployments:**\n\n"

    for p in panels:
        text += (
            f"🌐 **URL:** {p[3]}\n"
            f"🆔 **Server ID:** `{p[0]}`\n"
            f"👤 **User:** `{p[1]}`\n"
            f"🏷️ **Type:** `{p[2]}`\n"
            f"📅 **Expiry:** `{p[4]}`\n\n"
        )

    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "🎯 Support")
async def support_info(message: Message):
    await message.answer(
        "🛠️ For help, support or SLA concerns, contact @proxaura."
    )


@router.message(F.text == "🚀 Create Panel")
async def init_panel_build(message: Message, state: FSMContext):
    u_db = await get_user(message.from_user.id)

    if message.from_user.id != ADMIN_ID:
        if not u_db or u_db["credits"] < 1:
            await message.answer(
                "❌ Insufficient credits! Invite users to earn hosting resources."
            )
            return

    await message.answer(
        "📝 Enter a unique **Username** for your new panel:"
    )

    await state.set_state(
        PanelCreationSR.waiting_for_username
    )


@router.message(PanelCreationSR.waiting_for_username)
async def process_p_user(message: Message, state: FSMContext):
    user_input = message.text.strip()

    if not is_valid_username(user_input):
        await message.answer(
            "❌ Invalid characters! Use alphanumeric entries between 3-15 symbols."
        )
        return

    await state.update_data(
        p_username=user_input
    )

    await message.answer(
        "🔒 Set a secure operational **Password**:"
    )

    await state.set_state(
        PanelCreationSR.waiting_for_password
    )


@router.message(PanelCreationSR.waiting_for_password)
async def process_p_pass(message: Message, state: FSMContext):
    password = message.text.strip()

    if len(password) < 6:
        await message.answer(
            "❌ Weak security. Choose a password with at least 6 characters."
        )
        return

    data = await state.get_data()
    p_user = data["p_username"]

    await state.clear()

    status_msg = await message.answer(
        "⚙️ *Processing environment provisioning pipeline... Please wait.*",
        parse_mode="Markdown"
    )

    res = await create_hosting_user(
        username=p_user,
        password=password,
        server_type="python"
    )

    if res and res.get("status") == "created":
        u_info = res["user"]

        await add_panel(
            user_id=message.from_user.id,
            server_id=u_info["server_id"],
            username=u_info["username"],
            server_type=u_info["server_type"],
            url=u_info["url"],
            expires_at=u_info["expires_at"]
        )

        if message.from_user.id != ADMIN_ID:
            await update_credits(
                message.from_user.id,
                -1
            )

        success_txt = (
            "🚀 **Environment Deployed Successfully!**\n\n"
            f"🔗 **URL:** {u_info['url']}\n"
            f"🆔 **Server ID:** `{u_info['server_id']}`\n"
            f"👤 **Username:** `{u_info['username']}`\n"
            f"🔑 **Password:** `{password}`\n"
            f"📅 **Expiry Date:** `{u_info['expires_at']}`"
        )

        await status_msg.edit_text(
            success_txt,
            parse_mode="Markdown"
        )

    else:
        await status_msg.edit_text(
            "❌ Cloud execution runtime cluster returned internal deployment system failures."
        )