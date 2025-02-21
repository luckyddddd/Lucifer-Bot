import os

# Load configuration from environment variables.
# Make sure to set these in your environment or in a .env file.
TOKEN = os.environ.get("DISCORD_TOKEN")
ZUKI_API_URL = os.environ.get("ZUKI_API_URL")
ZUKI_API_KEY = os.environ.get("ZUKI_API_KEY")

# Convert IDs to integers; if not set, default to 0.
try:
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "0"))
except ValueError:
    LOG_CHANNEL_ID = 0

# Allowed channel IDs provided as a comma-separated list.
ALLOWED_CHANNEL_IDS = [int(x) for x in os.environ.get("ALLOWED_CHANNEL_IDS", "").split(",") if x]

# Authorized role IDs provided as a comma-separated list.
AUTHORIZED_ROLES = os.environ.get("AUTHORIZED_ROLES", "").split(",")

# Forbidden topics list.
FORBIDDEN_TOPICS = [
    "politics",
    "violence",
    "drugs",
    "hate speech",
    "sex",
    "racism"
]
