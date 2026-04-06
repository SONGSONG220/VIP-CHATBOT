from nexichat import db

premiumdb = db.PremiumUsers.premium
msg_count_db = db.MsgCount.daily_counts


async def is_premium(user_id: int) -> bool:
    user = await premiumdb.find_one({"user_id": user_id})
    return bool(user)


async def add_premium(user_id: int):
    await premiumdb.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )


async def remove_premium(user_id: int):
    await premiumdb.delete_one({"user_id": user_id})


async def get_daily_count(user_id: int) -> int:
    from datetime import datetime
    today = datetime.utcnow().strftime("%Y-%m-%d")
    doc = await msg_count_db.find_one({"user_id": user_id, "date": today})
    return doc["count"] if doc else 0


async def increment_daily_count(user_id: int):
    from datetime import datetime
    today = datetime.utcnow().strftime("%Y-%m-%d")
    await msg_count_db.update_one(
        {"user_id": user_id, "date": today},
        {"$inc": {"count": 1}},
        upsert=True
    )


async def get_all_premium_users():
    return await premiumdb.find().to_list(length=None)
