import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
# BOT_TOKEN = str(os.getenv("GROUPS_ID"))
CHANNEL_ID = str(os.getenv("CHANNEL_ID"))
UZOMAN_CHANNEL_ID = str(os.getenv("UZOMAN_CHANNEL_ID"))
DATABASE = str(os.getenv("DATABASE"))
PGUSER = str(os.getenv("PGUSER"))
PGPASSWORD = str(os.getenv("PGPASSWORD"))

SLEEP_TIME = .3


ip = str(os.getenv("ip"))

# webhook settings
# Public base url where your external nginx terminates TLS, e.g. https://bot.example.com
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", BOT_TOKEN)
WEBHOOK_PATH = f"/bot/webhook/{WEBHOOK_SECRET}/"
WEBHOOK_URL = f"{PUBLIC_BASE_URL}{WEBHOOK_PATH}" if PUBLIC_BASE_URL else ""



I18N_DOMAIN = 'testbot'
BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = BASE_DIR / 'locales'

WEBHOOK_SSL_CERT = BASE_DIR / "webhook_cert.pem"
WEBHOOK_SSL_PRIV = BASE_DIR / "webhook_pkey.pem"

