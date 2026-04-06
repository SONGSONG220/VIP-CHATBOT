import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
from config import OWNER_ID
from nexichat import nexichat
from nexichat.database.premium import is_premium, add_premium, remove_premium


async def check_ban_right(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status == CMS.OWNER:
            return True
        if member.status == CMS.ADMINISTRATOR:
            return member.privileges.can_restrict_members
        return False
    except:
        return False


async def check_add_admin_right(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status == CMS.OWNER:
            return True
        if member.status == CMS.ADMINISTRATOR:
            return member.privileges.can_promote_members
        return False
    except:
        return False


def get_target(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id, message.reply_to_message.from_user.mention
    elif len(message.command) > 1:
        return message.command[1], message.command[1]
    return None, None


@nexichat.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message: Message):
    if not await check_ban_right(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Haay~ tumhare paas ban karne ka right nahi hai 😔")
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kise ban karna hai? Reply karo ya username do 🥺")
    reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason given"
    try:
        await client.ban_chat_member(message.chat.id, target_id)
        await message.reply_text(
            f"✅ **Banned!**\n👤 User: {target_mention}\n📝 Reason: {reason}\n\n_Naruto ne bhi bola tha galat logon ko door karo~ 🍃_"
        )
    except ChatAdminRequired:
        await message.reply_text("Mujhe admin banao pehle 😢")
    except UserAdminInvalid:
        await message.reply_text("Is admin ko ban nahi kar sakti 🥺")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@nexichat.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message: Message):
    if not await check_ban_right(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Haay~ tumhare paas unban karne ka right nahi hai 😔")
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kise unban karna hai? 🥺")
    try:
        await client.unban_chat_member(message.chat.id, target_id)
        await message.reply_text(f"✅ **Unbanned!**\n👤 User: {target_mention}\n\n_Sab ko ek mauka milna chahiye~ 🌸_")
    except ChatAdminRequired:
        await message.reply_text("Mujhe admin access chahiye 😢")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@nexichat.on_message(filters.command("kick") & filters.group)
async def kick_user(client, message: Message):
    if not await check_ban_right(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Haay~ tumhare paas kick karne ka right nahi hai 😔")
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kise kick karna hai? 🥺")
    try:
        await client.ban_chat_member(message.chat.id, target_id)
        await asyncio.sleep(1)
        await client.unban_chat_member(message.chat.id, target_id)
        await message.reply_text(f"👢 **Kicked!**\n👤 User: {target_mention}\n\n_Wapas aa sakte hain agar sudhar jayein~ 🌸_")
    except ChatAdminRequired:
        await message.reply_text("Mujhe admin access chahiye 😢")
    except UserAdminInvalid:
        await message.reply_text("Is admin ko kick nahi kar sakti 🥺")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@nexichat.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message: Message):
    if not await check_ban_right(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Haay~ tumhare paas mute karne ka right nahi hai 😔")
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kise mute karna hai? 🥺")
    try:
        await client.restrict_chat_member(message.chat.id, target_id, ChatPermissions(can_send_messages=False))
        await message.reply_text(f"🔇 **Muted!**\n👤 User: {target_mention}\n\n_Ab thodi der chup rehna padega~ 🌸_")
    except ChatAdminRequired:
        await message.reply_text("Mujhe admin access chahiye 😢")
    except UserAdminInvalid:
        await message.reply_text("Is admin ko mute nahi kar sakti 🥺")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@nexichat.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message: Message):
    if not await check_ban_right(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Haay~ tumhare paas unmute karne ka right nahi hai 😔")
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kise unmute karna hai? 🥺")
    try:
        await client.restrict_chat_member(
            message.chat.id, target_id,
            ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
        )
        await message.reply_text(f"🔊 **Unmuted!**\n👤 User: {target_mention}\n\n_Ab baat kar sakte ho~ 🌸_")
    except ChatAdminRequired:
        await message.reply_text("Mujhe admin access chahiye 😢")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@nexichat.on_message(filters.command("promote") & filters.group)
async def promote_user(client, message: Message):
    if not await check_add_admin_right(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Haay~ tumhare paas promote karne ka right nahi hai 😔")
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kise promote karna hai? 🥺")
    try:
        promoter = await client.get_chat_member(message.chat.id, message.from_user.id)
        await client.promote_chat_member(message.chat.id, target_id, privileges=promoter.privileges)
        await message.reply_text(f"⬆️ **Promoted!**\n👤 User: {target_mention}\n\n_Ab admin hai! Zimmedaari se kaam karna~ 🌸_")
    except ChatAdminRequired:
        await message.reply_text("Mujhe promote right chahiye 😢")
    except UserAdminInvalid:
        await message.reply_text("Promote nahi ho sakta 🥺")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@nexichat.on_message(filters.command("demote") & filters.group)
async def demote_user(client, message: Message):
    if not await check_add_admin_right(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Haay~ tumhare paas demote karne ka right nahi hai 😔")
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kise demote karna hai? 🥺")
    try:
        await client.promote_chat_member(message.chat.id, target_id, privileges=None)
        await message.reply_text(f"⬇️ **Demoted!**\n👤 User: {target_mention}\n\n_Ab admin nahi raha~ 🍃_")
    except ChatAdminRequired:
        await message.reply_text("Mujhe demote right chahiye 😢")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@nexichat.on_message(filters.command("fullpromote") & filters.group)
async def fullpromote_user(client, message: Message):
    try:
        req = await client.get_chat_member(message.chat.id, message.from_user.id)
        if req.status != CMS.OWNER:
            return await message.reply_text("Haay~ sirf group owner /fullpromote use kar sakta hai 😔")
    except:
        return
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kise full promote karna hai? 🥺")
    try:
        from pyrogram.types import ChatPrivileges
        await client.promote_chat_member(
            message.chat.id, target_id,
            privileges=ChatPrivileges(
                can_manage_chat=True, can_delete_messages=True,
                can_manage_video_chats=True, can_restrict_members=True,
                can_promote_members=True, can_change_info=True,
                can_invite_users=True, can_pin_messages=True,
            )
        )
        await message.reply_text(f"👑 **Full Admin!**\n👤 User: {target_mention}\n\n_Sab powers de di hain~ 🌸_")
    except ChatAdminRequired:
        await message.reply_text("Mujhe full admin rights chahiye 😢")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@nexichat.on_message(filters.command("gban") & filters.user(int(OWNER_ID)))
async def global_ban(client, message: Message):
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kise gban karna hai? 🥺")
    reason = " ".join(message.command[2:]) if len(message.command) > 2 else "Global ban"
    from nexichat.database.chats import get_served_chats
    chats = await get_served_chats()
    success = 0
    failed = 0
    msg = await message.reply_text(f"⚡ Global ban chal raha hai {len(chats)} groups mein...")
    for chat in chats:
        try:
            await client.ban_chat_member(chat["chat_id"], target_id)
            success += 1
        except:
            failed += 1
    await msg.edit_text(
        f"✅ **Global Ban Done!**\n👤 {target_mention}\n📝 {reason}\n✅ {success} groups\n❌ {failed} failed"
    )


@nexichat.on_message(filters.command("broadcast") & filters.user(int(OWNER_ID)))
async def broadcast(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Jo message broadcast karna hai usse reply karo 🥺")
    from nexichat.database.chats import get_served_chats
    from nexichat.database.users import get_served_users
    chats = await get_served_chats()
    users = await get_served_users()
    msg = await message.reply_text("📢 Broadcast chal raha hai...")
    success = 0
    failed = 0
    for chat in chats:
        try:
            await message.reply_to_message.copy(chat["chat_id"])
            success += 1
            await asyncio.sleep(0.3)
        except:
            failed += 1
    for user in users:
        try:
            await message.reply_to_message.copy(user["user_id"])
            success += 1
            await asyncio.sleep(0.3)
        except:
            failed += 1
    await msg.edit_text(f"✅ **Broadcast Done!**\n✅ Success: {success}\n❌ Failed: {failed}")


@nexichat.on_message(filters.command("addpremium") & filters.user(int(OWNER_ID)))
async def add_prem(client, message: Message):
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kise premium dena hai? 🥺")
    await add_premium(int(target_id))
    await message.reply_text(f"💎 **Premium Diya!**\n👤 {target_mention}\n\n_Ab unlimited msgs! 🌸_")


@nexichat.on_message(filters.command("removepremium") & filters.user(int(OWNER_ID)))
async def remove_prem(client, message: Message):
    target_id, target_mention = get_target(message)
    if not target_id:
        return await message.reply_text("Kiska premium hatana hai? 🥺")
    await remove_premium(int(target_id))
    await message.reply_text(f"❌ **Premium Hataya!**\n👤 {target_mention}")


@nexichat.on_message(filters.command("setpersonality") & filters.group)
async def set_personality(client, message: Message):
    try:
        req = await client.get_chat_member(message.chat.id, message.from_user.id)
        if req.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            return await message.reply_text("Sirf admins personality change kar sakte hain 😔")
    except:
        return
    if len(message.command) < 2:
        return await message.reply_text("Use: /setpersonality girl ya /setpersonality boy")
    p = message.command[1].lower()
    if p not in ["girl", "boy"]:
        return await message.reply_text("Sirf 'girl' ya 'boy' choose karo 🥺")
    await nexichat.db.PersonalityDb.personality.update_one(
        {"chat_id": message.chat.id}, {"$set": {"personality": p}}, upsert=True
    )
    await message.reply_text(
        f"✅ Personality: **{p.upper()}**\n"
        f"{'_Ab Hinata style mein baat karungi~ 🌸_' if p == 'girl' else '_Ab cool boy style~ 😎_'}"
  )
