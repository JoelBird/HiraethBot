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



async def getAllParticipantIds():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    participants = serverDict["participantsDict"]

    key_names = []
    for key in participants:
        key_names.append(key)

    return(key_names)


async def resetParticipantsDict():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    serverDict["participantsDict"] = {}

    with open('serverDict', 'w') as f:
        json.dump(serverDict, f, indent=4)

    

async def updateBattleEmbed(interaction):

    numberOfParticipants = await getServerDictValue('numberOfParticipants')
    battleStartUnix = await getServerDictValue('battleStartUnix')
    timestamp = await unixToTimestamp(battleStartUnix)
    
    embed = discord.Embed(title="",description=f"# A battle has started!\n`{interaction.user.name }` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\nParticipants: {numberOfParticipants}\nRound 1 Begins: "+timestamp, color=colorRed)
    embed.set_image(url = "https://i.postimg.cc/B6FNRfgk/battlebegins.jpg")
    view = discord.ui.View()
    button = views.theButton(label="Join Battle", custom_id='wd421edc13d', style=discord.ButtonStyle.red)
    view.add_item(button)

    battleMessageId = await getServerDictValue('battleMessageId')
    await interaction.followup.edit_message(message_id = battleMessageId, embed = embed, view = view)

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
    

    
async def hasSelectedVictim(interaction):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    victimName = serverDict['participantsDict'][str(interaction.user.id)]['victimName']
    
    if victimName == 'false':
        return(False, victimName)
    else:
        return(True, victimName)

    
async def increaseNumberOfParticipants():
    numberOfParticipants = await getServerDictValue('numberOfParticipants')
    newNumberOfParticipants = int(numberOfParticipants) + 1
    await setServerDictValue('numberOfParticipants', str(newNumberOfParticipants))



async def resetPlayerChoices():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    participants = serverDict["participantsDict"]

    for participant in participants:
        participants[str(participant)]['attackRoll'] = 'false'
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
            random_number = random.randint(0, 20)
            participants[str(participant)]['attackRoll'] = random_number

        victimName = participants[str(participant)]['victimName']
        if victimName == 'false':
            playerName = participants[str(participant)]['memberName']
            listOfPlayerNames = await getPlayerNames()
            listOfPlayerNames.remove(playerName)
            randomPlayer = random.choice(listOfPlayerNames)
            participants[str(participant)]['victimName'] = randomPlayer
        
    with open('serverDict', 'w') as f:
        json.dump(serverDict, f, indent=4)
        

async def heroesAttackFunc(interaction):

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
        victimName = participants[str(key)]['victimName']
        victimId = await getIdFromName(victimName)
        heroAttack = participants[str(key)]['heroAttack']
        weapon1 = participants[str(key)]['weapon1']
        weapon2 = participants[str(key)]['weapon2']
        weapons = []
        if weapon1 != 'None':
            weapons.append(weapon1)
        if weapon2 != 'None':
            weapons.append(weapon2)
        if len(weapons) == 0:
            weapons.append('Fist')
            weapons.append('Foot')
            weapons.append('Helmet')
            weapons.append('Big toe')
        randomWeapon = random.choice(weapons)

        attackPhrases = ['lands a blow on', 'swiftly slices', 'batters', 'executes a flurry of blows on', 'hammers down on', 'slashes', 'sweeps', 'blazes', 'tranquilizes', 'launches an attack on', 'stuns', 'brutalizes', 'concusses', 'impales', 'erupts onto', 'agressively strikes']
        randomAttackPhrase = random.choice(attackPhrases)

        victimImage = await getParticipantValue(victimId, 'heroImage')
        victimHealth = await getParticipantValue(victimId, 'health')
        victimHeroDefence = await getParticipantValue(victimId, 'heroDefence')
        victimHeroName = await getParticipantValue(victimId, 'heroName')
        victimWeapon1 = await getParticipantValue(victimId, 'weapon1')
        victimWeapon2 = await getParticipantValue(victimId, 'weapon2')
        victimWeapons = []
        if victimWeapon1 != None:
            victimWeapons.append(victimWeapon1)
        if victimWeapon2 != None:
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
            await interaction.followup.send(embed=alreadyDeadEmbed, ephemeral = False)
            await asyncio.sleep(7)
            continue
    
        totalAttack = int(attackRoll) + int(heroAttack)
        attackEmbed = discord.Embed(title=f"{memberName} Attacks {victimName}", description=f"`{heroName}` {randomAttackPhrase} `{victimHeroName}` with their `{randomWeapon}`\n\n`Attack Roll: {attackRoll}`\n`{heroName} Attack: {heroAttack}`\n`Total Attack Damage: {str(totalAttack)}`", color=colorRed)
        attackEmbed.set_thumbnail(url = heroImage)
        await interaction.followup.send(embed=attackEmbed, ephemeral = False)
        await asyncio.sleep(7)
                
        defenceEmbed = discord.Embed(title=f"{victimName} Defends", description=f"`{victimName}` {randomDefencePhrase} defends with their `{randomVictimWeapon}`\n\n`{victimHeroName} Defence: {victimHeroDefence}`\n`Total Defence: {str(victimHeroDefence)}`", color=colorCyan)
        defenceEmbed.set_thumbnail(url = victimImage)
        await interaction.followup.send(embed=defenceEmbed, ephemeral = False)
        await asyncio.sleep(7)
        
        damageReceived = totalAttack - int(victimHeroDefence)
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
        await interaction.followup.send(embed=outcomeEmbed, ephemeral = False)
        await asyncio.sleep(7)

        await setParticipantValue(victimId, 'health', str(updatedVictimHealth))

    return
        

        


async def newParticipant(interaction, heroName):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    try:
        serverDict['participantsDict'][str(interaction.user.id)]
        return(True)
    except:
        heroData = await getHeroData(heroName, interaction.user.id)
         
        serverDict['participantsDict'][str(interaction.user.id)] = {}
        serverDict['participantsDict'][str(interaction.user.id)]['attackRoll'] = 'false'
        serverDict['participantsDict'][str(interaction.user.id)]['victimName'] = 'false'
        serverDict['participantsDict'][str(interaction.user.id)]['health'] = '100'
        serverDict['participantsDict'][str(interaction.user.id)]['memberName'] = str(interaction.user.name)
        serverDict['participantsDict'][str(interaction.user.id)]['memberId'] = str(interaction.user.id)
        serverDict['participantsDict'][str(interaction.user.id)]['heroName'] = heroName
        serverDict['participantsDict'][str(interaction.user.id)]['heroAttack'] = heroData['attack']
        serverDict['participantsDict'][str(interaction.user.id)]['heroDefence'] = heroData['defence']
        serverDict['participantsDict'][str(interaction.user.id)]['heroImage'] = heroData['image']

        if 'Knight' in heroName:
            serverDict['participantsDict'][str(interaction.user.id)]['heroClass'] = 'knight'
            serverDict['participantsDict'][str(interaction.user.id)]['weapon1'] = heroData['leftScabbard']
            serverDict['participantsDict'][str(interaction.user.id)]['weapon2'] = heroData['rightScabbard']

        if 'Druid' in heroName:
            serverDict['participantsDict'][str(interaction.user.id)]['heroClass'] = 'druid'
            serverDict['participantsDict'][str(interaction.user.id)]['weapon1'] = heroData['staff']
            serverDict['participantsDict'][str(interaction.user.id)]['weapon2'] = heroData['weapon']


        with open('serverDict', 'w') as f:
            json.dump(serverDict, f, indent=4)

        return(False)


async def setParticipantDictValue(interaction, heroName):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    try:
        serverDict['participantsDict'][str(interaction.user.id)]
        return
    except:
        heroData = await getHeroData(heroName, interaction.user.id)
         
        serverDict['participantsDict'][str(interaction.user.id)] = {}
        serverDict['participantsDict'][str(interaction.user.id)]['attackRoll'] = 'false'
        serverDict['participantsDict'][str(interaction.user.id)]['victimName'] = 'false'
        serverDict['participantsDict'][str(interaction.user.id)]['health'] = '100'
        serverDict['participantsDict'][str(interaction.user.id)]['memberName'] = str(interaction.user.name)
        serverDict['participantsDict'][str(interaction.user.id)]['heroName'] = heroName
        serverDict['participantsDict'][str(interaction.user.id)]['heroAttack'] = heroData['attack']
        serverDict['participantsDict'][str(interaction.user.id)]['heroDefence'] = heroData['defence']

        if 'Knight' in heroName:
            serverDict['participantsDict'][str(interaction.user.id)]['weapon1'] = heroData['leftScabbard']
            serverDict['participantsDict'][str(interaction.user.id)]['weapon2'] = heroData['rightScabbard']

        if 'Druid' in heroName:
            serverDict['participantsDict'][str(interaction.user.id)]['weapon1'] = heroData['staff']
            serverDict['participantsDict'][str(interaction.user.id)]['weapon2'] = heroData['weapon']


        with open('serverDict', 'w') as f:
            json.dump(serverDict, f, indent=4)


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
        image =  'https://ipfs.io/ipfs/' + image
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
        image =  'https://ipfs.io/ipfs/' + image
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


async def getContestParticipants(guild):

    role_name = "Participant"
    participants = []
    participantRole = discord.utils.get(guild.roles, name="Participant")

    for member in participantRole.members:
        participants.append(member.name)

    random.shuffle(participants)

    return(participants)

    


async def getNumberOfContestParticipants(guild):

    numberOfParticipants = str(len(await getContestParticipants(guild)))
    return(numberOfParticipants)


async def getNowUnix():
        now = datetime.datetime.now()
        nowUnix = int(round(now.timestamp()))
        return(nowUnix)

async def unixToTimestamp(unix):
        timestamp = '<t:'+str(unix)+':R>'
        return(timestamp)


async def wipeRumbleRoyaleDictionary(guildId):
    
    f = open("serverAccounts.txt")
    s = f.read()
    serversDict = json.loads(s)

    for account in serversDict:
        if str(guildId) == str(serversDict[account]['serverId']):
            serversDict[str(account)]['rumbleRoyale']['participants'] = []
            serversDict[str(account)]['rumbleRoyale']['votes'] = []
            serversDict[str(account)]['rumbleRoyale']['hasVoted'] = []
            serversDict[str(account)]['rumbleRoyale']['majorityVote'] = 'False'
            serversDict[str(account)]['rumbleRoyale']['hasEnded'] = 'True'

        

    with open('serverAccounts.txt', 'w') as f:
        json.dump(serversDict, f, indent=4)



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
        membersDict[str(memberId)]['wins'] = '0'
        membersDict[str(memberId)]['losses'] = '0'
        membersDict[str(memberId)]['polygonWallet'] = 'false'
        membersDict[str(memberId)]['ethereumWallet'] = 'false'
        membersDict[str(memberId)]['heroOptionsPosition'] = '0'

        with open('memberAccounts', 'w') as f:
            json.dump(membersDict, f, indent=4)
        