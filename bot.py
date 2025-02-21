import disnake
from disnake.ext import commands
import aiohttp
import json
import random
import asyncio
from config import TOKEN, ZUKI_API_URL, ZUKI_API_KEY, LOG_CHANNEL_ID, ALLOWED_CHANNEL_IDS, AUTHORIZED_ROLES, FORBIDDEN_TOPICS

# Optimize intents for the bot.
intents = disnake.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    # Optionally, specify test guilds or other startup parameters here.
)

# Create an OpenAI client using the ZukiJourney API settings.
# (Assuming a similar interface to OpenAI; replace with your API client if needed.)
# For demonstration purposes, this example uses aiohttp for API calls.

# Cache for role checks.
role_cache = {}

def contains_forbidden_topic(message: str) -> bool:
    """Check if the message contains any forbidden topic."""
    for topic in FORBIDDEN_TOPICS:
        if topic.lower() in message.lower():
            return True
    return False

def has_authorized_role(member: disnake.Member) -> bool:
    """Optimized role check using caching."""
    cache_key = f"{member.id}_{member.guild.id}"
    if cache_key in role_cache:
        return role_cache[cache_key]
    
    result = any(str(role.id) in AUTHORIZED_ROLES for role in member.roles)
    role_cache[cache_key] = result
    return result

@bot.event
async def on_ready():
    """Event handler when the bot is ready."""
    print(f'Logged in as {bot.user}')
    try:
        # Load command extensions here if needed.
        bot.load_extension("cogs.commands")
        print(f'Commands loaded successfully.')
        activity = disnake.Activity(type=disnake.ActivityType.listening, name="Your commands")
        await bot.change_presence(status=disnake.Status.online, activity=activity)
    except Exception as e:
        print(f"Error loading commands cog: {str(e)}")

@bot.event
async def on_message(message: disnake.Message):
    """Handle incoming messages."""
    # Ignore messages from the bot itself.
    if message.author == bot.user:
        return

    # Check if the user has an authorized role.
    if not has_authorized_role(message.author):
        await message.channel.send("You do not have permission to use this bot.")
        return

    # Process AI queries if the message starts with '!q'
    if message.content.startswith('!q'):
        await message.add_reaction('👍')

        if contains_forbidden_topic(message.content):
            await message.channel.send("This query contains a forbidden topic and will not be processed.")
            return

        # Extract the user query.
        user_input = message.content[len('!q '):].strip()

        # Build the API request.
        headers = {
            'Authorization': f'Bearer {ZUKI_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            "model": "llama-3.1-405b-instruct",  # Specify the desired model.
            "messages": [{"role": "user", "content": user_input}],
            "temperature": 0,
            "max_tokens": 150,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "style": "formal"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(ZUKI_API_URL, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        generated_text = result.get('choices', [{}])[0].get('message', {}).get('content', 'Response not found')
                        await message.channel.send(f'{message.author.mention} Answer from Lucifer Bot: {generated_text}')
                    else:
                        print(f"Error: Status code {response.status}")
        except Exception as e:
            await message.channel.send(f'{message.author.mention} An error occurred: {str(e)}')
    
    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(TOKEN)
