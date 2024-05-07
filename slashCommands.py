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
    import views

    colorCyan = discord.Colour.from_str('#00ffcd')
    colorRed = discord.Colour.from_str('#FF272A')
    colorOrange = discord.Colour.from_str('#FF7A59')
    colorGreen = discord.Colour.from_str('#7DB980')
    colorBlack = discord.Colour.from_str('#0e1522')
    colorWhite = discord.Colour.from_str('#FFFFFF')
    colorPink = discord.Colour.from_str('#ffc0d6')
    colorGold = discord.Colour.from_str('#FDD835')
    color1v1 = discord.Colour.from_str('#A86051')


    @tree.command(name='leaderboard', description='View the top Hiraeth PVP players')
    async def leaderboard(interaction: discord.Interaction):

            await interaction.response.defer(ephemeral=True)
            
            leaderboardString = ''
            sorted_data = await botFunctions.extractAndSortWins()
            for wins, name in sorted_data:
                leaderboardString = leaderboardString + f"🪙 `{name} - {wins} wins`\n"

            embed1 = discord.Embed(title="Welcome to the Leaderboard", description = "Here you can see how you compare to the other participants of Hiraeth PVP", color=colorGold)
            embed1.set_thumbnail(url = "https://i.postimg.cc/QxcWv8XY/trophy-1f3c6.png")

            embed2 = discord.Embed(title=':trophy: Top Participants', description = 'This leaderboard displays Participants based on their Wins\n\n'+leaderboardString, color=colorGold)
            embedList = [embed1, embed2]
            await interaction.followup.send(embeds=embedList, ephemeral=True)


    @tree.command(name='add_staff', description='Add member to staff')
    async def add_staff(interaction: discord.Interaction, member: discord.Member):
            
        await interaction.response.defer(ephemeral=True)
        
        isStaff, embed = await botFunctions.isStaff(interaction.user.id)
        if isStaff == 'false':
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
    
        staffList = await botFunctions.getServerDictValue('staff')
        staffList.append(str(member.id))
        await botFunctions.setServerDictValue('staff', staffList)
        memberName = '<@' + str(member.id) + '>'
        embed = discord.Embed(title="",description=f"Successfully added {memberName} to Staff", color=colorGreen)
        await interaction.followup.send(embed=embed, ephemeral = True)


    @tree.command(name='remove_staff', description='Remove member of staff')
    async def remove_staff(interaction: discord.Interaction, member: discord.Member):
        
        await interaction.response.defer(ephemeral=True)
        
        isStaff, embed = await botFunctions.isStaff(interaction.user.id)
        if isStaff == 'false':
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
        
        staffList = await botFunctions.getServerDictValue('staff')
        staffList.remove(str(member.id))
        await botFunctions.setServerDictValue('staff', staffList)
        memberName = '<@' + str(member.id) + '>'
        embed = discord.Embed(title="",description=f"Successfully removed {memberName} from Staff", color=colorGreen)
        await interaction.followup.send(embed=embed, ephemeral = True)


    @tree.command(name='list_staff', description='List staff members')
    async def list_staff(interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        staffList = await botFunctions.getServerDictValue('staff')
        string = ''
        for memberId in staffList:
            memberName = '<@' + str(memberId) + '>'
            string = string + memberName + '\n'

        embed = discord.Embed(title="Staff List:",description=string, color=colorCyan)
        embed.set_thumbnail(url = "https://i.postimg.cc/bNF5ZpZs/staff.png")
        await interaction.followup.send(embed=embed, ephemeral = True)


    @tree.command(name='set_tournament', description='Set a new Tournament (Wipes previous tournament wins)')
    async def set_tournament(interaction: discord.Interaction, tournament_name: str):

        await interaction.response.defer(ephemeral=True)

        isStaff, embed = await botFunctions.isStaff(interaction.user.id)
        if isStaff == 'false':
            await interaction.followup.send(embed=embed, ephemeral = True)
            return

        await botFunctions.setServerDictValue('druidTournamentWins', '0')
        await botFunctions.setServerDictValue('knightTournamentWins', '0')
        await botFunctions.setServerDictValue('isTournamentActive', 'true')
        await botFunctions.setServerDictValue('tournamentName', tournament_name)
        embed = discord.Embed(title="",description=f"Successfully Set Tournament", color=colorGreen)
        await interaction.followup.send(embed=embed, ephemeral = True)


    @tree.command(name='disable_tournament', description='Disable Tournament (Wipes tournament wins)')
    async def disable_tournament(interaction: discord.Interaction):
        
        await interaction.response.defer(ephemeral=True)

        isStaff, embed = await botFunctions.isStaff(interaction.user.id)
        if isStaff == 'false':
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
        
        await botFunctions.setServerDictValue('druidTournamentWins', '0')
        await botFunctions.setServerDictValue('knightTournamentWins', '0')
        await botFunctions.setServerDictValue('isTournamentActive', 'false')
        await botFunctions.setServerDictValue('tournamentName', 'false')
        embed = discord.Embed(title="",description=f"Successfully Disabled Tournament", color=colorGreen)
        await interaction.followup.send(embed=embed, ephemeral = True)
    

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
            embed = discord.Embed(description='We detected '+amountOfDruids+' Druids in your wallet', color=colorGreen)
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
            embed = discord.Embed(description='We detected '+amountOfKnights+' Knights in your wallet', color=colorGreen)
            await interaction.followup.send(embed=embed, ephemeral = True)



    @tree.command(name='cancel_battle', description='Cancel the current battle')
    async def cancel_battle(interaction: discord.Interaction):
        
        await interaction.response.defer(ephemeral=True)

        isStaff, embed = await botFunctions.isStaff(interaction.user.id)
        if isStaff == 'false':
            await interaction.followup.send(embed=embed, ephemeral = True)
            return

        battleInSession = await botFunctions.getServerDictValue('battleInSession')
        if battleInSession == 'false':
            embed = discord.Embed(title='',description='There is no active battle', color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return

        battleChannelId = int(await botFunctions.getServerDictValue('battleChannelId'))
        battleChannel = interaction.client.get_channel(battleChannelId)
        

        await botFunctions.cancelBattleMessage(interaction.client)

        await botFunctions.resetPlayerChoices()
        await botFunctions.resetServerDict()
        
        embed = discord.Embed(title="Battle Cancelled", description="`/cancel_battle` was used", color=colorBlack)
        embed.set_thumbnail(url = "https://i.postimg.cc/wMJQnydT/fotor-ai-20240403211513.jpg")
        await battleChannel.send(embed = embed)

        embed = discord.Embed(title="", description="Battle cancelled successfully", color=colorGreen)
        await interaction.followup.send(embed=embed, ephemeral = True)


    
    @tree.command(name='battle', description='Battle begins when countdown ends')
    async def battle(interaction: discord.Interaction, minutes_to_start: int):
        
        await interaction.response.defer(ephemeral=True)

        battleInSession = await botFunctions.getServerDictValue('battleInSession')
        if battleInSession == 'true':
            embed = discord.Embed(title="",description="A battle has already started", color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
            
        await botFunctions.newMemberFunc(str(interaction.user.id), str(interaction.user.name))

        nowUnix = await botFunctions.getNowUnix()
        secondsToStart = minutes_to_start * 60
        battleStartUnix = nowUnix + secondsToStart
        timestamp = await botFunctions.unixToTimestamp(battleStartUnix)

        await botFunctions.setServerDictValue('battleStartUnix', str(battleStartUnix))
        dict = {}
        dict[interaction.user.id] = {}

        embed = discord.Embed(title="",description="# A battle has started!\n`"+interaction.user.name + "` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Participants: 0`\n`Round 1 Begins: `"+timestamp, color=colorRed)
        embed.set_image(url = "https://i.postimg.cc/FKBmytTy/battlebegins3.jpg")

        view = discord.ui.View()
        button = views.theButton(label="Join Battle", custom_id='wd421edc13d', style=discord.ButtonStyle.red)
        view.add_item(button)

        message = await interaction.channel.send(embed=embed, view = view)
        await botFunctions.setServerDictValue('battleMessageId', str(message.id))
        await botFunctions.setServerDictValue('battleChannelId', str(message.channel.id))
        await botFunctions.setServerDictValue('battleInSession', 'true')
        await botFunctions.setServerDictValue('battleMode', 'countdown')
       
        await asyncio.sleep(secondsToStart)

        numberOfRemainingPlayers = int(await botFunctions.getNumberOfRemainingPlayers())
        if numberOfRemainingPlayers < 2:
            embed = discord.Embed(title="Battle Cancelled", description="Not enough heroes joined", color=colorBlack)
            embed.set_thumbnail(url = "https://i.postimg.cc/wMJQnydT/fotor-ai-20240403211513.jpg")
            await botFunctions.setServerDictValue('battleInSession', 'false')
            await interaction.followup.send(embed=embed, ephemeral = False)
            await botFunctions.cancelBattleMessage(interaction.client)
            return
        
        await botFunctions.startBattle(interaction.client)



    @tree.command(name='battle_participants', description='Battle begins when participants reached')
    async def battle_participants(interaction: discord.Interaction, participants_to_start: int):
        
        await interaction.response.defer(ephemeral=True)

        isStaff, embed = await botFunctions.isStaff(interaction.user.id)
        if isStaff == 'false':
            await interaction.followup.send(embed=embed, ephemeral = True)
            return

        battleInSession = await botFunctions.getServerDictValue('battleInSession')
        if battleInSession == 'true':
            embed = discord.Embed(title="", description="A battle has already started", color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
        
        if participants_to_start < 2:
            embed = discord.Embed(title="", description="Must be at least 2 participants", color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return

        embed = discord.Embed(title="",description=f"# A battle has started!\n`{interaction.user.name}` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Participants: 0/{str(participants_to_start)}`\n`Round 1 Begins when {str(participants_to_start)}/{str(participants_to_start)} participants have joined`", color=colorRed)
        embed.set_image(url = "https://i.postimg.cc/FKBmytTy/battlebegins3.jpg")

        view = discord.ui.View()
        button = views.theButton(label="Join Battle", custom_id='wd421edc13d', style=discord.ButtonStyle.red)
        view.add_item(button)

        message = await interaction.channel.send(embed=embed, view = view)

        await botFunctions.setServerDictValue('battleMessageId', str(message.id))
        await botFunctions.setServerDictValue('battleChannelId', str(message.channel.id))
        await botFunctions.setServerDictValue('battleInSession', 'true')
        await botFunctions.setServerDictValue('battleMode', 'participants')
        await botFunctions.setServerDictValue('participantsToStart', str(participants_to_start))



    @tree.command(name='battle_set', description='Battle begins with /battle_start')
    async def battle_set(interaction: discord.Interaction):
        
        await interaction.response.defer(ephemeral=True)

        isStaff, embed = await botFunctions.isStaff(interaction.user.id)
        if isStaff == 'false':
            await interaction.followup.send(embed=embed, ephemeral = True)
            return

        battleInSession = await botFunctions.getServerDictValue('battleInSession')
        if battleInSession == 'true':
            embed = discord.Embed(title="", description="A battle has already started", color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return

        numberOfParticipants = await botFunctions.getAllParticipantIds()
        numberOfParticipants = str(len(numberOfParticipants))
        embed = discord.Embed(title="",description=f"# A battle has started!\n`{interaction.user.name}` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Participants: {numberOfParticipants}`\n`Round 1 Begins when staff runs /battle_start`", color=colorRed)
        embed.set_image(url = "https://i.postimg.cc/FKBmytTy/battlebegins3.jpg")

        view = discord.ui.View()
        button = views.theButton(label="Join Battle", custom_id='wd421edc13d', style=discord.ButtonStyle.red)
        view.add_item(button)

        message = await interaction.channel.send(embed=embed, view = view)

        await botFunctions.setServerDictValue('battleMessageId', str(message.id))
        await botFunctions.setServerDictValue('battleChannelId', str(message.channel.id))
        await botFunctions.setServerDictValue('battleInSession', 'true')
        await botFunctions.setServerDictValue('battleMode', 'staff')
        await botFunctions.setServerDictValue('battleSet', 'true')
        

    @tree.command(name='battle_start', description='Start a set battle')
    async def battle_start(interaction: discord.Interaction):
        
        await interaction.response.defer(ephemeral=True)

        isStaff, embed = await botFunctions.isStaff(interaction.user.id)
        if isStaff == 'false':
            await interaction.followup.send(embed=embed, ephemeral = True)
            return

        battleSet = await botFunctions.getServerDictValue('battleSet')
        if battleSet == 'false':
            embed = discord.Embed(title="", description="There is no set battle to start", color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
        
        numberOfParticipants = await botFunctions.getAllParticipantIds()
        numberOfParticipants = len(numberOfParticipants)
        if numberOfParticipants < 2:
            embed = discord.Embed(title="", description="There must be at least 2 players to start", color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
        
        embed = discord.Embed(title="", description="Battle has been started", color=colorGreen)
        await interaction.followup.send(embed=embed, ephemeral = True)
        
        await botFunctions.startBattle(interaction.client)



    @tree.command(name='battle_ghost', description='Battle the ghost of a random members knight/druid')
    async def battle_ghost(interaction: discord.Interaction):
        
        await interaction.response.defer(ephemeral=False)

        memberName, memberId, heroName = await botFunctions.getRandomHero(interaction.user.id)
        isAlreadyParticipant = await botFunctions.newParticipant(memberName, memberId, heroName)
        attackerNameString = '<@' + str(interaction.user.id) + '>'
        victimNameString = '<@' + str(memberId) + '>'
        

        embed = discord.Embed(title="",description=f"# {attackerNameString} has challenged the ghost of {victimNameString}\n## Rules:\nAt the start of every Round, you are required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of each Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Round 1 Begins when you join the battle, {interaction.user.name}`", color=colorCyan)
        embed.set_image(url = "https://i.postimg.cc/rp6R5wWV/ghost.jpg")
        view = discord.ui.View()
        button = views.theButton(label="Join Battle", custom_id='wd421edc13d', style=discord.ButtonStyle.blurple)
        view.add_item(button)
        embed.set_footer(text="", icon_url="https://i.postimg.cc/44HQ2t7X/thing.png")
        message = await interaction.followup.send(embed=embed, view=view)

        await botFunctions.setServerDictValue('battleChannelId', str(interaction.channel.id))
        await botFunctions.setServerDictValue('battleMessageId', str(message.id))
        await botFunctions.setServerDictValue('battleInSession', 'true')
        await botFunctions.setServerDictValue('battleMode', 'ghost')
        await botFunctions.setServerDictValue('ghostBattleStarterId', str(interaction.user.id))

    
    @tree.command(name='battle_1v1', description='Select an opponent to battle 1v1')
    async def battle_1v1(interaction: discord.Interaction, member: discord.Member):
        
        await interaction.response.defer(ephemeral=False)

        attackerNameString = '<@' + str(interaction.user.id) + '>'
        victimNameString = '<@' + str(interaction.user.id) + '>'

        embed = discord.Embed(title="",description=f"# {attackerNameString} has challenged {victimNameString}\n## Rules:\nAt the start of every Round, you are required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of each Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Round 1 Begins when you and {member.name} join the battle`", color=color1v1)
        embed.set_image(url = "https://i.postimg.cc/8c8Kb92v/knight.jpg")
        view = discord.ui.View()
        button = views.theButton(label="Join Battle", custom_id='wd421edc13d', style=discord.ButtonStyle.red)
        view.add_item(button)
        message = await interaction.followup.send(embed=embed, view=view)

        await botFunctions.setServerDictValue('battleChannelId', str(interaction.channel.id))
        await botFunctions.setServerDictValue('battleMessageId', str(message.id))
        await botFunctions.setServerDictValue('battleInSession', 'true')
        await botFunctions.setServerDictValue('battleMode', '1v1')
        await botFunctions.setServerDictValue('1v1BattleStarterId', str(interaction.user.id))
        await botFunctions.setServerDictValue('1v1BattleVictimId', str(member.id))