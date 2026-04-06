import sys
import asyncio
import importlib
from flask import Flask
import threading
import config
from pyrogram import idle
from pyrogram.types import BotCommand
from config import OWNER_ID
from nexichat import LOGGER, nexichat, userbot, load_clone_owners
from nexichat.modules import ALL_MODULES
from nexichat.modules.Clone import restart_bots
from nexichat.modules.Id_Clone import restart_idchatbots


app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)


async def anony_boot():
    try:
        await nexichat.start()
        me = await nexichat.get_me()
        try:
            await nexichat.send_message(
                int(OWNER_ID),
                f"**@{me.username} Is started ✅**"
            )
        except Exception as ex:
            LOGGER.info(f"@{me.username} Started.")

        asyncio.create_task(restart_bots())
        asyncio.create_task(restart_idchatbots())
        await load_clone_owners()

        if config.STRING1:
            try:
                await userbot.start()
                try:
                    await nexichat.send_message(
                        int(OWNER_ID),
                        f"**Id-Chatbot Also Started ✅**"
                    )
                except Exception as ex:
                    LOGGER.info(f"Id-Chatbot Started.")
            except Exception as ex:
                LOGGER.error(f"Error starting id-chatbot: {ex}")

        await idle()

    except Exception as ex:
        LOGGER.error(ex)
    finally:
        try:
            await nexichat.stop()
        except Exception:
            pass


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(anony_boot())
