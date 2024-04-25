import discord
import json
import asyncio
import datetime
from discord.ext import tasks
import requests
from smartContract import smartContractFunctions
import views
from binance.client import Client
from web3 import Web3 #was using python 3.11.1 64 bit, got package error, had to uninstall it and install 3.9.11 64 bit for it to work https://www.python.org/downloads/release/python-3911/
from web3.middleware import geth_poa_middleware
import modals
import random
import pyshorteners
import re
import embeds
from moralis import evm_api

colorCyan = discord.Colour.from_str('#00ffcd')
colorRed = discord.Colour.from_str('#FF272A')
colorOrange = discord.Colour.from_str('#FF7A59')
colorGreen = discord.Colour.from_str('#7DB980')
colorBlack = discord.Colour.from_str('#0e1522')
colorWhite = discord.Colour.from_str('#FFFFFF')
colorPink = discord.Colour.from_str('#ffc0d6')
colorGold = discord.Colour.from_str('#FDD835')

async def startBattle(bot):


        battleMode = int(await getServerDictValue('battleMode'))
        if battleMode != 'ghost':
            await cancelBattleMessage(bot)

        battleChannelId = int(await getServerDictValue('battleChannelId'))
        battleChannel = bot.get_channel(battleChannelId)
        
        view = discord.ui.View()
        button = views.theButton(label="Roll For Attack", custom_id='awdg423d', style=discord.ButtonStyle.red)
        view.add_item(button)

        button = views.theButton(label="Roll For Defence", custom_id='awdwad1312', style=discord.ButtonStyle.blurple)
        view.add_item(button)

        options = await getVictimOptions()
        select = views.victimSelect(options=options)
        view.add_item(select)

        participantNames = ''
        participantIds = await getAllParticipantIds()
        for memberId in participantIds:
            memberNameString = '<@' + str(memberId) + '>'
            participantNames = participantNames + memberNameString + '\n'
        
        embed = discord.Embed(title=f"Battle has commenced!", description=f"**Participants:**\n{participantNames}", color=colorGold)
        embed.set_image(url = "https://i.postimg.cc/wMJQnydT/fotor-ai-20240403211513.jpg")
        await battleChannel.send(embed=embed)

        await asyncio.sleep(15)

        numberOfRemainingPlayers = int(await getNumberOfRemainingPlayers())
        roundNumber = 1
        while numberOfRemainingPlayers >= 2:
            
            nowUnix = await getNowUnix()
            end = nowUnix + 30
            timestamp = await unixToTimestamp(end)

            embed = discord.Embed(title=f"Round {roundNumber}", description=f"`Time left:` {timestamp}", color=colorRed)
            embed.set_image(url = "https://i.postimg.cc/4NXdnq89/1v1battle3.jpg")
            await battleChannel.send(embed=embed, view = view)

            await asyncio.sleep(30)

            await autofillForAbsentPlayers()

            await heroesAttackFunc(battleChannel)
            
            outcomeString = ''
            participantIds = await getAllParticipantIds()
            for id in participantIds:
                memberName = await getParticipantValue(id, 'memberName')
                heroName = await getParticipantValue(id, 'heroName')
                heroClass = await getParticipantValue(id, 'heroClass')
                health = await getParticipantValue(id, 'health')
                if int(health) <= 0:
                    outcomeString = outcomeString + f"`💀 {memberName} | {heroName} - Health: {health}`\n"
                if int(health) > 0:
                    outcomeString = outcomeString + f"`❤️ {memberName} | {heroName} - Health: {health}`\n"
            embed = discord.Embed(title=f"Round {roundNumber} Outcome",description=outcomeString, color=colorBlack)
            embed.set_image(url = "https://i.postimg.cc/PxBxFK0n/wounded-knight.jpg")
            await battleChannel.send(embed=embed)

            await asyncio.sleep(10)

            numberOfRemainingPlayers = int(await getNumberOfRemainingPlayers())
            if numberOfRemainingPlayers == 1:
                heroName, memberName, memberId, heroImage = await getRemainingPlayer()
                knightWins = await getServerDictValue('knightWins')
                knightTournamentWins = await getServerDictValue('knightTournamentWins')
                druidWins = await getServerDictValue('druidWins')
                druidTournamentWins = await getServerDictValue('druidTournamentWins')
                isTournamentActive = await getServerDictValue('isTournamentActive')
                tournamentName = await getServerDictValue('tournamentName')


                if 'Druid' in str(heroName):
                    clan = '`Druids!`'
                    druidWins = int(druidWins) + 1
                    await setServerDictValue('druidWins', str(druidWins))
                    if isTournamentActive == 'true':
                        druidTournamentWins = int(druidTournamentWins) + 1
                        await setServerDictValue('druidTournamentWins', str(druidTournamentWins))
                        
                if 'Knight' in str(heroName):
                    clan = '`Knights!`'
                    knightWins = await getServerDictValue('knightWins')
                    knightWins = int(knightWins) + 1
                    await setServerDictValue('knightWins', str(knightWins))
                    if isTournamentActive == 'true':
                        knightTournamentWins = int(knightTournamentWins) + 1
                        await setServerDictValue('knightTournamentWins', str(knightTournamentWins))

                wins = await getMemberDictValue(memberId, 'wins')
                updatedWins = str(int(wins) + 1)
                await setMemberDictValue(memberId, 'wins', updatedWins)
                
                embed = discord.Embed(title=f"{memberName} Stands Victorious!", description=f"`{heroName}` is the last remaining Hero\n\nThis is another victory for the {clan}\n\n", color=colorGold)
                embed.add_field(name='Knight Victories', value=knightWins, inline=True)
                embed.add_field(name='Druid Victories', value=druidWins, inline=True)
                embed.add_field(name=f'{memberName} Victories', value=updatedWins, inline=True)
                if isTournamentActive == 'true':
                    embed.add_field(name=f'Knight {tournamentName} Victories', value=knightTournamentWins, inline=True)
                    embed.add_field(name=f'Druid {tournamentName} Victories', value=druidTournamentWins, inline=True)

                embed.set_image(url = heroImage)
                await battleChannel.send(embed=embed)

                await resetServerDict()
                await resetPlayerChoices()
                return
            
            if numberOfRemainingPlayers == 0:
                embed = discord.Embed(title=f"All heroes have perished", description=f"No one survived the previous Round", color=colorBlack)
                embed.set_image(url = 'https://i.postimg.cc/P5f5RgmB/empty-battlefield.jpg')
                await battleChannel.send(embed=embed)
                await resetServerDict()
                await resetPlayerChoices()
                return
            
            await resetPlayerChoices()
            roundNumber = roundNumber + 1

async def getRandomHero():

        walletTypes = ['ethereumWallet', 'polygonWallet']
        randomWalletType = random.choice(walletTypes)
        listOfWallets = []
        listOfMemberIds = []

        f = open("memberAccounts")
        s = f.read()
        membersDict = json.loads(s)

        for account in membersDict:
            if membersDict[account][randomWalletType] == 'false':
                continue
            
            listOfWallets.append(membersDict[account][randomWalletType])
            listOfMemberIds.append(membersDict[account]['discordId'])
            listOfMemberIds.append(membersDict[account]['discordName'])
        
        randomWallet = random.choice(listOfWallets)
        if randomWalletType == 'ethereumWallet':
            walletThings = await getWalletKnights(randomWallet)

        if randomWalletType == 'polygonWallet':
            walletThings = await getWalletDruids(randomWallet)
        
        length = len(walletThings)
        random_number = random.randint(0, length)
        
        memberName = walletThings[random_number]['memberName']
        memberId = listOfMemberIds[random_number]['memberId']
        heroName = walletThings[random_number]['heroName']

        return(memberName, memberId, heroName)


async def getAllParticipantIds():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    participants = serverDict["participantsDict"]

    key_names = []
    for key in participants:
        key_names.append(key)

    return(key_names)


async def resetServerDict():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    serverDict["participantsDict"] = {}

    with open('serverDict', 'w') as f:
        json.dump(serverDict, f, indent=4)

    await setServerDictValue('battleStartUnix', 'false')
    await setServerDictValue('battleMessageId', 'false')
    await setServerDictValue('battleChannelId', 'false')
    await setServerDictValue('battleInSession', 'false')
    await setServerDictValue('battleMode', 'false')
    await setServerDictValue('participantsToStart', 'false')
    await setServerDictValue('battleSet', 'false')
    

async def updateBattleEmbed(interaction):

    numberOfParticipants = await getAllParticipantIds()
    numberOfParticipants = str(len(numberOfParticipants))
    battleStartUnix = await getServerDictValue('battleStartUnix')
    timestamp = await unixToTimestamp(battleStartUnix)
    battleMode = await getServerDictValue('battleMode')
    participantsToStart = await getServerDictValue('participantsToStart')


    if battleMode == 'countdown':
        embed = discord.Embed(title="",description=f"# A battle has started!\n`{interaction.user.name}` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Participants: {numberOfParticipants}`\n`Round 1 Begins: `"+timestamp, color=colorRed)
    
    if battleMode == 'participants':
        embed = discord.Embed(title="",description=f"# A battle has started!\n`{interaction.user.name}` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Participants: {numberOfParticipants}/{participantsToStart}`\n`Round 1 Begins when {participantsToStart}/{participantsToStart} participants have joined`", color=colorRed)
    
    if battleMode == 'staff':
        embed = discord.Embed(title="",description=f"# A battle has started!\n`{interaction.user.name}` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Participants: {numberOfParticipants}`\n`Round 1 Begins when staff runs /battle_start`", color=colorRed)
    
    embed.set_image(url = "https://i.postimg.cc/B6FNRfgk/battlebegins.jpg")

    view = discord.ui.View()
    button = views.theButton(label="Join Battle", custom_id='wd421edc13d', style=discord.ButtonStyle.red)
    view.add_item(button)

    battleChannelId = int(await getServerDictValue('battleChannelId'))
    battleChannel = interaction.client.get_channel(battleChannelId)
    battleMessageId = int(await getServerDictValue('battleMessageId'))
    battleMessage = await battleChannel.fetch_message(battleMessageId)
    await battleMessage.edit(embed = embed, view = view)


async def cancelBattleMessage(bot):
    battleChannelId = int(await getServerDictValue('battleChannelId'))
    battleChannel = bot.get_channel(battleChannelId)
    battleMessageId = int(await getServerDictValue('battleMessageId'))
    battleMessage = await battleChannel.fetch_message(battleMessageId)
    await battleMessage.edit(view = None)


async def isParticipant(interaction):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    try:
        serverDict['participantsDict'][str(interaction.user.id)]
        return(True)
    except:
        return(False)
    

async def hasRolledForAttack(interaction):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    attackRoll = serverDict['participantsDict'][str(interaction.user.id)]['attackRoll']

    if attackRoll == 'false':
        return(False, attackRoll)
    else:
        return(True, attackRoll)
    


async def hasRolledForDefence(interaction):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    defenceRoll = serverDict['participantsDict'][str(interaction.user.id)]['defenceRoll']

    if defenceRoll == 'false':
        return(False, defenceRoll)
    else:
        return(True, defenceRoll)
    

    
async def hasSelectedVictim(interaction):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    victimName = serverDict['participantsDict'][str(interaction.user.id)]['victimName']
    
    if victimName == 'false':
        return(False, victimName)
    else:
        return(True, victimName)


async def resetPlayerChoices():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    participants = serverDict["participantsDict"]

    for participant in participants:
        participants[str(participant)]['attackRoll'] = 'false'
        participants[str(participant)]['defenceRoll'] = 'false'
        participants[str(participant)]['victimName'] = 'false'
        
    with open('serverDict', 'w') as f:
        json.dump(serverDict, f, indent=4)

async def autofillForAbsentPlayers():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    participants = serverDict["participantsDict"]

    for participant in participants:
        
        attackRoll = participants[str(participant)]['attackRoll']
        if attackRoll == 'false':
            random_number = random.randint(0, 100)
            participants[str(participant)]['attackRoll'] = random_number

        defenceRoll = participants[str(participant)]['defenceRoll']
        if defenceRoll == 'false':
            random_number = random.randint(0, 100)
            participants[str(participant)]['defenceRoll'] = random_number

        victimName = participants[str(participant)]['victimName']
        if victimName == 'false':
            playerName = participants[str(participant)]['memberName']
            listOfPlayerNames = await getPlayerNames()
            listOfPlayerNames.remove(playerName)
            randomPlayer = random.choice(listOfPlayerNames)
            participants[str(participant)]['victimName'] = randomPlayer
        
    with open('serverDict', 'w') as f:
        json.dump(serverDict, f, indent=4)
        

async def heroesAttackFunc(channel):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    participants = serverDict["participantsDict"]

    keys = list(participants.keys()) #Shuffling order of participant attacks
    random.shuffle(keys)
    for key in keys:
        health = int(participants[str(key)]['health'])
        if health <= 0:
            continue

        heroName = participants[str(key)]['heroName']
        heroImage = participants[str(key)]['heroImage']
        memberName = participants[str(key)]['memberName']
        attackRoll = participants[str(key)]['attackRoll']
        defenceRoll = participants[str(key)]['defenceRoll']
        victimName = participants[str(key)]['victimName']
        victimId = await getIdFromName(victimName)
        heroAttack = participants[str(key)]['heroAttack']
        weapon1 = participants[str(key)]['weapon1']
        weapon2 = participants[str(key)]['weapon2']
        weapons = []
        if 'None' not in str(weapon1):
            weapons.append(weapon1)
        if 'None' not in str(weapon2):
            weapons.append(weapon2)
        if len(weapons) == 0:
            weapons.append('Fist')
            weapons.append('Foot')
            weapons.append('Helmet')
            weapons.append('Big toe')
        randomWeapon = random.choice(weapons)

        attackPhrases = ['lands a blow on', 'swiftly slices', 'batters', 'executes a flurry of blows on', 'hammers down on', 'slashes', 'sweeps', 'blazes', 'tranquilizes', 'launches an attack on', 'stuns', 'brutalizes', 'concusses', 'impales', 'erupts onto', 'aggressively strikes']
        randomAttackPhrase = random.choice(attackPhrases)

        victimImage = await getParticipantValue(victimId, 'heroImage')
        victimHealth = await getParticipantValue(victimId, 'health')
        victimHeroDefence = await getParticipantValue(victimId, 'heroDefence')
        victimDefenceRoll = await getParticipantValue(victimId, 'defenceRoll')
        victimHeroName = await getParticipantValue(victimId, 'heroName')
        victimWeapon1 = await getParticipantValue(victimId, 'weapon1')
        victimWeapon2 = await getParticipantValue(victimId, 'weapon2')
        victimWeapons = []
        if 'None' not in str(victimWeapon1):
            victimWeapons.append(victimWeapon1)
        if 'None' not in str(victimWeapon2):
            victimWeapons.append(victimWeapon2)
        if len(victimWeapons) == 0:
            victimWeapons.append('Fist')
            victimWeapons.append('Foot')
            victimWeapons.append('Helmet')
            victimWeapons.append('Big toe')
        randomVictimWeapon = random.choice(victimWeapons)

        defencePhrases = ['valiantly', 'swiftly', 'Vigorously', 'Passionately', 'Courageously', 'Firmly', 'Tenaciously', 'Skillfully', 'Instinctively', 'Bravely', 'Decisively', 'Strategically']
        randomDefencePhrase = random.choice(defencePhrases)

        if int(victimHealth) <= 0:
            alreadyDeadEmbed = discord.Embed(title=f"{memberName} attacks {victimName}", description=f"..but {victimName} is already dead..`", color=colorBlack)
            alreadyDeadEmbed.set_thumbnail(url = heroImage)
            await channel.send(embed=alreadyDeadEmbed)
            await asyncio.sleep(7)
            continue
    
        totalAttack = int(attackRoll) + int(heroAttack)
        attackEmbed = discord.Embed(title=f"{memberName} Attacks {victimName}", description=f"`{heroName}` {randomAttackPhrase} `{victimHeroName}` with their `{randomWeapon}`\n\n`Attack Roll: {attackRoll}`\n`{heroName} Attack: {heroAttack}`\n`Total Attack: {str(totalAttack)}`", color=colorRed)
        attackEmbed.set_thumbnail(url = heroImage)
        await channel.send(embed=attackEmbed)
        await asyncio.sleep(7)

        totalDefence = int(victimDefenceRoll) + int(victimHeroDefence)  
        defenceEmbed = discord.Embed(title=f"{victimName} Defends", description=f"`{victimName}` {randomDefencePhrase} defends with their `{randomVictimWeapon}`\n\n`Defence Roll: {victimDefenceRoll}`\n`{victimHeroName} Defence: {victimHeroDefence}`\n`Total Defence: {str(totalDefence)}`", color=colorCyan)
        defenceEmbed.set_thumbnail(url = victimImage)
        await channel.send(embed=defenceEmbed)
        await asyncio.sleep(7)
        
        damageReceived = totalAttack - totalDefence
        if damageReceived < 0:
            damageReceived = 0

        updatedVictimHealth = int(victimHealth) - damageReceived
        if updatedVictimHealth <= 0:
            outcomeWord = 'Perishes'
            outcomeColor = colorBlack
        else:
            outcomeWord = 'Remains'
            outcomeColor = colorGold
            
        outcomeEmbed = discord.Embed(title=f"{victimName} {outcomeWord}", description=f"`{victimHeroName} Post conflict:`\n\n`Total Damage Received: {damageReceived}`\n`Remaining Health: {updatedVictimHealth}`", color=outcomeColor)
        outcomeEmbed.set_thumbnail(url = victimImage)
        await channel.send(embed=outcomeEmbed)
        await asyncio.sleep(7)

        await setParticipantValue(victimId, 'health', str(updatedVictimHealth))

    return
        


async def newParticipant(memberName, memberId, heroName):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    try:
        serverDict['participantsDict'][str(memberId)]
        return(True)
    except:
        heroData = await getHeroData(heroName, memberId)
         
        serverDict['participantsDict'][str(memberId)] = {}
        serverDict['participantsDict'][str(memberId)]['attackRoll'] = 'false'
        serverDict['participantsDict'][str(memberId)]['defenceRoll'] = 'false'
        serverDict['participantsDict'][str(memberId)]['victimName'] = 'false'
        serverDict['participantsDict'][str(memberId)]['health'] = '100'
        serverDict['participantsDict'][str(memberId)]['memberName'] = str(memberName)
        serverDict['participantsDict'][str(memberId)]['memberId'] = str(memberId)
        serverDict['participantsDict'][str(memberId)]['heroName'] = heroName
        serverDict['participantsDict'][str(memberId)]['heroAttack'] = heroData['attack']
        serverDict['participantsDict'][str(memberId)]['heroDefence'] = heroData['defence']
        serverDict['participantsDict'][str(memberId)]['heroImage'] = heroData['image']

        if 'Knight' in heroName:
            serverDict['participantsDict'][str(memberId)]['heroClass'] = 'knight'
            serverDict['participantsDict'][str(memberId)]['weapon1'] = heroData['leftScabbard']
            serverDict['participantsDict'][str(memberId)]['weapon2'] = heroData['rightScabbard']

        if 'Druid' in heroName:
            serverDict['participantsDict'][str(memberId)]['heroClass'] = 'druid'
            serverDict['participantsDict'][str(memberId)]['weapon1'] = heroData['staff']
            serverDict['participantsDict'][str(memberId)]['weapon2'] = heroData['weapon']


        with open('serverDict', 'w') as f:
            json.dump(serverDict, f, indent=4)

        return(False)


async def isParticipant(interaction):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    try:
        serverDict['participantsDict'][str(interaction.user.id)]
        return(True)
    except:
        return(False)

async def setParticipantDictValue(interaction, key, value):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    serverDict['participantsDict'][str(interaction.user.id)][key] = value

    with open('serverDict', 'w') as f:
        json.dump(serverDict, f, indent=4)


async def getHeroData(heroName, memberId):

    ethereumWallet = await getMemberDictValue(memberId, 'ethereumWallet')
    polygonWallet = await getMemberDictValue(memberId, 'polygonWallet')
    
    if 'Knight' in heroName:
        walletKnights = await getWalletKnights(ethereumWallet)
        heroData = next((v for v in walletKnights.values() if v['name'] == heroName), None)
    if 'Druid' in heroName:
        walletDruids = await getWalletDruids(polygonWallet)
        heroData = next((v for v in walletDruids.values() if v['name'] == heroName), None)
    return(heroData)
    


async def getWalletKnights(walletAddress):

    f = open("tokens")
    s = f.read()
    tokensDict = json.loads(s)
    api_key = tokensDict["moralis_api_key"]

    params = {
    "chain": 'eth',
    "format": "decimal",
    "media_items": False,
    "address": walletAddress
    }

    result = evm_api.nft.get_wallet_nfts(
    api_key=api_key,
    params=params,
    )

    contractAddress = '0xD2deFe14811BEC6332C6ae8CcE85a858b3A80B56'

    filtered_entries = [entry for entry in result["result"] if entry["token_address"].lower() == contractAddress.lower()]
    dict = {}
    i = 0
    for entry in filtered_entries:
        # Convert JSON string to dictionary
        metadata = json.loads(filtered_entries[i]['metadata'])
        #print(data)

        attributes = {attr['trait_type']: attr['value'] for attr in metadata['attributes']}
       
        right_scabbard = attributes.get('Right Scabbard', None)
        left_scabbard = attributes.get('Left Scabbard', None)
        attack = attributes.get('Attack', None)
        defence = attributes.get('Defence', None)
        image = metadata['image']
        image = image.rsplit("/", 1)[-1]
        image =  'https://' + image + '.ipfs.nftstorage.link/' #Using 'https://ipfs.io/ipfs/' + image doesnt render in Discord
        name = metadata['name']
        
        dict[i] = {}
        dict[i]['leftScabbard'] = left_scabbard
        dict[i]['rightScabbard'] = right_scabbard
        if attack != None:
            attack = ''.join([char for char in attack if char.isdigit()])
        dict[i]['attack'] = attack
        if defence != None:
            defence = ''.join([char for char in defence if char.isdigit()])
        dict[i]['defence'] = defence
        dict[i]['image'] = image
        dict[i]['name'] = name

        i = i+1

    return(dict)

async def getWalletDruids(walletAddress):

    f = open("tokens")
    s = f.read()
    tokensDict = json.loads(s)
    api_key = tokensDict["moralis_api_key"]

    params = {
    "chain": 'polygon',
    "format": "decimal",
    "media_items": False,
    "address": walletAddress
    }

    result = evm_api.nft.get_wallet_nfts(
    api_key=api_key,
    params=params,
    )

    contractAddress = '0xAe65887F23558699978566664CC7dC0ccd67C0f8'
    filtered_entries = [entry for entry in result["result"] if entry["token_address"].lower() == contractAddress.lower()]
    dict = {}
    i = 0

    for entry in filtered_entries:
        # Convert JSON string to dictionary
        try:
            metadata = json.loads(filtered_entries[i]['metadata']) #Some tokens have metadata: None
        except:
            continue

        attributes = {attr['trait_type']: attr['value'] for attr in metadata['attributes']}
       
        spell = attributes.get('Spell', None)
        staff = attributes.get('Staff', None)
        weapon = attributes.get('Weapons', None)
        attack = attributes.get('Attack', None)
        defence = attributes.get('Defence', None)
        image = metadata['image']
        image = image.rsplit("/", 1)[-1]
        image =  'https://' + image + '.ipfs.nftstorage.link/' #Using 'https://ipfs.io/ipfs/' + image doesnt render in Discord
        name = metadata['name']
        
        dict[i] = {}
        dict[i]['spell'] = spell
        dict[i]['staff'] = staff
        dict[i]['weapon'] = weapon
        if attack != None:
            attack = ''.join([char for char in attack if char.isdigit()])
        dict[i]['attack'] = attack
        if defence != None:
            defence = ''.join([char for char in defence if char.isdigit()])
        dict[i]['defence'] = defence
        dict[i]['image'] = image
        dict[i]['name'] = name

        i = i+1

    return(dict)
        


async def getNumberOfRemainingPlayers():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)
    participants = serverDict["participantsDict"]

    number = 0

    for participant in participants:
        health = participants[str(participant)]['health']
        if int(health) > 0:
            number = number + 1

    return(number)

async def getRemainingPlayer():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)
    participants = serverDict["participantsDict"]

    for participant in participants:
        health = participants[str(participant)]['health']
        if int(health) > 0:
            heroName = participants[str(participant)]['heroName']
            memberName = participants[str(participant)]['memberName']
            memberId = participants[str(participant)]['memberId']
            heroImage = participants[str(participant)]['heroImage']

    return(heroName, memberName, memberId, heroImage)

async def getHeroOptions(memberId):

    ethereumWallet = await getMemberDictValue(memberId, 'ethereumWallet')
    polygonWallet = await getMemberDictValue(memberId, 'polygonWallet')

    options = [[]]
    i = 0
    if polygonWallet != 'false':
        walletDruids = await getWalletDruids(polygonWallet)
        for key, value in walletDruids.items():
            attack = value['attack']
            defence = value['defence']
            options[i].append(discord.SelectOption(label=value['name'], description='Attack: '+attack+' | Defence: '+defence, emoji='⚗️'))
            if len(options[i]) >= 25:
                i += 1
                options.append([])

    if ethereumWallet != 'false':
        walletKnights = await getWalletKnights(ethereumWallet)
        for key, value in walletKnights.items():
            attack = value['attack']
            defence = value['defence']
            options[i].append(discord.SelectOption(label=value['name'], description='Attack: '+attack+' | Defence: '+defence, emoji='⚔️'))
            if len(options[i]) >= 25:
                i += 1
                options.append([])
    return(options)
    

async def getVictimOptions():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    options = []
    participants = serverDict["participantsDict"]

    for participant in participants:
        health = participants[str(participant)]['health']
        if int(health) <= 0:
            continue

        memberName = participants[str(participant)]['memberName']
        heroAttack = participants[str(participant)]['heroAttack']
        heroDefence = participants[str(participant)]['heroDefence']
        heroClass = participants[str(participant)]['heroClass']
        if heroClass == 'druid':
            options.append(discord.SelectOption(label=memberName, description='Attack: '+heroAttack+' | Defence: '+heroDefence, emoji='⚗️'))
        if heroClass == 'knight':
            options.append(discord.SelectOption(label=memberName, description='Attack: '+heroAttack+' | Defence: '+heroDefence, emoji='⚔️'))

    return(options)


async def getIdFromName(memberName):

    
    f = open("memberAccounts")
    s = f.read()
    membersDict = json.loads(s)

    key = 'discordName'

    for account in membersDict:
        if str(memberName) == str(membersDict[account]['discordName']):
             
            value = str(account)
            return(value)

async def getPlayerNames():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    listOfNames = []
    participants = serverDict["participantsDict"]

    for participant in participants:
        memberName = participants[str(participant)]['memberName']
        listOfNames.append(memberName)
 
    return(listOfNames)


async def getWeb3(chain):

    f = open("tokens")
    s = f.read()
    tokensDict = json.loads(s)
    private_key = tokensDict["private_key"]

    account_from = {
    'private_key': private_key,
    'address': '0x63C18042Ff056493c62bc74d04A32F03a5813798',
    }

    #https://polygon-mainnet.infura.io/v3/a31017990a434050ab5b5dad42ba299a
    #https://polygon-mumbai.infura.io/v3/a31017990a434050ab5b5dad42ba299a
    if chain == 'polygon':
        provider_url = 'https://polygon-mainnet.infura.io/v3/a31017990a434050ab5b5dad42ba299a'
    if chain == 'ethereum':
        provider_url = 'https://mainnet.infura.io/v3/a31017990a434050ab5b5dad42ba299a'

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0) 
    return(web3)


async def getOpenProjBot():

    #This is like API Requests

    #Mellow: 
    # Well you could always opt to use the lower http client level at least then. Because then you wouldn't need to connect to the gateway
    # Not .start You do not want to connect to the gateway

    #using .login with await allows bot to perform requests in d.py fashion, which avoids the terminal being consumed by bot
    #importing the bot relaunches it in terminal

    #SolsticeShard:
    #If you really want to login to the gateway every single time you want to do this, the important thing to note is that none of your bot's caches will be filled. No get_x's work. You have to fetch everything
    #The creation and maintenance of the bot's cache happens by the bot being actively connected to the gateway and receiving events

    #await OpenProjBot.close() #Must close connection after using else Unclosed client session error

    # "The problem is that fetch_guild doesn’t return the channels/members/categories, use get_guild instead"
    # To get channels from guild using the API client we must do below, as we've done in generateServerInvite:
    # guild = await OpenProjBot.fetch_guild(int(guildId))
    # channels = await guild.fetch_channels()

    f = open("tokens")
    s = f.read()
    tokensDict = json.loads(s)
    OpenProjBotToken = tokensDict["OpenProjBotToken"]

    OpenProjBot = discord.Client(intents=discord.Intents.all())
    await OpenProjBot.login(str(OpenProjBotToken)) #BE WARY IF TESTING WITH OPENPROJBOTTEST, THEYRE IN DIFFERENT SERVERS AND HAVE DIFFERENT SERVERACCOUNTS SO CANT ACCESS GUILD FOR EXAMPLE
    return(OpenProjBot)
   




async def generateGameLeaderboard(guild, title, interaction):

            await interaction.response.defer()              
            #guildId = int(interaction.message.embeds[0].footer.text)
            guildId = guild.id
            guild = interaction.client.get_guild(guildId)
            topParticipantsList = await extract_and_sort_tokens(guild.name, guild.name+'TokensEarnedThis'+title+'Contest')
            # Initialize an empty string to store the result
            result_string = ""
            # Iterate through the list
            for index, (tokens, name, percentage) in enumerate(topParticipantsList, start=1):
                # Add position, name, and tokens to the result string
                if str(guildId) == '1131699351496962069': #OpenProj server Ids
                    result_string += f"`{index}` - {name} - `{tokens}` :coin: - " + str(percentage) +"% chance of winning\n"
                else:
                    result_string += f"`{index}` - {name} - `{tokens}` :coin:\n"

            embed1 = discord.Embed(title="Welcome to the " + title + " Leaderboard", description = "Here you can see how you compare to the other Participants in this task", color=openProjCyan)
            embed1.set_thumbnail(url = "https://i.postimg.cc/QxcWv8XY/trophy-1f3c6.png")

            embed2 = discord.Embed(title=':trophy: Top Participants', description = 'This leaderboard displays Participants based on their Tokens Earned this '+title+' task\n\n'+result_string, color=openProjCyan)
            embedList = [embed1, embed2]
            await interaction.followup.send(embeds=embedList, ephemeral=True)


async def generateGamesMenu(interaction):
            
            imageEmbed = discord.Embed(title='', color=openProjCyan)
            imageEmbed.set_image(url = 'https://i.postimg.cc/k4bfb4vJ/Games.jpg')
            embed = discord.Embed(title='OpenProj Games', description = '`Select a game below to start`', color=openProjCyan)

            embedsList = [imageEmbed, embed]
            options = await getGamesOptions()
            view = discord.ui.View()
            select = views.memberGameSelect(options)
            view.add_item(select)

            await interaction.followup.send(embeds=embedsList, view = view, ephemeral = True, wait=True)



async def getGamesOptions():

    options = [ # the list of options from which users can choose, a required field
             discord.SelectOption(
                label="Among Us",
                description="Imposters vs Crewmates"
            ),
             discord.SelectOption(
                label="Who's Most Likely (Bad Edition)",
                description="Participants vote who's most likely"
            ),
             discord.SelectOption(
                label="Russian Roulette",
                description="Each participant must shoot themself, first to die loses"
            ),
            discord.SelectOption(
                label="invaders",
                description="Invaders Web Game"
            ),
            discord.SelectOption(
                label="slicer",
                description="Slicer Web Game"
            ),
            discord.SelectOption(
                label="jumper",
                description="Jumper Web Game"
            ),
            discord.SelectOption(
                label="catcher",
                description="Catcher Web Game"
            ),
        ]

    return(options)




async def getNowUnix():
        now = datetime.datetime.now()
        nowUnix = int(round(now.timestamp()))
        return(nowUnix)

async def unixToTimestamp(unix):
        timestamp = '<t:'+str(unix)+':R>'
        return(timestamp)

async def isStaff(memberId):
    
    staffList = await getServerDictValue('staff')
    if str(memberId) in staffList or str(memberId) == '903781746611462214' or str(memberId) == '433648637763911680' or str(memberId) == '960601733556482108':
       return('true', 'true')
    else:
        embed = discord.Embed(title="",description=f"Only staff members can use that command", color=colorBlack)
        return('false', embed)



async def setServerDictValue(key, value, nestedKey = 'False'):
    
    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    if nestedKey == 'False':
        serverDict[key] = value
    else:
        serverDict[key][nestedKey] = value
        
    with open('serverDict', 'w') as f:
        json.dump(serverDict, f, indent=4)


async def getServerDictValue(key, nestedKey = 'False'):
    
    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    if nestedKey == 'False':
        value = serverDict[key]
    else:
        value = serverDict[key][nestedKey]
    return(value)


        
async def setMemberDictValue(memberId, key, value, nestedKey = 'False'):
    
    f = open("memberAccounts")
    s = f.read()
    membersDict = json.loads(s)

    if nestedKey == 'False':
        membersDict[str(memberId)][key] = value
    else:
        membersDict[str(memberId)][key][nestedKey] = value
        
    with open('memberAccounts', 'w') as f:
            json.dump(membersDict, f, indent=4)


async def getMemberDictValue(memberId, key, nestedKey = 'False'):
    
    f = open("memberAccounts")
    s = f.read()
    membersDict = json.loads(s)
    
    if key not in membersDict[str(memberId)].keys():
        return('Not There') #cause shares are only created when member earns shares
        
    if nestedKey == 'False':
        value = membersDict[str(memberId)][key]
    else:
        value = membersDict[str(memberId)][key][nestedKey]
    return(value)



async def getParticipantValue(memberId, key):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)
  
    value = serverDict['participantsDict'][str(memberId)][key]
    return(value)


async def setParticipantValue(memberId, key, value):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)
  
    serverDict['participantsDict'][str(memberId)][key] = value

    with open('serverDict', 'w') as f:
        json.dump(serverDict, f, indent=4)


#Create new member account - takes message
async def newMemberFunc(memberId, memberName):

    f = open("memberAccounts")
    s = f.read()
    membersDict = json.loads(s)

    try:
        membersDict[str(memberId)]
        return
    except:
        membersDict[str(memberId)] = {}
        membersDict[str(memberId)]['discordName'] = str(memberName)
        membersDict[str(memberId)]['discordId'] = str(memberId)
        membersDict[str(memberId)]['wins'] = '0'
        membersDict[str(memberId)]['losses'] = '0'
        membersDict[str(memberId)]['polygonWallet'] = 'false'
        membersDict[str(memberId)]['ethereumWallet'] = 'false'
        membersDict[str(memberId)]['heroOptionsPosition'] = '0'

        with open('memberAccounts', 'w') as f:
            json.dump(membersDict, f, indent=4)
        