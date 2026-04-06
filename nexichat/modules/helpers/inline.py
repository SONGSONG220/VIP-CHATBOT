from pyrogram.types import InlineKeyboardButton
from config import SUPPORT_GRP, UPDATE_CHNL, MAIN_BOT_USERNAME
from nexichat import OWNER, nexichat


START_BOT = [
    [
        InlineKeyboardButton(
            text="➕ Add Me In Your Group ➕",
            url=f"https://t.me/{nexichat.username}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(
            text="📢 Update Channel",
            url=f"https://t.me/{UPDATE_CHNL}",
        ),
        InlineKeyboardButton(
            text="🤖 Clone Bot",
            callback_data="CLONE_INFO",
        ),
    ],
    [
        InlineKeyboardButton(
            text="❓ Help",
            callback_data="HELP",
        ),
    ],
]

PNG_BTN = START_BOT

DEV_OP = [
    [
        InlineKeyboardButton(text="🥀 Owner 🥀", user_id=OWNER),
        InlineKeyboardButton(text="✨ Support ✨", url=f"https://t.me/{SUPPORT_GRP}"),
    ],
]

HELP_BTN = [
    [
        InlineKeyboardButton(text="❓ Help", callback_data="HELP"),
        InlineKeyboardButton(text="❌ Close", callback_data="CLOSE"),
    ],
]

HELP_BUTN = [
    [
        InlineKeyboardButton(text="« Help »", url=f"https://t.me/{nexichat.username}?start=help"),
        InlineKeyboardButton(text="❌ Close", callback_data="CLOSE"),
    ],
]

BACK = [
    [
        InlineKeyboardButton(text="« Back", callback_data="BACK"),
        InlineKeyboardButton(text="❌ Close", callback_data="CLOSE"),
    ],
]

CLOSE_BTN = [
    [
        InlineKeyboardButton(text="❌ Close", callback_data="CLOSE"),
    ],
]

CHATBOT_ON = [
    [
        InlineKeyboardButton(text="✅ Enable", callback_data="enable_chatbot"),
        InlineKeyboardButton(text="❌ Disable", callback_data="disable_chatbot"),
    ],
]

S_BACK = [
    [
        InlineKeyboardButton(text="« Back", callback_data="SBACK"),
        InlineKeyboardButton(text="❌ Close", callback_data="CLOSE"),
    ],
]

CHATBOT_BACK = [
    [
        InlineKeyboardButton(text="« Back", callback_data="CHATBOT_BACK"),
        InlineKeyboardButton(text="❌ Close", callback_data="CLOSE"),
    ],
]

HELP_START = [
    [
        InlineKeyboardButton(text="« Help »", callback_data="HELP"),
        InlineKeyboardButton(text="❌ Close", callback_data="CLOSE"),
    ],
]

ABOUT_BTN = [
    [
        InlineKeyboardButton(text="🎄 Support", url=f"https://t.me/{SUPPORT_GRP}"),
        InlineKeyboardButton(text="« Help »", callback_data="HELP"),
    ],
    [
        InlineKeyboardButton(text="🍾 Owner", user_id=OWNER),
    ],
    [
        InlineKeyboardButton(text="📢 Updates", url=f"https://t.me/{UPDATE_CHNL}"),
        InlineKeyboardButton(text="« Back", callback_data="BACK"),
    ],
]

MUSIC_BACK_BTN = [
    [
        InlineKeyboardButton(text="Coming Soon", callback_data="soon"),
    ],
]

CLONE_INFO_BTN = [
    [
        InlineKeyboardButton(
            text="🤖 Clone Your Bot",
            url=f"https://t.me/{MAIN_BOT_USERNAME}?start=clone"
        ),
    ],
    [
        InlineKeyboardButton(text="💎 Get Premium", callback_data="PREMIUM_INFO"),
    ],
    [
        InlineKeyboardButton(text="« Back", callback_data="BACK"),
    ],
]

PREMIUM_INFO_BTN = [
    [
        InlineKeyboardButton(text="💰 Buy Premium", url=f"https://t.me/{SUPPORT_GRP}"),
    ],
    [
        InlineKeyboardButton(text="« Back", callback_data="CLONE_INFO"),
    ],
]
