import discord
import botFunctions
import random
import json
import datetime
import views


colorCyan = discord.Colour.from_str('#00ffcd')
colorRed = discord.Colour.from_str('#FF272A')
colorOrange = discord.Colour.from_str('#FF7A59')
colorGreen = discord.Colour.from_str('#7DB980')
colorBlack = discord.Colour.from_str('#0e1522')
colorWhite = discord.Colour.from_str('#FFFFFF')
colorPink = discord.Colour.from_str('#ffc0d6')
colorGold = discord.Colour.from_str('#FDD835')


async def leaderboard(guild):

            topParticipantsList = await botFunctions.extract_and_sort_tokens(guild.name, guild.name+"Tokens")
            # Initialize an empty string to store the result
            result_string = ""
            # Iterate through the list
            for index, (tokens, name, percentage) in enumerate(topParticipantsList, start=1):
                # Add position, name, and tokens to the result string
                if str(guild.id) == '1131699351496962069': #OpenProj server Id
                    result_string += f"`{index}` - {name} - `{tokens}` :coin: - " + str(percentage) +"% chance of winning\n"
                else:
                    result_string += f"`{index}` - {name} - `{tokens}` :coin:\n"

            embed = discord.Embed(title=':trophy: Top Participants', description = 'This leaderboard displays Participants based on the tokens they currently have in this contest\n'+result_string, color=openProjCyan)
            return(embed)
