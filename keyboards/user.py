from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Profile"), KeyboardButton(text="🚀 Create Panel")],
            [KeyboardButton(text="📈 Referrals"), KeyboardButton(text="📂 My Panels")],
            [KeyboardButton(text="🎯 Support")]
        ],
        resize_keyboard=True
    )

def force_join_keyboard(not_joined_channels):
    buttons = []
    for _, username in not_joined_channels:
        clean_name = username.replace("@", "")
        buttons.append([InlineKeyboardButton(text=f"Join {username}", url=f"https://t.me/{clean_name}")])
    
    buttons.append([InlineKeyboardButton(text="🔄 Verify Join", callback_data="verify_join")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
