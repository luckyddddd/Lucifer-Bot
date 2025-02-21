# Lucifer-Bot
Lucifer Bot is a feature-rich Discord bot built with [disnake](https://docs.disnake.dev/) that integrates AI capabilities through the ZukiJourney API. It offers a variety of functions, including:

- **AI-Powered Queries:** Use commands (e.g., `!q`) to send questions to the ZukiJourney API and receive intelligent answers.
- **Role Management:** Assign roles using slash commands such as `/give_role` and create roles with `/create_role`.
- **Meme Commands:** Fetch and display random memes from a local cache.
- **Content Moderation:** Automatically detect forbidden topics in user messages.
- **Logging:** Log important actions like role creation and command usage.

## Features

- **Asynchronous & Optimized:** Uses asynchronous operations, caching, and a connection pool for SQLite to ensure high performance.
- **Environment-Driven Configuration:** No hard-coded tokens or API keys; configuration values are loaded from environment variables.
- **Easy Deployment:** Set up your environment variables, install the dependencies, and launch the bot.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/lucifer-bot.git
   cd lucifer-bot
2. Install dependencies:
pip install -r requirements.txt

3. Configure your environment:
DISCORD_TOKEN=your_bot_token
ZUKI_API_URL=https://api.zukijourney.com/v1
ZUKI_API_KEY=your_zuki_api_key
LOG_CHANNEL_ID=123456789012345678
ALLOWED_CHANNEL_IDS=123456789012345678,987654321098765432
AUTHORIZED_ROLES=123456789012345678,234567890123456789

4. Run the bot:
python bot.py

