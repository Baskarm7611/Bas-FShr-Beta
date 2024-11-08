#(©)Tamilgram


from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from pymongo import MongoClient

# Load environment variables
load_dotenv('.env')

# Initialize bot variables
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", '')  # Format: "<bot_id>:<token>"
if not TG_BOT_TOKEN:
    logging.error('BOT TOKEN NOT FOUND!!')
    exit(1)

bot_id = int(TG_BOT_TOKEN.split(':', 1)[0])  # Extract bot_id from TG_BOT_TOKEN

API_ID = int(os.getenv("API_ID", "0"))  # Format: integer, obtained from my.telegram.org
if not API_ID:
    logging.error('API ID NOT FOUND!!')
    exit(1)

API_HASH = os.getenv("API_HASH", "")  # Format: string, obtained from my.telegram.org
if not API_HASH:
    logging.error('API HASH NOT FOUND!!')
    exit(1)

DB_URL = os.getenv("DB_URL", "")  # Format: MongoDB connection string
if not DB_URL:
    logging.error("DB URL NOT SET!!")
    exit(1)

# Fetch environment variables from the database if available
if DB_URL:
    conn = MongoClient(DB_URL)
    db = conn[str(bot_id)]
    col = db['tamilgram-configs']
    env_vars = {env['var_name']: env['value'] for env in col.find()}
    for key, value in env_vars.items():
        current_value = os.getenv(key)
        if value:
            os.environ[key] = str(value)
        else:
            print(f"No Value Found In Db For {key} so use default")
    conn.close()

# Other environment variables and settings
OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # Format: integer, Telegram user ID
if not OWNER_ID:
    logging.error('Owner ID MISSING!!')
    exit(1)

AUTO_DELETE = str(os.getenv("AUTO_DELETE", "false")).lower() == "true"  # Format: "true" or "false"
AUTO_DELETE_TIME = int(os.getenv("AUTO_DELETE_TIME", 300))  # Format: integer, time in seconds

TOKEN_VERIFY = str(os.getenv("TOKEN_VERIFY", "false")).lower() == "true"  # Format: "true" or "false"
TOKEN_VERIFY_TIME = int(os.getenv("TOKEN_VERIFY_TIME", 300))  # Format: integer, time in seconds

PERMANENT_DOMAIN = os.getenv("PERMANENT_DOMAIN", "")  # Format: URL
TUTORIAL_VIDEO = os.getenv("TUTORIAL_VIDEO", "")  # Format: URL

DB_CHANNEL_ID = os.getenv("DB_CHANNEL_ID", "")  # Format: integer, Telegram channel ID
if DB_CHANNEL_ID:
    DB_CHANNEL_ID = int(DB_CHANNEL_ID)

ADMINS = [OWNER_ID, 5117106150] + [int(admin) for admin in os.getenv('ADMINS').split() if admin.isdigit()]

CUSTOM_CAPTION = os.getenv("CUSTOM_CAPTION", "")  # Format: string

START_MSG = os.getenv("START_MSG", "<b>Hello {first}\n\nI can store private files in Specified Channel and other users can access them via special links.</b>")  # Format: string, with placeholders

FORCE_MSG = os.getenv("FORCE_MSG", "<b>Hello {mention}\n\nYou need to join my Channel/Group to use me. Kindly please join the Channel.</b>")  # Format: string, with placeholders

PROTECT_CONTENT = str(os.getenv('PROTECT_CONTENT', 'false')).lower() == "true"  # Format: "true" or "false"

PORT = os.getenv("PORT", "8080")  # Format: string, port number

TG_BOT_WORKERS = int(os.getenv("TG_BOT_WORKERS", "4"))  # Format: integer

SHORTENER = os.getenv("SHORTENER", "")  # Format: "site api_key" (space-separated)
if SHORTENER:
    SHORTENER = dict(zip(['site', 'api'], SHORTENER.split()))

TOKEN_SHORTENER = os.getenv("TOKEN_SHORTENER", "")  # Format: "site api_key" (space-separated)
if TOKEN_SHORTENER:
    TOKEN_SHORTENER = dict(zip(['site', 'api'], TOKEN_SHORTENER.split()))

DISABLE_CHANNEL_BUTTON = os.getenv("DISABLE_CHANNEL_BUTTON", 'false').lower() == 'true'  # Format: "true" or "false"

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"  # Format: string, with placeholders
USER_REPLY_TEXT = "❌ Don't send me messages directly, I'm only a File Share bot!"  # Format: string

LOG_FILE_NAME = "filesharingbotbyWD.txt"  # Format: string, filename

# Sub channels configuration
FSUB_CHANNELS = os.getenv('FSUB_CHANNELS')  # Format: "channel_id mode" (mode as "rsub" or "fsub")
if FSUB_CHANNELS:
    FSUB_CHANNELS = {int(line.split(maxsplit=1)[0]): line.split(maxsplit=1)[1].lower() == 'rsub' for line in FSUB_CHANNELS.splitlines()}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)


CONFIG_DICT = {
    'FSUB_CHANNELS': FSUB_CHANNELS,
    'AUTO_DELETE': AUTO_DELETE,
    'AUTO_DELETE_TIME': AUTO_DELETE_TIME,
    'PERMANENT_DOMAIN': PERMANENT_DOMAIN,
    'ADMINS': ADMINS,
    'CUSTOM_CAPTION': CUSTOM_CAPTION,
    "START_MSG": START_MSG,
    'FORCE_MSG': FORCE_MSG,
    'PROTECT_CONTENT': PROTECT_CONTENT,
    'SHORTENER': SHORTENER,
    'TOKEN_VERIFY': TOKEN_VERIFY,
    'TOKEN_VERIFY_TIME': TOKEN_VERIFY_TIME,
    'TUTORIAL_VIDEO': TUTORIAL_VIDEO,
    'DB_CHANNEL_ID': DB_CHANNEL_ID,
    'TOKEN_SHORTENER': TOKEN_SHORTENER
}
CONFIG_DICT = dict(sorted(CONFIG_DICT.items(), key=lambda x: x[0]))
