from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import ADMIN_ID
from database import get_global_stats, add_channel, remove_channel, get_channels, get_all_user_ids
from keyboards.admin import admin_panel_keyboard

router = Router()

class AdminSR(StatesGroup):
    waiting_for_ch_id = State()
    waiting_for_ch_user = State()
    waiting_for_rem_id = State()
    waiting_for_broadcast = State()

@router.message(Command("admin"))
async def admin_dashboard(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🛠️ **BDX Central Operations Center Engine**", reply_markup=admin_panel_keyboard(), parse_mode="Markdown")

@router.message(Command("stats"))
@router.callback_query(F.data == "adm_stats")
async def show_stats(event):
    uid = event.from_user.id if isinstance(event, Message) else event.from_user.id
    if uid != ADMIN_ID: return
    
    users, refs, panels = await get_global_stats()
    stats_text = (
        "📊 **Global Host Systems Analytics Overview**\n\n"
        f"👥 Total Users registered: `{users}`\n"
        f"📈 Total Network Referrals: `{refs}`\n"
        f"🚀 Active App Subcontainers: `{panels}`"
    )
    if isinstance(event, Message):
        await event.answer(stats_text, parse_mode="Markdown")
    else:
        await event.message.answer(stats_text, parse_mode="Markdown")
        await event.answer()

@router.callback_query(F.data == "adm_add_ch")
async def process_add_ch_flow(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    await callback.message.answer("📥 Send the **Channel Chat ID** (e.g., `-100123456789`):")
    await state.set_state(AdminSR.waiting_for_ch_id)
    await callback.answer()

@router.message(AdminSR.waiting_for_ch_id)
async def process_ch_id(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.update_data(ch_id=int(message.text.strip()))
    await message.answer("🏷️ Send the **Channel Username** with `@` (e.g., `@MyChannel`):")
    await state.set_state(AdminSR.waiting_for_ch_user)

@router.message(AdminSR.waiting_for_ch_user)
async def complete_ch_add(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    data = await state.get_data()
    await add_channel(data['ch_id'], message.text.strip())
    await state.clear()
    await message.answer("✅ Mandatory force join routing tracking matrix linked successfully!")

@router.callback_query(F.data == "adm_rem_ch")
async def init_rem_ch(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    channels = await get_channels()
    if not channels:
        await callback.message.answer("No channels configured.")
        return
    
    txt = "📋 **Configured Access Verification Nodes:**\n"
    for cid, cuser in channels:
        txt += f"`{cid}` : {cuser}\n"
    txt += "\nSend the Channel Chat ID to remove:"
    await callback.message.answer(txt, parse_mode="Markdown")
    await state.set_state(AdminSR.waiting_for_rem_id)
    await callback.answer()

@router.message(AdminSR.waiting_for_rem_id)
async def complete_ch_rem(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await remove_channel(int(message.text.strip()))
    await state.clear()
    await message.answer("❌ Channel removed from enforcement array.")

@router.callback_query(F.data == "adm_broadcast")
async def start_broadcast_flow(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    await callback.message.answer("📝 Send the message content you wish to broadcast globally to all users:")
    await state.set_state(AdminSR.waiting_for_broadcast)
    await callback.answer()

@router.message(AdminSR.waiting_for_broadcast)
async def execute_broadcast_transmission(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    uids = await get_all_user_ids()
    await state.clear()
    
    delivery_status = await message.answer("⚡ *Transmitting broadcast payload downlinks...*", parse_mode="Markdown")
    success, fail = 0, 0
    
    for uid in uids:
        try:
            await message.copy_to(chat_id=uid)
            success += 1
        except Exception:
            fail += 1
            
    await delivery_status.edit_text(f"📢 **Broadcast Complete!**\n\n✅ Delivered: `{success}`\n❌ Unreachable: `{fail}`", parse_mode="Markdown")
