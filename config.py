from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_ID = getenv("API_ID", "37096542")
API_HASH = getenv("API_HASH", "e87f06819f9d2b3364502b978650568f")
BOT_TOKEN = getenv("BOT_TOKEN", "8670466939:AAGkqOfWy6adbrUaGyU8wr7YhjO3zjNXZlw")
STRING1 = getenv("STRING_SESSION", None)
MONGO_URL = getenv("MONGO_URL", "mongodb+srv://aditya0:aditya0@cluster0.9m8897t.mongodb.net/?appName=Cluster0")
OWNER_ID = int(getenv("OWNER_ID", "7812646657"))
SUPPORT_GRP = getenv("SUPPORT_GRP", "bothub13")
UPDATE_CHNL = getenv("UPDATE_CHNL", "botbykilwakillua")
OWNER_USERNAME = getenv("OWNER_USERNAME", "usernametnot")

GROQ_API_KEYS = [
    getenv("GROQ_API_KEY_1", "gsk_Xq2i9NHhMFGhgr3ePqJXWGdyb3FYZ0pvORnPES5Xkyoa1iEWgw"),
    getenv("GROQ_API_KEY_2", "gsk_q6jmGgCYwGfkP8lNlLYhWGdyb3FYY9mh6uhXygE7KyJNXGX6T5"),
    getenv("GROQ_API_KEY_3", "gsk_Fev8XX9N2TCZ9o0Ls2UeWGdyb3FYc7OgQAuuuNB3HcpshR2tbG"),
]
GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k]

MAIN_BOT_USERNAME = getenv("MAIN_BOT_USERNAME", "Hinata_cha5tbot")

START_IMAGE = getenv("START_IMAGE", "https://files.catbox.moe/7m7pc4.jpg")
HELP_IMAGE = getenv("HELP_IMAGE", "https://files.catbox.moe/96o6ft.jpg")
QR_IMAGE = getenv("QR_IMAGE", "https://files.catbox.moe/1wwfpf.jpg")

FREE_DAILY_LIMIT = 150
