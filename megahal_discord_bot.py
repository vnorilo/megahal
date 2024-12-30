import discord
from discord.ext import commands
import megahal
import zipfile
import pickle
import os
import json  # Added to handle JSON configuration

def load_config():
    config_path = 'config.json'
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"{config_path} not found. Please create it and add your Discord token.")
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

# Load configuration from config.json
config = load_config()
DISCORD_TOKEN = config.get('DISCORD_TOKEN')

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in config.json")

class MegaHALBot(commands.Bot):
    def __init__(self, brain_file="megahal.pkl", learn=True):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.brain_file = brain_file
        self.learn_mode = learn
        self.megahal = None

    async def setup_hook(self):
        if os.path.exists(self.brain_file):
            try:
                with zipfile.ZipFile(self.brain_file, 'r') as zipf:
                    with zipf.open('checkpoint.pkl') as pickle_file:
                        self.megahal = pickle.load(pickle_file)
                print(f"Successfully loaded brain from: {self.brain_file}")
            except Exception as e:
                print(f"Error loading brain: {e}")
                self.megahal = megahal.MegaHAL()
        else:
            self.megahal = megahal.MegaHAL()
            print(f"No existing brain found at: {self.brain_file}, starting fresh")

    @commands.command()
    async def toggle_learning(self, ctx):
        self.learn_mode = not self.learn_mode
        await ctx.send(f"Learning mode is now {'enabled' if self.learn_mode else 'disabled'}")

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)
        if self.user in message.mentions:
            clean_content = message.clean_content.replace(f'@{self.user.name}', '').strip()
            if not clean_content:
                await message.channel.send("You sent an empty message")
                return
            response = self.megahal.respond(clean_content)
            if self.learn_mode:
                self.megahal.learn(clean_content)
            await message.channel.send(response)

bot = MegaHALBot(
   brain_file="megahal.pkl",  # Brain file path
   learn=True  # Start with learning enabled
)

@bot.event
async def on_ready():
   print(f'Bot {bot.user} is now running!')
   print(f'Brain file: {bot.brain_file}')
   print(f'Learning mode: {"enabled" if bot.learn_mode else "disabled"}')

bot.run(DISCORD_TOKEN)
