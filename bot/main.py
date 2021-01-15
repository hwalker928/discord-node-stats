import discord
from discord.ext import commands
from discord.ext import tasks
import aiohttp
import json

intents = discord.Intents.default()
intents.members = True

with open('config.json') as config_jsonfile:
    config_1 = json.load(config_jsonfile)
    prefix_to_use = config_1["botPrefix"]
bot = commands.Bot(command_prefix=prefix_to_use, intents=intents)
with open('config.json') as bot.config_jsonfile:
    bot.config_json = json.load(bot.config_jsonfile)
    bot.node_name = bot.config_json["nodeName"]

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
    update_channel = bot.get_channel(bot.config_json["channelUpdates"])
    node_owner = bot.get_user(bot.config_json["nodeOwnerID"])
    await update_channel.send(f":warning: {node_owner.mention}, {bot.node_name} is down! :warning:")

@bot.event
async def on_ready():
    print("The monitoring has started.")
    server_checker.start()
    bot.task_active = True

async def nodeOwnerCheck(ctx):
    node_owner = bot.get_user(bot.config_json["nodeOwnerID"])
    return ctx.message.author.id == node_owner.id

@bot.command(aliases=["m", "disable", "noalert", "noalerts", "turnoff", "shutdown", "start", "turnon", "alerts", "alertsenable", "enable"])
@commands.check(nodeOwnerCheck)
async def maintanance(ctx):
    if bot.task_active:
        server_checker.cancel()
        bot.task_active = False
        await ctx.send(":x: Monitoring disabled.")
    else:
        server_checker.restart()
        bot.task_active = True
        await ctx.send(":white_check_mark: Monitoring enabled.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You must be the node owner to run this!")
    else:
        await ctx.send(f"Error: `{error}`")

bot.run(bot.config_json["token"])