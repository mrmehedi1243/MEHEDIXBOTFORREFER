from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="➕ Add Channel", callback_data="adm_add_ch"), 
         InlineKeyboardButton(text="❌ Remove Channel", callback_data="adm_rem_ch")],
        [InlineKeyboardButton(text="📊 View Stats", callback_data="adm_stats")]
    ])
