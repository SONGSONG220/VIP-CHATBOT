import random
import asyncio
import itertools
from groq import AsyncGroq
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty, UserIsBlocked, PeerIdInvalid
from pyrogram.enums import ChatAction, ChatMemberStatus as CMS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from deep_translator import GoogleTranslator
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from nexichat.database import add_served_cchat, add_served_cuser
from nexichat.database.premium import is_premium, get_daily_count, increment_daily_count
from config import MONGO_URL, GROQ_API_KEYS, FREE_DAILY_LIMIT
from nexichat import nexichat, mongo, LOGGER, db
from nexichat.idchatbot.helpers import chatai, languages
import asyncio

translator = GoogleTranslator()
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
        LOGGER.warning(f"Groq error (idchatbot): {e}")
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
        elif reply_message.audio:
            reply_data["text"] = reply_message.audio.file_id
            reply_data["check"] = "audio"
        elif reply_message.animation:
            reply_data["text"] = reply_message.animation.file_id
            reply_data["check"] = "gif"
        elif reply_message.voice:
            reply_data["text"] = reply_message.voice.file_id
            reply_data["check"] = "voice"
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


async def get_chat_language(chat_id, bot_id):
    doc = await lang_db.find_one({"chat_id": chat_id, "bot_id": bot_id})
    return doc["language"] if doc and "language" in doc else None


async def get_personality(chat_id, bot_id):
    doc = await db.PersonalityDb.personality.find_one({"chat_id": chat_id, "bot_id": bot_id})
    return doc.get("personality", "girl") if doc else "girl"


@Client.on_message(filters.left_chat_member)
async def on_bot_kicked(client: Client, message: Message):
    if message.left_chat_member.id == client.me.id:
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
            LOGGER.warning(f"DM error after kick (idchatbot): {e}")


@Client.on_message(filters.incoming)
async def chatbot_response(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        bot_id = client.me.id

        chat_status = await status_db.find_one({"chat_id": chat_id, "bot_id": bot_id})
        if chat_status and chat_status.get("status") == "disabled":
            return

        if message.text and any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
            if message.chat.type in ["group", "supergroup"]:
                return await add_served_chat(message.chat.id)
            else:
                return await add_served_user(message.chat.id)

        if not message.from_user or message.from_user.is_bot:
            return

        should_reply = (
            (message.reply_to_message and message.reply_to_message.from_user.id == client.me.id)
            or not message.reply_to_message
        )

        if not should_reply:
            return

        # ── MSG LIMIT CHECK ──
        sender_id = message.from_user.id
        prem = await is_premium(sender_id)

        if not prem:
            count = await get_daily_count(sender_id)
            if count >= FREE_DAILY_LIMIT:
                try:
                    await message.reply_text(
                        f"Haay {message.from_user.first_name}... aaj ke {FREE_DAILY_LIMIT} messages use ho gaye 😢\n"
                        f"Kal phir baat karte hain! Ya premium lo aur unlimited baat karo 🌸"
                    )
                except:
                    pass
                return
            await increment_daily_count(sender_id)

        user_text = message.text or ""

        # Sticker reply
        if not user_text and message.sticker:
            cute_replies = [
                "Itna cute sticker! 🥺 Naruto ko bhi dikhaungi~",
                "Waah! Bahut achha hai ye 💕",
                "Hehe~ mujhe bhi aisa chahiye 😊",
            ]
            await asyncio.sleep(1)
            await message.reply_text(random.choice(cute_replies))
            return

        if not user_text:
            return

        angry_keywords = ["idiot", "stupid", "shut up", "bakwaas", "chup", "bekar", "useless", "hate"]
        is_angry = any(w in user_text.lower() for w in angry_keywords)

        personality = await get_personality(chat_id, bot_id)

        # ── GROQ AI REPLY ──
        groq_reply = await get_groq_reply(user_text, personality)

        if groq_reply:
            if is_angry:
                sad_prefix = random.choice([
                    "Haay... 😢 ", "Aaa... iska matlab kya tha? 🥺 ", "Mujhe bura laga... 😭 "
                ])
                groq_reply = sad_prefix + groq_reply

            chat_lang = await get_chat_language(chat_id, bot_id)
            if chat_lang and chat_lang != "nolang" and chat_lang != "en":
                try:
                    groq_reply = GoogleTranslator(source='auto', target=chat_lang).translate(groq_reply)
                except:
                    pass

            await message.reply_text(groq_reply)

        else:
            # ── FALLBACK: DB SE REPLY ──
            reply_data = await get_reply(user_text)
            if reply_data:
                check = reply_data.get("check", "none")
                text = reply_data.get("text", "")
                if check == "sticker":
                    await message.reply_sticker(text)
                elif check == "photo":
                    await message.reply_photo(text)
                elif check == "video":
                    await message.reply_video(text)
                elif check == "audio":
                    await message.reply_audio(text)
                elif check == "gif":
                    await message.reply_animation(text)
                elif check == "voice":
                    await message.reply_voice(text)
                elif text:
                    chat_lang = await get_chat_language(chat_id, bot_id)
                    if chat_lang and chat_lang != "nolang":
                        try:
                            text = GoogleTranslator(source='auto', target=chat_lang).translate(text)
                        except:
                            pass
                    await message.reply_text(text)
            else:
                hinata_fallbacks = [
                    "Hehe~ mujhe samajh nahi aaya, phir se batao? 😊",
                    "Aaa... kya bola? Main sun rahi thi 😅",
                    "Kyaa? Sorry samjhi nahi 🥺",
                ]
                await message.reply_text(random.choice(hinata_fallbacks))

        # ── REPLY SAVE (LEARNING) ──
        if message.reply_to_message and message.reply_to_message.from_user:
            if message.reply_to_message.from_user.id == client.me.id:
                if message.reply_to_message.text:
                    await save_reply(message.reply_to_message, message)

    except MessageEmpty:
        pass
    except Exception as e:
        LOGGER.warning(f"chatbot_response error (idchatbot): {e}")
