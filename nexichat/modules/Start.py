import random
import config
from nexichat import nexichat, mongo
from pyrogram.enums import ChatType
from pyrogram import Client, filters
from config import OWNER_ID, UPDATE_CHNL, MAIN_BOT_USERNAME
from nexichat.database.chats import get_served_chats, add_served_chat
from nexichat.database.users import get_served_users, add_served_user
from nexichat.database.premium import is_premium
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from nexichat.modules.helpers import START_BOT, HELP_BTN, CLONE_INFO_BTN, PREMIUM_INFO_BTN
from nexichat import db

status_db = db.ChatBotStatusDb.StatusCollection
START_IMAGE = config.START_IMAGE
HELP_IMAGE = config.HELP_IMAGE

HELP_TEXT = """
🌸 **Hinata Bot - All Powers** 🌸

**👥 Group Admin Commands:**
• `/ban` — User ko ban karo (ban right chahiye)
• `/unban` — Unban karo (ban right chahiye)
• `/kick` — Kick karo bina ban ke (ban right chahiye)
• `/mute` — Mute karo (ban right chahiye)
• `/unmute` — Unmute karo (ban right chahiye)
• `/promote` — Admin banao (promote right chahiye)
• `/demote` — Admin se hatao (promote right chahiye)
• `/fullpromote` — Full rights do (sirf group owner)

**🤖 Bot Commands:**
• `/chatbot` — Enable/Disable chatbot
• `/lang` — Language set karo
• `/setpersonality girl/boy` — Personality change karo
• `/status` — Chatbot status dekho

**👑 Owner Only:**
• `/broadcast` — Sab ko message bhejo
• `/gban` — Global ban
• `/addpremium` — Premium do
• `/removepremium` — Premium hatao
• `/restart` — Bot restart karo

**🤖 Clone:**
• `/clone` — Apna bot banao!
  Free: 150 msgs/day | Premium: Unlimited!

_Made with 💕 by Hinata | Powered by Naruto 🍜_
"""

CLONE_TEXT = f"""
🤖 **Bot Clone Karo!**

**🆓 Free Clone:**
• Daily 150 messages limit
• Basic chat features
• Main bot: @{MAIN_BOT_USERNAME}

**💎 Premium Clone:**
• ❌ Koi limit nahi!
• Start image/message customize
• Help image customize
• Broadcast + GBan access
• Boy/Girl personality choose karo
"""

PREMIUM_TEXT = """
💎 **Premium Features:**
✅ Unlimited messages
✅ Start image/message customize
✅ Help image customize
✅ Broadcast power
✅ GBan access
✅ Boy/Girl personality
✅ Priority support

**Premium ke liye support se contact karo!**
"""

async def set_default_status(chat_id):
    try:
        if not await status_db.find_one({"chat_id": chat_id}):
            await status_db.insert_one({"chat_id": chat_id, "status": "enabled"})
    except:
        pass


@nexichat.on_message(filters.new_chat_members)
async def welcome_new_member(client, message: Message):
    await add_served_chat(message.chat.id)
    await set_default_status(message.chat.id)
    try:
        for member in message.new_chat_members:
            if member.id == nexichat.id:
                users = len(await get_served_users())
                chats = len(await get_served_chats())
                await client.send_photo(
                    message.chat.id,
                    photo=START_IMAGE,
                    caption=(
                        f"Haay! Main **Hinata** hoon~ 🌸\n"
                        f"Naruto mera boyfriend hai hehe~\n\n"
                        f"Mujhse reply karo ya @mention karo baat karne ke liye! 💕\n\n"
                        f"👥 Groups: **{chats}** | 👤 Users: **{users}**"
                    ),
                    reply_markup=InlineKeyboardMarkup(START_BOT),
                )
            else:
                welcome_msgs = [
                    f"Haay {member.mention}! Group mein aapka swagat hai~ 🌸",
                    f"Kyaa! {member.mention} aa gaye! Khush hoon tumse milke 🥺",
                    f"Aaa~ {member.mention}, Welcome! Naruto ne bhi kaha tha naye dosto se milna chahiye 💕",
                ]
                await message.reply_text(random.choice(welcome_msgs))
    except:
        pass


@nexichat.on_message(filters.command("start") & filters.private)
async def start_private(client, message: Message):
    user = message.from_user
    await add_served_user(user.id)
    prem = await is_premium(user.id)
    await client.send_photo(
        message.chat.id,
        photo=START_IMAGE,
        caption=(
            f"Haay {'💎 ' if prem else ''}**{user.first_name}**! Main Hinata hoon~ 🌸\n\n"
            f"{'💎 Aap premium user ho! Sab powers available hain 🌟\n\n' if prem else ''}"
            f"Naruto mera boyfriend hai hehe~\n"
            f"Mujhse yahan baat karo ya group mein add karo! 💕"
        ),
        reply_markup=InlineKeyboardMarkup(START_BOT),
    )


@nexichat.on_message(filters.command("start") & filters.group)
async def start_group(client, message: Message):
    await add_served_chat(message.chat.id)
    await set_default_status(message.chat.id)
    await client.send_photo(
        message.chat.id,
        photo=START_IMAGE,
        caption=f"Haay **{message.from_user.first_name}**! Main Hinata hoon~ 🌸\nNaruto mera boyfriend hai hehe~ 💕",
        reply_markup=InlineKeyboardMarkup(START_BOT),
    )


@nexichat.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    await client.send_photo(
        message.chat.id,
        photo=HELP_IMAGE,
        caption=HELP_TEXT,
        reply_markup=InlineKeyboardMarkup(HELP_BTN),
    )


@nexichat.on_callback_query(filters.regex("^HELP$"))
async def help_callback(client, cb: CallbackQuery):
    try:
        await cb.message.edit_caption(
            caption=HELP_TEXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("« Back", callback_data="BACK"),
                 InlineKeyboardButton("❌ Close", callback_data="CLOSE")]
            ])
        )
    except:
        await cb.answer(HELP_TEXT[:200], show_alert=True)


@nexichat.on_callback_query(filters.regex("^CLONE_INFO$"))
async def clone_info_cb(client, cb: CallbackQuery):
    try:
        await cb.message.edit_caption(
            caption=CLONE_TEXT,
            reply_markup=InlineKeyboardMarkup(CLONE_INFO_BTN),
        )
    except:
        await cb.answer(CLONE_TEXT[:200], show_alert=True)


@nexichat.on_callback_query(filters.regex("^PREMIUM_INFO$"))
async def premium_info_cb(client, cb: CallbackQuery):
    try:
        await cb.message.edit_caption(
            caption=PREMIUM_TEXT,
            reply_markup=InlineKeyboardMarkup(PREMIUM_INFO_BTN),
        )
    except:
        await cb.answer(PREMIUM_TEXT[:200], show_alert=True)


@nexichat.on_callback_query(filters.regex("^BACK$"))
async def back_cb(client, cb: CallbackQuery):
    user = cb.from_user
    prem = await is_premium(user.id)
    try:
        await cb.message.edit_caption(
            caption=(
                f"Haay {'💎 ' if prem else ''}**{user.first_name}**! Main Hinata hoon~ 🌸\n\n"
                f"{'💎 Premium user ho! Sab powers available! 🌟\n\n' if prem else ''}"
                f"Naruto mera boyfriend hai hehe~ 💕"
            ),
            reply_markup=InlineKeyboardMarkup(START_BOT),
        )
    except:
        pass


@nexichat.on_callback_query(filters.regex("^CLOSE$"))
async def close_cb(client, cb: CallbackQuery):
    try:
        await cb.message.delete()
    except:
        await cb.answer("Close nahi ho sakta 😢", show_alert=True)
