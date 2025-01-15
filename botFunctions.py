import aiohttp
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
import random
import pyshorteners
import re
from moralis import evm_api

colorCyan = discord.Colour.from_str('#00ffcd')
colorRed = discord.Colour.from_str('#FF272A')
colorOrange = discord.Colour.from_str('#FF7A59')
colorGreen = discord.Colour.from_str('#7DB980')
colorBlack = discord.Colour.from_str('#0e1522')
colorWhite = discord.Colour.from_str('#FFFFFF')
colorPink = discord.Colour.from_str('#ffc0d6')
colorGold = discord.Colour.from_str('#FDD835')


async def get_defeated_heroes():
    try:
        # Load the JSON file
        with open("serverDict", 'r') as file:
            server_dict = json.load(file)

        # Get the participants dictionary
        participants = server_dict.get("participantsDict", {})
        defeated_heroes = []

        # Iterate through each participant
        for participant_id, participant_data in participants.items():
            health = int(participant_data.get("health", 0))  # Convert health to integer
            if health <= 0:  # Check if health is 0 or less
                hero_name = participant_data.get("heroName")
                if hero_name:  # Ensure heroName exists
                    defeated_heroes.append(hero_name)

        return defeated_heroes

    except Exception as e:
        print(f"Error occurred: {e}")
        return []



# In-memory dictionary to keep track of hero options positions for each user
hero_options_positions = {}

# Function to update the hero options position for a user
async def update_hero_options_position(user_id, updatedHeroOptionsPosition):
    hero_options_positions[user_id] = updatedHeroOptionsPosition


# Function to get the hero options position for a user
async def get_hero_options_position(user_id):
    return hero_options_positions.get(user_id)



async def startBattle(bot):

    await cancelBattleMessage(bot)

    battleChannelId = int(await getServerDictValue('battleChannelId'))
    battleChannel = bot.get_channel(battleChannelId)
    
    view = discord.ui.View()
    # button = views.theButton(label="Roll For Attack", custom_id='awdg423d', style=discord.ButtonStyle.red)
    # view.add_item(button)

    # button = views.theButton(label="Roll For Defence", custom_id='awdwad1312', style=discord.ButtonStyle.blurple)
    # view.add_item(button)

    options = await getVictimOptions()
    select = views.victimSelect(options=options)
    view.add_item(select)

    button = views.theButton(label="Use A Spell", custom_id='d31f42gd132ww', style=discord.ButtonStyle.blurple)
    view.add_item(button)

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
        end = nowUnix + 20
        timestamp = await unixToTimestamp(end)

        phrases = ["🪨 Let's Rock!", "🔥 It's getting heated! 🔥", "👊 Fight!", "💯 This is Heroes Of Hiraeth!", "😏 Who wants $HGLD?", "🪖 HOO-HAA!!", "🏆 Winner takes all!", "⏰ Time to fight!"]
        randomPhrase = random.choice(phrases)

        embed = discord.Embed(title="", description=f"`Time left:` {timestamp}\n# {randomPhrase}", color=colorRed)
        if randomPhrase == "💯 This is Heroes Of Hiraeth!":
            embed.set_thumbnail(url = "https://em-content.zobj.net/source/joypixels-animations/366/hundred-points_1f4af.gif")
        elif randomPhrase == "👊 Fight!":
            embed.set_thumbnail(url = "https://em-content.zobj.net/source/joypixels-animations/366/oncoming-fist_1f44a.gif")
        elif randomPhrase == "😏 Who wants $HGLD?":
            embed.set_thumbnail(url = "https://em-content.zobj.net/source/joypixels-animations/366/smirking-face_1f60f.gif")
        elif randomPhrase == "⏰ Time to fight!":
            embed.set_thumbnail(url = "https://em-content.zobj.net/source/joypixels-animations/366/alarm-clock_23f0.gif")
        elif randomPhrase == "🪖 HOO-HAA!!":
            embed.set_thumbnail(url = "https://em-content.zobj.net/source/joypixels-animations/366/pistol_1f52b.gif")
        elif randomPhrase == "🪨 Let's Rock!":
            embed.set_thumbnail(url = "https://em-content.zobj.net/source/joypixels-animations/366/bomb_1f4a3.gif")
        elif randomPhrase == "🏆 Winner takes all!":
            embed.set_thumbnail(url = "https://em-content.zobj.net/source/joypixels-animations/366/crown_1f451.gif")
        else:
            embed.set_thumbnail(url = "https://em-content.zobj.net/source/joypixels-animations/366/fire_1f525.gif")

        if roundNumber == 1:
            embed.set_image(url = "https://i.postimg.cc/Dfc89xWj/round1.png")
        elif roundNumber == 2:
            embed.set_image(url = "https://i.postimg.cc/BZNnYtyR/round2.png")
        elif roundNumber == 3:
            embed.set_image(url = "https://i.postimg.cc/fbqn3w7F/round3.png")
        elif roundNumber == 4:
            embed.set_image(url = "https://i.postimg.cc/MKJkf3RW/round4.png")
        elif roundNumber == 5:
            embed.set_image(url = "https://i.postimg.cc/W1SxK2y3/round5.png")
        elif roundNumber == 6:
            embed.set_image(url = "https://i.postimg.cc/j5n9LySw/round6.png")
        elif roundNumber == 7:
            embed.set_image(url = "https://i.postimg.cc/g0TQzgmb/round7.png")
        elif roundNumber == 8:
            embed.set_image(url = "https://i.postimg.cc/tJhMzyP9/round8.png")
        elif roundNumber == 9:
            embed.set_image(url = "https://i.postimg.cc/8kW9GdYx/round9.png")
        elif roundNumber == 10:
            embed.set_image(url = "https://i.postimg.cc/3RGSK7t2/round10.png")
        else:
            embed.set_image(url = "https://i.postimg.cc/gjPMj57Q/roundxxx.png")
        await battleChannel.send(embed=embed, view = view)

        await asyncio.sleep(20)

        await autofillForAbsentPlayers()

        await heroesAttackFunc(battleChannel)
        
        embed = discord.Embed(title="",description=f"# Round {roundNumber} Outcome", color=colorGold)
        participantIds = await getAllParticipantIds()
        for id in participantIds:
            memberName = await getParticipantValue(id, 'memberName')
            heroName = await getParticipantValue(id, 'heroName')
            heroClass = await getParticipantValue(id, 'heroClass')
            health = await getParticipantValue(id, 'health')
            if int(health) <= 0:
                embed.add_field(name=f"💀 {memberName}", value=f"Health: {health}", inline=True)
            if int(health) > 0:
                embed.add_field(name=f"❤️ {memberName}", value=f"Health: {health}", inline=True)     

        imageLinks = ["https://i.postimg.cc/YSQDDzLf/vs-1.png", "https://i.postimg.cc/W1vx45KQ/vs-2.png", "https://i.postimg.cc/VkCK5WgQ/vs-3.png"]   
        imageLink = random.choice(imageLinks)
        embed.set_image(url = imageLink)
        await battleChannel.send(embed=embed)

        await asyncio.sleep(10)


        numberOfRemainingPlayers = int(await getNumberOfRemainingPlayers())

        if numberOfRemainingPlayers == 1:
            heroName, heroClass, memberName, memberId, heroImage = await getRemainingPlayer()

        if numberOfRemainingPlayers == 0:
            heroName, memberName, memberId, heroImage, health = await getPlayerWithMostHealth()

        if numberOfRemainingPlayers == 1 or numberOfRemainingPlayers == 0:
            knightWins = await getServerDictValue('knightWins')
            knightTournamentWins = await getServerDictValue('knightTournamentWins')
            druidWins = await getServerDictValue('druidWins')
            druidTournamentWins = await getServerDictValue('druidTournamentWins')
            isTournamentActive = await getServerDictValue('isTournamentActive')
            tournamentName = await getServerDictValue('tournamentName')


            if 'druid' in str(heroClass):
                clan = '`Druids!`'
                druidWins = int(druidWins) + 1
                await setServerDictValue('druidWins', str(druidWins))
                if isTournamentActive == 'true':
                    druidTournamentWins = int(druidTournamentWins) + 1
                    await setServerDictValue('druidTournamentWins', str(druidTournamentWins))
                    
            if 'knight' in str(heroClass):
                clan = '`Knights!`'
                knightWins = await getServerDictValue('knightWins')
                knightWins = int(knightWins) + 1
                await setServerDictValue('knightWins', str(knightWins))
                if isTournamentActive == 'true':
                    knightTournamentWins = int(knightTournamentWins) + 1
                    await setServerDictValue('knightTournamentWins', str(knightTournamentWins))

            wins = await getMemberValue(memberId, 'wins')
            updatedWins = str(int(wins) + 1)
            await updateMemberValue(memberId, 'wins', updatedWins)

            embedLoading = discord.Embed(title="Processing Transaction..", description="", color=colorCyan)
            embedLoading.set_thumbnail(url="https://i.postimg.cc/ry0MnB9v/loading-gif.gif")   
            loadingMessage = await battleChannel.send(embed=embedLoading)

            wallets = await getMemberValue(memberId, 'wallets')
            walletAddress = wallets[0]
            winnerHgld = await calculateWinnerHgld()
            signature = await sendHgld(walletAddress, winnerHgld)

            if numberOfRemainingPlayers == 1:
                embed = discord.Embed(title=f"{memberName} is our Champion!", description=f"`{heroName}` is the last remaining Hero and has been sent **{winnerHgld} $HGLD!**\n\n`Transaction Signature: {signature}`\n\nThis is another victory for the **{clan}**\n\n", color=colorGold)

            if numberOfRemainingPlayers == 0:
                embed = discord.Embed(title=f"{memberName} is our Champion!", description=f"`{heroName}` is the Hero with the most remaining health after everyone has perished and has been sent **{winnerHgld} $HGLD!**\n\n`Transaction Signature: {signature}`\n\nThis is another victory for the **{clan}**\n\n", color=colorGold)
            
            embed.add_field(name='Knight Victories', value=knightWins, inline=True)
            embed.add_field(name='Druid Victories', value=druidWins, inline=True)
            embed.add_field(name=f'{memberName} Victories', value=updatedWins, inline=True)
            if isTournamentActive == 'true':
                embed.add_field(name=f'Knight {tournamentName} Victories', value=knightTournamentWins, inline=True)
                embed.add_field(name=f'Druid {tournamentName} Victories', value=druidTournamentWins, inline=True)

            embed.set_image(url = heroImage)
            embed.set_thumbnail(url="https://em-content.zobj.net/source/microsoft/379/trophy_1f3c6.png")       
            await battleChannel.send(embed=embed)
            await loadingMessage.delete()

            defeated_heroes = await get_defeated_heroes()
            endpoint = f"https://www.heroesnft.app:3002/api/update-defeated-heroes"

            payload = {"defeatedHeroes": defeated_heroes}
            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                print(response.json())
            except requests.exceptions.RequestException as e:
                print({"error": str(e)})

            await resetServerDict()
            await resetPlayerChoices()
            return
        
        
        await resetPlayerChoices()
        roundNumber = roundNumber + 1



async def getRandomHero(userId):

    heroTypes = ['druid', 'knight']
    randomHeroClass = random.choice(heroTypes)

    numberOfNfts = 0
    while numberOfNfts < 1:
        
        randomMember = await getRandomMember()
        if randomMember['discordId'] == str(userId):
            continue

        if randomHeroClass == 'knight':
            walletItems = await getWalletKnights(randomMember['wallets'][0])

        if randomHeroClass == 'druid':
            walletItems = await getWalletDruids(randomMember['wallets'][0])

        numberOfNfts = len(walletItems) #Prevent selecting wallet with 0 druids/knights

    length = len(walletItems) - 1
    random_number = random.randint(0, length)
    heroName = walletItems[random_number]['name']

    return(randomMember['discordName'], randomMember['discordId'], heroName, randomHeroClass)



async def getRandomMember():
    url = 'https://www.heroesnft.app:3002/api/member/random'  # Endpoint for getting a random member

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Raises an HTTPError for unsuccessful status codes
                
                # Parse JSON response
                data = await response.json()
                print(f"Random Member: {data}")
                return data

    except aiohttp.ClientResponseError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


async def getAllParticipantIds():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    participants = serverDict["participantsDict"]

    key_names = []
    for key in participants:
        key_names.append(key)

    return(key_names)


async def calculateWinnerHgld():
    numberOfParticipants = len(await getAllParticipantIds())
    winnerHgld = numberOfParticipants * 100
    return(winnerHgld)


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
    await setServerDictValue('ghostBattleStarterId', 'false')
    await setServerDictValue('1v1BattleStarterId', 'false')
    await setServerDictValue('1v1BattleVictimId', 'false')
    

async def updateBattleEmbed(interaction):

    numberOfParticipants = await getAllParticipantIds()
    numberOfParticipants = str(len(numberOfParticipants))
    battleStartUnix = await getServerDictValue('battleStartUnix')
    timestamp = await unixToTimestamp(battleStartUnix)
    battleMode = await getServerDictValue('battleMode')
    participantsToStart = await getServerDictValue('participantsToStart')

    battleChannelId = int(await getServerDictValue('battleChannelId'))
    battleChannel = interaction.client.get_channel(battleChannelId)
    battleMessageId = int(await getServerDictValue('battleMessageId'))
    battleMessage = await battleChannel.fetch_message(battleMessageId)
    battleMessageAuthor = str(battleMessage.author.name)


    if battleMode == 'countdown':
        embed = discord.Embed(title="",description=f"# A battle has started!\n`{battleMessageAuthor}` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Participants: {numberOfParticipants}`\n`Round 1 Begins: `"+timestamp, color=colorRed)
    
    if battleMode == 'participants':
        embed = discord.Embed(title="",description=f"# A battle has started!\n`{battleMessageAuthor}` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Participants: {numberOfParticipants}/{participantsToStart}`\n`Round 1 Begins when {participantsToStart}/{participantsToStart} participants have joined`", color=colorRed)
    
    if battleMode == 'staff':
        embed = discord.Embed(title="",description=f"# A battle has started!\n`{battleMessageAuthor}` has started a battle\n## Rules:\nAt the start of every Round, each player is required to:\n\n⚔️ **Roll a dice for Attack**\n🛡️ **Roll a dice for Defence**\n💀 **Select a Hero to Attack**\n\nThe bot will announce the outcome of every Hero's actions during the round\n\n🏆 **The last Hero remaining is Victorious!**\n\n`Participants: {numberOfParticipants}`\n`Round 1 Begins when staff runs /battle_start`", color=colorRed)
    
    await battleMessage.edit(embed = embed, view = views.joinBattle())


async def cancelBattleMessage(bot):
    battleChannelId = int(await getServerDictValue('battleChannelId'))
    battleChannel = bot.get_channel(battleChannelId)
    battleMessageId = int(await getServerDictValue('battleMessageId'))
    battleMessage = await battleChannel.fetch_message(battleMessageId)
    await battleMessage.edit(view = None)



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
            random_number = random.randint(0, 50)
            participants[str(participant)]['defenceRoll'] = random_number

        victimName = participants[str(participant)]['victimName']
        if victimName == 'false':
            playerName = participants[str(participant)]['memberName']
            listOfAlivePlayerNames = await getAlivePlayerNames()
            if playerName in listOfAlivePlayerNames:
                listOfAlivePlayerNames.remove(playerName)

            randomPlayer = random.choice(listOfAlivePlayerNames)
            participants[str(participant)]['victimName'] = randomPlayer
        
    with open('serverDict', 'w') as f:
        json.dump(serverDict, f, indent=4)



async def getAlivePlayerNames():

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    listOfNames = []
    participants = serverDict["participantsDict"]

    for participant in participants:
        memberName = participants[str(participant)]['memberName']
        memberHealth = participants[str(participant)]['health']
        if int(memberHealth) > 0:
            listOfNames.append(memberName)
 
    return(listOfNames)
        

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
        memberId = participants[str(key)]['memberId']
        spellName = participants[str(key)]['spellName']
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
            victimWeapons.append('Fist')
            victimWeapons.append('Foot')
            victimWeapons.append('Helmet')
            victimWeapons.append('Big toe')
            victimWeapons.append('UK size 10 shoe')
            victimWeapons.append('Pocket watch')
            victimWeapons.append('Open palm')
            victimWeapons.append('Nails')
        randomWeapon = random.choice(weapons)

        attackPhrases = ['lands a blow on', 'swiftly slices', 'batters', 'executes a flurry of blows on', 'hammers down on', 'slashes', 'sweeps', 'blazes', 'tranquilizes', 'launches an attack on', 'stuns', 'brutalizes', 'concusses', 'impales', 'erupts onto', 'aggressively strikes', 'Staggers', 'mauls', 'tenaciously sweeps', 'wrathfully bashes', 'forefully strikes']
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
            victimWeapons.append('UK size 8 shoe')
            victimWeapons.append('Pocket watch')
            victimWeapons.append('Open palm')
            victimWeapons.append('Nails')
        randomVictimWeapon = random.choice(victimWeapons)

        defencePhrases = ['valiantly', 'swiftly', 'Vigorously', 'Passionately', 'Courageously', 'Firmly', 'Tenaciously', 'Skillfully', 'Instinctively', 'Bravely', 'Decisively', 'Strategically']
        randomDefencePhrase = random.choice(defencePhrases)

        if int(victimHealth) <= 0:
            alreadyDeadEmbed = discord.Embed(title=f"{memberName} attacks {victimName}", description=f"`..but {victimName} is already dead..`", color=colorBlack)
            alreadyDeadEmbed.set_thumbnail(url = heroImage)
            await channel.send(embed=alreadyDeadEmbed)
            await asyncio.sleep(5)
            continue

        spellDamage = '0'
        if spellName == 'Acid Rain':
            spellDamage = '10'
            spellUrl = "https://i.postimg.cc/0QLTnjGj/acid-rain-spell.webp"
            serverSpellName = 'acidRain'
        if spellName == 'Fire Ball':
            spellDamage = '20'
            spellUrl = "https://i.postimg.cc/Z5VXgVP1/fire-bolt-spell.webp"
            serverSpellName = 'fireBall'
        if spellName == "Lightning Strike":
            spellUrl = "https://i.postimg.cc/yNGt6xbj/lightning-bolt-spell.webp"
            spellDamage = '30'
            serverSpellName = 'lightningBolt'

    
        totalAttack = int(attackRoll) + int(heroAttack) + int(spellDamage)
        if spellName == 'false':
            attackEmbed = discord.Embed(title=f"{memberName} Attacks {victimName}", description=f"`{heroName}` {randomAttackPhrase} `{victimHeroName}` with their `{randomWeapon}`\n\n`Attack Roll: {attackRoll}`\n`{heroName} Attack: {heroAttack}`\n`Total Attack: {str(totalAttack)}`", color=colorRed)
        else:
            attackEmbed = discord.Embed(title=f"{memberName} Attacks {victimName}", description=f"`{heroName}` uses `{spellName}!`\n\n`{heroName}` {randomAttackPhrase} `{victimHeroName}` with their `{randomWeapon}`\n\n`Spell Attack: {spellDamage}`\n`Attack Roll: {attackRoll}`\n`{heroName} Attack: {heroAttack}`\n`Total Attack: {str(totalAttack)}`", color=colorRed)
            attackEmbed.set_image(url = spellUrl)
        attackEmbed.set_thumbnail(url = heroImage)
        await channel.send(embed=attackEmbed)
        await asyncio.sleep(5)

        totalDefence = int(victimDefenceRoll) + int(victimHeroDefence)  
        defenceEmbed = discord.Embed(title=f"{victimName} Defends", description=f"`{victimName}` {randomDefencePhrase} defends with their `{randomVictimWeapon}`\n\n`Defence Roll: {victimDefenceRoll}`\n`{victimHeroName} Defence: {victimHeroDefence}`\n`Total Defence: {str(totalDefence)}`", color=colorCyan)
        defenceEmbed.set_thumbnail(url = victimImage)
        await channel.send(embed=defenceEmbed)
        await asyncio.sleep(5)
        
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
        await asyncio.sleep(5)

        await setParticipantValue(victimId, 'health', str(updatedVictimHealth))
        
        if spellName != 'false':
            await setParticipantValue(memberId, 'spellName', "false")
            await removeSpell(memberId, serverSpellName)
        
    return
        


async def newParticipant(memberName, memberId, heroName, heroClass):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    try:
        serverDict['participantsDict'][str(memberId)]
        return(True)
    except:
        heroData = await getHeroData(heroName, heroClass, memberId)
         
        serverDict['participantsDict'][str(memberId)] = {}
        serverDict['participantsDict'][str(memberId)]['attackRoll'] = 'false'
        serverDict['participantsDict'][str(memberId)]['defenceRoll'] = 'false'
        serverDict['participantsDict'][str(memberId)]['victimName'] = 'false'
        serverDict['participantsDict'][str(memberId)]['spellName'] = 'false'
        serverDict['participantsDict'][str(memberId)]['health'] = '100'
        serverDict['participantsDict'][str(memberId)]['memberName'] = str(memberName)
        serverDict['participantsDict'][str(memberId)]['memberId'] = str(memberId)
        serverDict['participantsDict'][str(memberId)]['heroName'] = heroName
        serverDict['participantsDict'][str(memberId)]['heroAttack'] = heroData['attack']
        serverDict['participantsDict'][str(memberId)]['heroDefence'] = heroData['defence']
        serverDict['participantsDict'][str(memberId)]['heroImage'] = heroData['image']

        if 'knight' in heroClass:
            serverDict['participantsDict'][str(memberId)]['heroClass'] = 'knight'
            serverDict['participantsDict'][str(memberId)]['weapon1'] = heroData['leftScabbard']
            serverDict['participantsDict'][str(memberId)]['weapon2'] = heroData['rightScabbard']

        if 'druid' in heroClass:
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



async def removeSpell(discordId, spellName):
    # Define the endpoint URL and payload
    url = "https://www.heroesnft.app:3002/api/removeSpell"
    payload = {
        "memberId": discordId,
        "spellName": spellName
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


async def getHeroData(heroName, heroClass, memberId):

    wallets = await getMemberValue(memberId, 'wallets')
    wallet = wallets[0]

    if 'knight' in heroClass:
        walletKnights = await getWalletKnights(wallet)
        heroData = next((v for v in walletKnights.values() if v['name'] == heroName), None)
    if 'druid' in heroClass:
        walletDruids = await getWalletDruids(wallet)
        heroData = next((v for v in walletDruids.values() if v['name'] == heroName), None)
    return(heroData)
    


async def getWalletKnights(walletAddress):

    contractAddress = '0xD2deFe14811BEC6332C6ae8CcE85a858b3A80B56'
    filtered_entries = await fetch_nfts(walletAddress, 'eth', contractAddress)

    dict = {}
    i = 0
    for entry in filtered_entries:
        # Convert JSON string to dictionary
        metadata = json.loads(filtered_entries[i]['metadata'])
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
        if attack != None and not isinstance(attack, int):
            attack = ''.join([char for char in attack if char.isdigit()])
        dict[i]['attack'] = attack
        if attack != None and not isinstance(attack, int):
            defence = ''.join([char for char in defence if char.isdigit()])
        dict[i]['defence'] = defence
        dict[i]['image'] = image
        dict[i]['name'] = name

        i = i+1

    return(dict)

async def getWalletDruids(walletAddress):

    contractAddress = '0xAe65887F23558699978566664CC7dC0ccd67C0f8'
    filtered_entries = await fetch_nfts(walletAddress, 'polygon', contractAddress)
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
        if attack == None:
            attack = '0'
        dict[i]['attack'] = attack
        if defence != None:
            defence = ''.join([char for char in defence if char.isdigit()])
        if defence == None:
            defence = '0'
        dict[i]['defence'] = defence
        dict[i]['image'] = image
        dict[i]['name'] = name

        i = i+1

    return(dict)
        

    
async def fetch_nfts(wallet_address, chain, nft_contract):

    #So, our API does return the required results, but it is not on the first page. We return up to 100 results per page, but since that wallet has more than 100, it is needed to go to the next pages. That code also filters only the nft contract you showed.
    f = open("tokens")
    s = f.read()
    tokensDict = json.loads(s)
    api_key = tokensDict["moralis_api_key"]
    
    cursor = None
    max_pages = 9999  # maximum number of pages to fetch
    page_count = 0
    filtered_results = []
    while page_count < max_pages:
        response = requests.get(f"https://deep-index.moralis.io/api/v2.2/{wallet_address}/nft?chain={chain}&format=decimal&media_items=false",
                                headers={"accept": "application/json", "X-API-Key": api_key},
                                params={"cursor": cursor})
        data = response.json()
        if "result" in data:
            # Filter the result objects based on the specified nft_contract
            filtered_result = [item for item in data["result"] if item["token_address"].lower() == nft_contract.lower()]
            if len(filtered_result) > 0:
                filtered_results.extend(filtered_result)
            #print(f"Page {page_count + 1}: ", filtered_result) #list of dictionaries
            cursor = data.get("cursor")
            if not cursor:
                return(filtered_results)
        else:
            print("Failed to fetch data")
            break
        page_count += 1


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
            heroClass = participants[str(participant)]['heroClass']
            memberName = participants[str(participant)]['memberName']
            memberId = participants[str(participant)]['memberId']
            heroImage = participants[str(participant)]['heroImage']

    return(heroName, heroClass, memberName, memberId, heroImage)



async def getPlayerWithMostHealth():
    # Load the server dictionary from the file
    with open("serverDict", "r") as f:
        serverDict = json.loads(f.read())
    
    participants = serverDict["participantsDict"]

    # Initialize variables to keep track of the participant with the highest health
    max_health = None
    best_participant = None

    # Iterate through participants to find the one with the highest health
    for participant in participants:
        health = int(participants[str(participant)]['health'])
        
        if max_health is None or health > max_health:
            max_health = health
            best_participant = participants[str(participant)]

    if best_participant:
        heroName = best_participant['heroName']
        memberName = best_participant['memberName']
        memberId = best_participant['memberId']
        heroImage = best_participant['heroImage']

        return (heroName, memberName, memberId, heroImage, max_health)
    else:
        return None  # Handle the case where no participants are found
    
async def getAliveHeroesRows(memberId):
    
    API_URL = "https://www.heroesnft.app:3002"
    url = f"{API_URL}/api/alive-heroes/{memberId}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        alive_heroes = response.json().get("aliveHeroes", [])
        return(alive_heroes)
    except requests.exceptions.RequestException as error:
        print(f"Error fetching alive heroes for {memberId}:", error)


async def getHeroOptions(memberId):

    aliveHeroes = await getAliveHeroesRows(memberId)
    options = [[]]
    i = 0

    for idx, hero in enumerate(aliveHeroes):
        heroName = hero['heroName']
        attack = hero['heroAttack']
        defence = hero['heroDefence']
        heroClass = hero['heroClass']
        uniqueHeroClass = f"{heroClass}_{idx}"  # Append index to make it unique - discord requires value param to be unique

        if heroClass == 'druid':
            options[i].append(discord.SelectOption(label=heroName, description='Attack: '+attack+' | Defence: '+defence, emoji='⚗️', value=uniqueHeroClass))
        if heroClass == 'knight':
            options[i].append(discord.SelectOption(label=heroName, description='Attack: '+attack+' | Defence: '+defence, emoji='⚔️', value=uniqueHeroClass))
        
        if len(options[i]) >= 25:
            i += 1
            options.append([])

    return(options)


# async def getHeroOptions(memberId):

#     wallets = await getMemberValue(memberId, 'wallets')
#     wallet = wallets[0]

#     options = [[]]
#     i = 0
#     walletDruids = await getWalletDruids(wallet)
#     for idx, (key, value) in enumerate(walletDruids.items()):
#         attack = value['attack']
#         defence = value['defence']
#         heroClass = 'druid'
#         uniqueHeroClass = f"{heroClass}_{idx}"  # Append index to make it unique - discord requires value param to be unique

#         options[i].append(discord.SelectOption(label=value['name'], description='Attack: '+attack+' | Defence: '+defence, emoji='⚗️', value=uniqueHeroClass,))

#         if len(options[i]) >= 25:
#             i += 1
#             options.append([])


#     walletKnights = await getWalletKnights(wallet)
#     for idx, (key, value) in enumerate(walletKnights.items()):
#         attack = value['attack']
#         defence = value['defence']
#         heroClass = 'knight'
#         uniqueHeroClass = f"{heroClass}_{idx}"  # Append index to make it unique - discord requires value param to be unique
        
#         options[i].append(discord.SelectOption(label=value['name'], description='Attack: '+attack+' | Defence: '+defence, emoji='⚔️', value=uniqueHeroClass))
        
#         if len(options[i]) >= 25:
#             i += 1
#             options.append([])

#     return(options)
    

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



async def getSpellOptions(discordId):

    # Define the URL and parameters
    url = "https://www.heroesnft.app:3002/api/getRow"
    params = {
        "id": discordId,  # Replace with the actual user ID
        "table": "members"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        memberSpells = json.loads(data.get("availableSpells", "[]"))

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    options = []
    if "acidRain" in memberSpells:
        options.append(discord.SelectOption(label="Acid Rain", description='Damage: 10', emoji='🌧️'))
    if "fireBall" in memberSpells:
        options.append(discord.SelectOption(label="Fire Ball", description='Damage: 20', emoji='🔥'))
    if "lightningBolt" in memberSpells:
        options.append(discord.SelectOption(label="Acid Rain", description='Damage: 30', emoji='⚡'))
      
    return(options)


async def getIdFromName(discordName):

    f = open("serverDict")
    s = f.read()
    serverDict = json.loads(s)

    # Get the participants dictionary
    participants_dict = serverDict.get('participantsDict', {})

    # Iterate through participants and find the matching discordName
    for discordId, member_data in participants_dict.items():
        if member_data.get('memberName') == discordName:
            return discordId


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


                  
async def extractAndSortWins():

    allMembers = await getAllMembers()
    # Extract "Wins" and "discordName" values into a list of tuples
    wins_and_names = [(int(data["wins"]), data["discordName"]) for data in allMembers if int(data["wins"]) > 0]
    # Sort the list of tuples based on the "Wins" value
    sorted_wins_and_names = sorted(wins_and_names, reverse=True)
    return sorted_wins_and_names




async def getAllMembers():
    url = 'https://www.heroesnft.app:3002/api/members'  # Endpoint for getting all members

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Raises an HTTPError for unsuccessful status codes
                
                # Parse JSON response
                data = await response.json()
                print(f"Members Data: {data}")
                return data

    except aiohttp.ClientResponseError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


async def getMember(discord_id):
    url = f'https://www.heroesnft.app:3002/api/member/{discord_id}'
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                member_data = await response.json()  # Parse the JSON response into a dictionary
                return member_data

    except aiohttp.ClientResponseError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')



async def getMemberValue(discordId, key):
    url = f'https://www.heroesnft.app:3002/api/member/{discordId}/{key}'  # Use f-string for URL formatting
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:  # Use GET for fetching data
                response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                
                # Parse JSON response
                data = await response.json()
                return data.get(key)

    except aiohttp.ClientResponseError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')



async def updateMemberValue(discordId, key, newValue):
    url = f'https://www.heroesnft.app:3002/api/member/update'  # Use f-string for URL formatting
    payload = {
        'discordId': discordId,
        'key': key,
        'newValue': newValue
    }  # Create a payload with key and value to send in the request body

    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=payload) as response:  # Use PUT to update data
                response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                
                # Parse JSON response or handle success message
                data = await response.text()
                return data

    except aiohttp.ClientResponseError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')



async def getAllMembers():
    url = f'https://www.heroesnft.app:3002/api/members'
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                members_data = await response.json()  # Parse the JSON response into a dictionary
                return members_data

    except aiohttp.ClientResponseError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')



async def getMemberIds():
    url = f'https://www.heroesnft.app:3002/api/members/ids'
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                response_data = await response.json()  # Parse the JSON response into a dictionary
                return response_data

    except aiohttp.ClientResponseError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None
    

async def sendHgld(recipient_address, amount):
    api_url = "https://www.heroesnft.app:3002/api/send-hgld"

    f = open("tokens")
    s = f.read()
    tokensDict = json.loads(s)
    hohServerApiKey = tokensDict["hohServerApiKey"]

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': hohServerApiKey
    }
    payload = {
        'recipientAddress': recipient_address,
        'amount': amount
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()

        if response_data.get("success") and "transactionHash" in response_data:
            return response_data["transactionHash"]
        else:
            return {'error': response_data.get("message", "Unknown error")}
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}