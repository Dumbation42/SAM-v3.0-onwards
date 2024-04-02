from os import remove
from json import load
from io import BytesIO
from aiosqlite import connect
from asyncio import sleep, run
from freeGPT import AsyncClient
from discord.ui import Button, View
from discord.ext.commands import Bot
from aiohttp import ClientSession, ClientError
from discord import Intents, Embed, File, Status, Activity, ActivityType, Colour
from discord.app_commands import (
    describe,
    checks,
    BotMissingPermissions,
    MissingPermissions,
    CommandOnCooldown,
)

intents = Intents.default()
intents.message_content = True
bot = Bot(command_prefix="!", intents=intents, help_command=None)
db = None
server_memory = {}
textCompModels = ["gpt3"]
imageGenModels = ["prodia"]
botpersonality = "GPT-3"

async def init_db():
    return await connect("database.db")

@bot.event
async def on_ready():
    print(f"\033[1;94m INFO \033[0m| {bot.user} has connected to Discord.")
    global db
    db = await connect("database.db")
    async with db.cursor() as cursor:
        await cursor.execute(
            "CREATE TABLE IF NOT EXISTS database(guilds INTEGER, channels INTEGER, models TEXT)"
        )
    print("\033[1;94m INFO \033[0m| Database connection successful.")
    sync_commands = await bot.tree.sync()
    print(f"\033[1;94m INFO \033[0m| Synced {len(sync_commands)} command(s).")
    while True:
        await bot.change_presence(
            status=Status.online,
            activity=Activity(
                type=ActivityType.playing,
                name="SAM v3.0",
            ),
        )
        await sleep(300)

@bot.event
async def on_message(message):
    global server_memory

    if message.author.bot:
        return

    if not message.guild or message.content.startswith('!'):
        return

    if not bot.user.mentioned_in(message):
        return

    if "GenerateImage" in message.content:
        server_id = message.guild.id
        image_prompt = message.content.replace("GenerateImage", "").strip()
        question_to_gpt3 = f"This is an automated prompt used for an ai moderated blacklist for an image generator, please only respond with yes or no: Is the following prompt likely to generate content that is considered NSFW (Pornographic Content or Nudity)? | Prompt: '{image_prompt}'"

        try:
            gpt3_response = await AsyncClient.create_completion("gpt3", question_to_gpt3)
            print(gpt3_response)
            content_safe = "No" in gpt3_response
        except Exception as e:
            print(f"An error occurred querying GPT-3: {e}")
            content_safe = False

        if content_safe:
            async with message.channel.typing():
                try:
                    image_response = await AsyncClient.create_generation("prodia", image_prompt)
                    await message.channel.send(file=File(fp=BytesIO(image_response), filename="generated_image.png"))
                except Exception as e:
                    print(f"An error occurred generating image: {e}")
        else:
            await message.channel.send("I just don't feel up to the task right now.")
    elif "ContextRefresh" in message.content:
        server_memory = {}
        await message.channel.send("Server Context Cleared")
        
    elif "SetPersonality" in message.content:
        parts = message.content.split("SetPersonality", 1)
        if len(parts) > 1:
            global botpersonality
            botpersonality = parts[1].strip()
            server_memory = {}
            await message.channel.send(f"Personality Set To: {botpersonality}")
    else:
        prompt = message.content.strip()
        server_id = message.guild.id
        server_last_response = server_memory.get(server_id, "")
        full_prompt = f"GPT-3 Last Response: {server_last_response} | Current Prompt (Ignore '@Bot User ID Here') (Respond in the style of {botpersonality}): {prompt}".strip()

        async with message.channel.typing():
            try:
                response = await AsyncClient.create_completion("gpt3", full_prompt)
                server_memory[server_id] = response
                await message.channel.send(response)
            except Exception as e:
                print(f"An error occurred: {e}")

    await bot.process_commands(message)

if __name__ == "__main__":
    with open("config.json", "r") as file:
        config = load(file)
    bot.run(config["BOT_TOKEN"])
