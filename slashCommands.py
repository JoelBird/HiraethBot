def slashCommands(tree):

    import discord
    from discord import app_commands
    import os
    import re
    import json
    from re import search
    import time
    import asyncio
    import sys
    from discord.utils import get
    from datetime import datetime
    from timeit import default_timer as timer
    import botFunctions
    from slashCommands import slashCommands
    import requests
    from smartContract import smartContractFunctions
    import random
    import embeds
    import views

    colorCyan = discord.Colour.from_str('#00ffcd')
    colorRed = discord.Colour.from_str('#FF272A')
    colorOrange = discord.Colour.from_str('#FF7A59')
    colorGreen = discord.Colour.from_str('#7DB980')
    colorBlack = discord.Colour.from_str('#0e1522')
    colorWhite = discord.Colour.from_str('#FFFFFF')
    colorPink = discord.Colour.from_str('#ffc0d6')
    colorGold = discord.Colour.from_str('#FDD835')
    

    @tree.command(name='connect_wallets', description='Connect your Wallets for PVP')
    async def connect_wallets(interaction: discord.Interaction, polygon: str = None, ethereum: str = None):
        
        await interaction.response.defer(ephemeral=True)
        await botFunctions.newMemberFunc(str(interaction.user.id), str(interaction.user.name))

        if polygon == None and ethereum == None:
            embed = discord.Embed(title='',description='please insert a polygon or ethereum wallet address to register your Heroes for PVP', color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return

        if polygon != None:
            web3Polygon = await botFunctions.getWeb3('polygon')
            if not web3Polygon.is_address(polygon):
                embed = discord.Embed(title='',description='You did not insert a valid polygon address', color=colorBlack)
                await interaction.followup.send(embed=embed, ephemeral = True)
                return
            
            if not web3Polygon.is_checksum_address(polygon): #checksum is correct format for addresses, they need capitalisation on certain letters, some people dont add
                polygon = web3Polygon.to_checksum_address(polygon)
            
            await botFunctions.setMemberDictValue(interaction.user.id, 'polygonWallet', polygon)
            data = await botFunctions.getWalletDruids(polygon)
            amountOfDruids = str(len(data))
            embed = discord.Embed(title='We detected '+amountOfDruids+' Druids in your wallet',description='Use `/my_heroes` to see your heroes', color=colorGreen)
            await interaction.followup.send(embed=embed, ephemeral = True)
        
        if ethereum != None:
            web3Ethereum = await botFunctions.getWeb3('ethereum')
            if not web3Ethereum.is_address(ethereum):
                embed = discord.Embed(title='',description='You did not insert a valid ethereum address', color=colorBlack)
                await interaction.followup.send(embed=embed, ephemeral = True)
                return

            if not web3Ethereum.is_checksum_address(ethereum):
                ethereum = web3Ethereum.to_checksum_address(ethereum)
            
            await botFunctions.setMemberDictValue(interaction.user.id, 'ethereumWallet', ethereum)
            data = await botFunctions.getWalletKnights(ethereum)
            amountOfKnights = str(len(data))
            embed = discord.Embed(title='We detected '+amountOfKnights+' Knights in your wallet',description='Use `/my_heroes` to see your heroes', color=colorGreen)
            await interaction.followup.send(embed=embed, ephemeral = True)

    
    # @tree.command(name='my_heroes', description='Connect your Wallets for PVP')
    # async def connect_wallets(interaction: discord.Interaction, polygon: str = None, ethereum: str = None):
        
    #     await interaction.response.defer(ephemeral=True)
    #     await botFunctions.newMemberFunc(str(interaction.user.id), str(interaction.user.name))

    
    @tree.command(name='battle', description='Begin a countdown battle!')
    async def connect_wallets(interaction: discord.Interaction, minutes_to_start: int):
        
        await interaction.response.defer(ephemeral=False)
        await botFunctions.newMemberFunc(str(interaction.user.id), str(interaction.user.name))

        nowUnix = await botFunctions.getNowUnix()
        secondsToStart = minutes_to_start * 60
        battleStartUnix = nowUnix + secondsToStart
        timestamp = await botFunctions.unixToTimestamp(battleStartUnix)

        await botFunctions.setServerDictValue('battleStartUnix', str(battleStartUnix))
        dict = {}
        dict[interaction.user.id] = {}

        embed = discord.Embed(title="",description="# A battle has started!\n`"+interaction.user.name + "` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\nParticipants: 0\nRound 1 Begins: "+timestamp, color=colorRed)
        embed.set_image(url = "https://i.postimg.cc/B6FNRfgk/battlebegins.jpg")

        view = discord.ui.View()
        button = views.theButton(label="Join Battle", custom_id='wd421edc13d', style=discord.ButtonStyle.red)
        view.add_item(button)

        message = await interaction.followup.send(embed=embed, view = view, ephemeral = False)
        await botFunctions.setServerDictValue('battleMessageId', str(message.id))
       
        await asyncio.sleep(secondsToStart)

        numberOfRemainingPlayers = int(await botFunctions.getNumberOfRemainingPlayers())
        if numberOfRemainingPlayers < 2:
            embed = discord.Embed(title="Battle Cancelled", description="Not enough heroes joined", color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = False)
            return

        view = discord.ui.View()
        button = views.theButton(label="Roll For Attack", custom_id='awdg423d', style=discord.ButtonStyle.red)
        view.add_item(button)

        options = await botFunctions.getVictimOptions()
        select = views.victimSelect(options=options)
        view.add_item(select)

        roundNumber = 1
        while numberOfRemainingPlayers >= 2:
            
            nowUnix = await botFunctions.getNowUnix()
            end = nowUnix + 30
            timestamp = await botFunctions.unixToTimestamp(end)

            embed = discord.Embed(title=f"Round {roundNumber}", description=f"`Time left:` {timestamp}", color=colorRed)
            embed.set_image(url = "https://i.postimg.cc/XNh88KDn/1v1battle3.jpg")
            await interaction.followup.send(embed=embed, view = view, ephemeral = False)

            await asyncio.sleep(30)

            await botFunctions.autofillForAbsentPlayers()

            await botFunctions.heroesAttackFunc(interaction)
            
            outcomeString = ''
            participantIds = await botFunctions.getAllParticipantIds()
            for id in participantIds:
                memberName = await botFunctions.getParticipantValue(id, 'memberName')
                heroName = await botFunctions.getParticipantValue(id, 'heroName')
                heroClass = await botFunctions.getParticipantValue(id, 'heroClass')
                health = await botFunctions.getParticipantValue(id, 'health')
                if int(health) <= 0:
                    outcomeString = outcomeString + f"`💀 {memberName} | {heroName} - Health: {health}`\n"
                if int(health) > 0:
                    outcomeString = outcomeString + f"`❤️ {memberName} | {heroName} - Health: {health}`\n"
            embed = discord.Embed(title=f"Round {roundNumber} Outcome",description=outcomeString, color=colorBlack)
            embed.set_image(url = "https://i.postimg.cc/PxBxFK0n/wounded-knight.jpg")
            await interaction.followup.send(embed=embed, ephemeral = False)

            await asyncio.sleep(10)

            numberOfRemainingPlayers = int(await botFunctions.getNumberOfRemainingPlayers())
            if numberOfRemainingPlayers == 1:
                heroName, memberName, memberId, heroImage = await botFunctions.getRemainingPlayer()
                embed = discord.Embed(title=f"{memberName} Stands Victorious!", description=f"`{heroName}` is the last remaining Hero", color=colorGold)
                embed.set_image(url = heroImage)
                await interaction.followup.send(embed=embed, ephemeral = False)

                wins = await botFunctions.getMemberDictValue(memberId, 'wins')
                updatedWins = str(int(wins) + 1)
                await botFunctions.setMemberDictValue(interaction.user.id, 'wins', updatedWins)
                return
            
            if numberOfRemainingPlayers == 0:
                embed = discord.Embed(title=f"All heroes have perished", description=f"No one survived the previous Round", color=colorBlack)
                embed.set_image(url = 'https://i.postimg.cc/P5f5RgmB/empty-battlefield.jpg')
                await interaction.followup.send(embed=embed, view = view, ephemeral = False)

                wins = await botFunctions.getMemberDictValue(memberId, 'wins')
                updatedWins = str(int(wins) + 1)
                await botFunctions.setMemberDictValue(interaction.user.id, 'wins', updatedWins)
                return


            await botFunctions.resetPlayerChoices()
            roundNumber = roundNumber + 1


        await botFunctions.resetParticipantsDict()