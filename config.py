from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_ID = getenv("API_ID", "37096542")
API_HASH = getenv("API_HASH", "e87f06819f9d2b3364502b978650568f")
BOT_TOKEN = getenv("BOT_TOKEN", None)
STRING1 = getenv("STRING_SESSION", None)
MONGO_URL = getenv("MONGO_URL", None)
OWNER_ID = int(getenv("OWNER_ID", "1808943146"))
SUPPORT_GRP = getenv("SUPPORT_GRP", "waifexanime")
UPDATE_CHNL = getenv("UPDATE_CHNL", "waifexanime")
OWNER_USERNAME = getenv("OWNER_USERNAME", "waifexanime")

GROQ_API_KEYS = [
    getenv("GROQ_API_KEY_1", ""),
    getenv("GROQ_API_KEY_2", ""),
    getenv("GROQ_API_KEY_3", ""),
]
GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k]

MAIN_BOT_USERNAME = getenv("MAIN_BOT_USERNAME", "Hinata_cha5tbot")

START_IMAGE = getenv("START_IMAGE", "https://files.catbox.moe/7m7pc4.jpg")
HELP_IMAGE = getenv("HELP_IMAGE", "https://files.catbox.moe/96o6ft.jpg")
QR_IMAGE = getenv("QR_IMAGE", "https://files.catbox.moe/1wwfpf.jpg")

FREE_DAILY_LIMIT = 150
