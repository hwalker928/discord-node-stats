import discord
from discord.ext import commands
from discord.ext import tasks
import aiohttp
import json

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
with open('config.json') as bot.config_jsonfile:
    bot.config_json = json.load(bot.config_jsonfile)

@tasks.loop(seconds=60)
async def server_checker():
    try:
        url = "http://" + bot.config_json["webserverIP"] + ":" + str(bot.config_json["webserverPort"])
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url + "/ram") as r:
                mem_per = int(round(float(await r.text())))
            async with cs.get(url + "/cpu") as r:
                cpu_per = int(round(float(await r.text())))
        if mem_per + cpu_per / 2 > 20:
            await server_good(cpu_per, mem_per)
        else:
            await server_idle(cpu_per, mem_per)
    except:
        await server_down()

async def server_good(cpu, ram):
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f'CPU: {cpu}% | RAM: {ram}%'))

async def server_idle(cpu, ram):
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name=f'CPU: {cpu}% | RAM: {ram}%'))

async def server_down():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name=f'OFFLINE'))
    chnl = bot.get_channel(bot.config_json["channelUpdates"])
    usr = bot.get_user(bot.config_json["nodeOwnerID"])
    nodeName = bot.config_json["nodeName"]
    await chnl.send(f":warning: {usr.mention}, {nodeName} is down! :warning:")

@bot.event
async def on_ready():
    print("started")
    server_checker.start()

bot.run(bot.config_json["token"])