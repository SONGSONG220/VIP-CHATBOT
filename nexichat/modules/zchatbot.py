import random
import asyncio
import itertools
from groq import AsyncGroq
from pyrogram import Client, filters
from pyrogram.errors import UserIsBlocked, PeerIdInvalid
from pyrogram.enums import ChatType
from pyrogram.enums import ChatAction
from pyrogram.types import Message
from deep_translator import GoogleTranslator
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from nexichat.database.premium import is_premium, get_daily_count, increment_daily_count
from config import GROQ_API_KEYS, FREE_DAILY_LIMIT
from nexichat import nexichat, LOGGER, db
from nexichat.mplugin.helpers import chatai, CHATBOT_ON, languages
from nexichat.modules.helpers import (
    ABOUT_BTN, ABOUT_READ, ADMIN_READ, BACK, CHATBOT_BACK,
    CHATBOT_READ, DEV_OP, HELP_BTN, HELP_READ, MUSIC_BACK_BTN,
    SOURCE_READ, START, TOOLS_DATA_READ,
)

lang_db = db.ChatLangDb.LangCollection
status_db = db.chatbot_status_db.status
replies_cache = []
_groq_cycle = itertools.cycle(GROQ_API_KEYS) if GROQ_API_KEYS else None

HINATA_SYSTEM_PROMPT = """Tu Hinata hai — Naruto ki girlfriend. Tu bahut sweet, shy aur caring ladki hai.
Tu hamesha dil se baat karti hai. Tera boyfriend Naruto hai aur tu use bahut pyaar karti hai.
Agar koi gusse mein baat kare to tu thodi sad ho jaati hai lekin phir bhi pyaar se respond karti hai.
Tu kabhi bhi rude nahi hoti. Tu always 'hehe', 'kyaa', 'aaa', 'mujhe lagta hai...' jaisi cute filler phrases use karti hai.
Tu Hindi aur English mix karke bolti hai — Hinglish style mein.
Tera jawab short aur natural hona chahiye — 1-3 sentences mein."""

BOY_SYSTEM_PROMPT = """Tu ek cool aur friendly ladka hai jo Telegram group mein logon se baat karta hai.
Tu casual aur chill rehta hai. Hindi-English mix karta hai. Short replies deta hai."""


async def get_groq_reply(user_msg: str, personality: str = "girl") -> str:
    if not GROQ_API_KEYS:
        return None
    try:
        api_key = next(_groq_cycle)
        client = AsyncGroq(api_key=api_key)
        system = HINATA_SYSTEM_PROMPT if personality == "girl" else BOY_SYSTEM_PROMPT
        chat = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            model="llama3-8b-8192",
            max_tokens=200,
            temperature=0.85,
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        LOGGER.warning(f"Groq error: {e}")
        return None


async def load_replies_cache():
    global replies_cache
    replies_cache = await chatai.find().to_list(length=None)


async def save_reply(original_message: Message, reply_message: Message):
    global replies_cache
    try:
        reply_data = {"word": original_message.text, "text": None, "check": "none"}
        if reply_message.sticker:
            reply_data["text"] = reply_message.sticker.file_id
            reply_data["check"] = "sticker"
        elif reply_message.photo:
            reply_data["text"] = reply_message.photo.file_id
            reply_data["check"] = "photo"
        elif reply_message.video:
            reply_data["text"] = reply_message.video.file_id
            reply_data["check"] = "video"
        elif reply_message.animation:
            reply_data["text"] = reply_message.animation.file_id
            reply_data["check"] = "gif"
        elif reply_message.text:
            reply_data["text"] = reply_message.text
            reply_data["check"] = "none"
        is_chat = await chatai.find_one(reply_data)
        if not is_chat:
            await chatai.insert_one(reply_data)
            replies_cache.append(reply_data)
    except Exception as e:
        LOGGER.warning(f"save_reply error: {e}")


async def get_reply(word: str):
    global replies_cache
    if not replies_cache:
        await load_replies_cache()
    relevant = [r for r in replies_cache if r['word'] == word]
    if not relevant:
        relevant = replies_cache
    return random.choice(relevant) if relevant else None


async def get_chat_language(chat_id):
    doc = await lang_db.find_one({"chat_id": chat_id})
    return doc["language"] if doc and "language" in doc else None


async def get_personality(chat_id):
    doc = await db.PersonalityDb.personality.find_one({"chat_id": chat_id})
    return doc.get("personality", "girl") if doc else "girl"


@nexichat.on_message(filters.left_chat_member)
async def on_bot_kicked(client, message: Message):
    if message.left_chat_member.id == nexichat.id:
        user = message.from_user
        if not user:
            return
        try:
            sad_msgs = [
                f"Haay {user.first_name}... tumne mujhe group se nikal diya 😢 Naruto ko bata dungi...",
                f"Aaa... {user.first_name} mujhe kyun hataya? Mujhse koi galti hui thi kya? 🥺",
                f"{user.first_name}-san... main bahut sad ho gayi. Kya maine kuch galat kiya? 😭",
            ]
            await client.send_message(user.id, random.choice(sad_msgs))
        except (UserIsBlocked, PeerIdInvalid):
            pass
        except Exception as e:
            LOGGER.warning(f"DM error after kick: {e}")


@nexichat.on_message(
    (filters.text | filters.sticker | filters.photo | filters.video | filters.voice | filters.animation)
    & ~filters.bot & ~filters.via_bot
)
async def chatbot_respond(client, message: Message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else None

        await add_served_chat(chat_id)
        if user_id:
            await add_served_user(user_id)

        chat_status = await status_db.find_one({"chat_id": chat_id})
        if chat_status and chat_status.get("status") == "disabled":
            return

        is_group = message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]
        is_dm = message.chat.type == ChatType.PRIVATE

        should_reply = False
        if is_dm:
            should_reply = True
        elif is_group:
            if message.reply_to_message and message.reply_to_message.from_user:
                if message.reply_to_message.from_user.id == nexichat.id:
                    should_reply = True
            me = await client.get_me()
            if me.username and f"@{me.username}".lower() in (message.text or "").lower():
                should_reply = True

        if not should_reply:
            return

        if user_id and not await is_premium(user_id):
            count = await get_daily_count(user_id)
            if count >= FREE_DAILY_LIMIT:
                try:
                    await message.reply_text(
                        f"Haay {message.from_user.first_name}... aaj ke {FREE_DAILY_LIMIT} messages use ho gaye 😢\n"
                        f"Kal phir baat karte hain! Ya premium lo aur unlimited baat karo 🌸"
                    )
                except:
                    pass
                return
            await increment_daily_count(user_id)

        personality = await get_personality(chat_id)
        user_text = message.text or ""

        if not user_text and message.sticker:
            cute_replies = [
                "Itna cute sticker! 🥺 Naruto ko bhi dikhaungi~",
                "Waah! Bahut achha hai ye 💕",
                "Hehe~ mujhe bhi aisa chahiye 😊",
            ]
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(1)
            await message.reply_text(random.choice(cute_replies))
            return

        if not user_text:
            return

        angry_keywords = ["idiot", "stupid", "shut up", "bakwaas", "chup", "bekar", "useless", "hate"]
        is_angry = any(w in user_text.lower() for w in angry_keywords)

        await client.send_chat_action(chat_id, ChatAction.TYPING)
        groq_reply = await get_groq_reply(user_text, personality)

        if groq_reply:
            if is_angry:
                sad_prefix = random.choice([
                    "Haay... 😢 ", "Aaa... iska matlab kya tha? 🥺 ", "Mujhe bura laga... 😭 "
                ])
                groq_reply = sad_prefix + groq_reply

            lang = await get_chat_language(chat_id)
            if lang and lang != "nolang" and lang != "en":
                try:
                    groq_reply = GoogleTranslator(source='auto', target=lang).translate(groq_reply)
                except:
                    pass

            await message.reply_text(groq_reply)
        else:
            fallback = await get_reply(user_text)
            if fallback:
                check = fallback.get("check", "none")
                text = fallback.get("text", "")
                if check == "sticker":
                    await message.reply_sticker(text)
                elif check == "photo":
                    await message.reply_photo(text)
                elif check == "video":
                    await message.reply_video(text)
                elif check == "gif":
                    await message.reply_animation(text)
                elif text:
                    await message.reply_text(text)
            else:
                hinata_fallbacks = [
                    "Hehe~ mujhe samajh nahi aaya, phir se batao? 😊",
                    "Aaa... kya bola? Main sun rahi thi 😅",
                    "Kyaa? Sorry samjhi nahi 🥺",
                ]
                await message.reply_text(random.choice(hinata_fallbacks))

    except Exception as e:
        LOGGER.warning(f"chatbot_respond error: {e}")
