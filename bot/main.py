from discord.ext import commands
from discord.ext import tasks
import aiohttp
import json

bot = commands.Bot(command_prefix="!")
with open('config.json') as bot.config_jsonfile:
    bot.config_json = json.load(bot.config_jsonfile)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(bot.config_json["token"])