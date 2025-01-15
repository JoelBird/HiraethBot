import discord
from discord import app_commands
import json
import asyncio
from slashCommands import slashCommands
import botFunctions #Like this to avoid circular imports error, import whole module
import views
import random
import aioschedule as schedule
import time
import nest_asyncio
from discord import Activity, ActivityType
nest_asyncio.apply() #used to fix twint RuntimeError: This event loop is already running in async function

colorCyan = discord.Colour.from_str('#00ffcd')
colorRed = discord.Colour.from_str('#FF272A')
colorOrange = discord.Colour.from_str('#FF7A59')
colorGreen = discord.Colour.from_str('#7DB980')
colorBlack = discord.Colour.from_str('#0e1522')
colorWhite = discord.Colour.from_str('#FFFFFF')
colorPink = discord.Colour.from_str('#ffc0d6')
colorGold = discord.Colour.from_str('#FDD835')


global isThreadDeleted
isThreadDeleted = False

class HiraethBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False  #we use this so the bot doesn't sync commands more than once

    async def on_ready(self):

        await self.change_presence(activity=Activity(type=ActivityType.playing, name="Hiraeth PVP"))

        #How to make buttons work after bot restart = You need to make the view persistent
        #Give every element in that view a unique ID, set the timeout to None and inside the setup_hook you need to do bot.add_view(YourView())
        HiraethBot.add_view(views.joinBattle())


        await self.wait_until_ready()
        if not self.synced:  #check if slash commands have been synced
            await tree.sync(
            )  #guild specific: leave blank if global (global registration can take 1-24 hours)
            self.synced = True
        print(f"We have logged in as {self.user}.")



HiraethBot = HiraethBot()
tree = app_commands.CommandTree(HiraethBot)

slashCommands(tree)



f = open("tokens")
s = f.read()
tokensDict = json.loads(s)
HiraethBotToken = tokensDict["HiraethBotToken"]


HiraethBot.run(str(HiraethBotToken))

