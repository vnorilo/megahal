import discord
from discord.ext import commands
import megahal
import zipfile
import pickle
import os
import json
from checkpoint import CheckpointSaver

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
        self.checkpoint_saver = CheckpointSaver(brain_file)

    async def setup_hook(self):
        loaded_brain = self.checkpoint_saver.load_checkpoint()
        if loaded_brain:
            self.megahal = loaded_brain
        else:
            self.megahal = megahal.MegaHAL()
            print(f"No existing brain found at: {self.brain_file}, starting fresh")

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
                self.checkpoint_saver.save_checkpoint(self.megahal)
                
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
