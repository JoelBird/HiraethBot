import discord
import json
import botFunctions
from smartContract import smartContractFunctions
import asyncio
from binance.client import Client
import datetime
import random
import requests
import re

colorCyan = discord.Colour.from_str('#00ffcd')
colorRed = discord.Colour.from_str('#FF272A')
colorOrange = discord.Colour.from_str('#FF7A59')
colorGreen = discord.Colour.from_str('#7DB980')
colorBlack = discord.Colour.from_str('#0e1522')
colorWhite = discord.Colour.from_str('#FFFFFF')
colorPink = discord.Colour.from_str('#ffc0d6')
colorGold = discord.Colour.from_str('#FDD835')



class joinBattle(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    #id required for persistent view/ buttons to work on bot reset
    @discord.ui.button(custom_id = 'djifjfj31h', label='Join Battle', style=discord.ButtonStyle.red)
    async def button(self, interaction: discord.Interaction, button: discord.ui.Button):            
        await interaction.response.defer(ephemeral=True)

        member = await botFunctions.getMember(interaction.user.id)
        if member is None:
            embed = discord.Embed(title='You have not connected your account', description=f'Please connect at heroesnft.app to join the battle', color=colorGold)
            view = discord.ui.View()
            url = 'https://heroesnft.app'
            view.add_item(discord.ui.Button(label = 'heroesnft.app', style = discord.ButtonStyle.link, url = url))
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            return

        battleMode = await botFunctions.getServerDictValue('battleMode')
        ghostBattleStarterId = await botFunctions.getServerDictValue('ghostBattleStarterId')
        if battleMode == 'ghost' and str(interaction.user.id) != str(ghostBattleStarterId):
            embed = discord.Embed(title='', description='You cannot join this ghost battle', color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
        
        battleStarterId = await botFunctions.getServerDictValue('1v1BattleStarterId')
        battleVictimId = await botFunctions.getServerDictValue('1v1BattleVictimId')
        if battleMode == '1v1' and str(interaction.user.id) not in str(battleStarterId) + str(battleVictimId):
            embed = discord.Embed(title='', description='You cannot join this 1v1 battle', color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
        
        options = await botFunctions.getHeroOptions(interaction.user.id)
        options2 = options[0]
        totalHeroes = len(options2)

        if totalHeroes == 0:
            embed = discord.Embed(title='', description='We could not find any Knights/Druids in your wallets', color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
    
        await botFunctions.update_hero_options_position(interaction.user.id, 0)
        
        view = discord.ui.View()
        select = heroSelect(options=options2)
        view.add_item(select)

        if len(options) > 1:
            button = theButton(label="➡️", custom_id='awdf312', style=discord.ButtonStyle.blurple)
            view.add_item(button)

        embed = discord.Embed(title='Select a Hero', description='Select a hero to use in this battle with the dropdown below', color=colorRed)
        embed.set_thumbnail(url = "https://i.postimg.cc/wMJQnydT/fotor-ai-20240403211513.jpg")

        await interaction.followup.send(embed=embed, view=view, ephemeral = True)


    @discord.ui.button(custom_id = 'awdwadp2o', label='Participants', style=discord.ButtonStyle.blurple)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):            
        await interaction.response.defer(ephemeral=True)
        listOfPlayerNames = await botFunctions.getPlayerNames()
        playersString = ''
        for player in listOfPlayerNames:
            playersString = playersString + f"🎮 `{player}`\n"
        
        embed = discord.Embed(title="", description = f"## Participants for this battle\n\n{playersString}", color=colorCyan)
        embed.set_thumbnail(url = "https://i.postimg.cc/yYfznPPL/contoller-emoji.png")
        await interaction.followup.send(embed=embed, ephemeral = True)




#This select is different, its a subclassed discord.ui.select, which means i can parse variables to it inside the init
class spellSelect(discord.ui.Select):
    def __init__(self, options) -> None:
      super().__init__(
        custom_id = 'f24fqf666g24',
        placeholder = "Select a Spell",
        options = options
      )
    #Just callback for this method, not select_callback
    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True)

        spellName = str(self.values[0])
        await botFunctions.setParticipantDictValue(interaction, 'spellName', spellName)
        
        if spellName == "Acid Rain":
            imageUrl = "https://i.postimg.cc/0QLTnjGj/acid-rain-spell.webp"
        if spellName == "Fire Ball":
            imageUrl = "https://i.postimg.cc/Z5VXgVP1/fire-bolt-spell.webp"
        if spellName == "Lightning Bolt":
            imageUrl = "https://i.postimg.cc/yNGt6xbj/lightning-bolt-spell.webp"

        embed = discord.Embed(title=spellName, description=f"You have chosen to use `{spellName}` on your victim", color=colorRed) #victimeName Doesnt work with ``
        embed.set_thumbnail(url = imageUrl)
        await interaction.followup.send(embed=embed, ephemeral = True)


#This select is different, its a subclassed discord.ui.select, which means i can parse variables to it inside the init
class victimSelect(discord.ui.Select):
    def __init__(self, options) -> None:
      super().__init__(
        custom_id = 'g3r12dewf21',
        placeholder = "Select a Victim",
        options = options
      )
    #Just callback for this method, not select_callback
    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True)

        isParticipant = await botFunctions.isParticipant(interaction)
        if isParticipant == False:
            embed = discord.Embed(title="",description='You are not a participant of this battle', color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
        
        health = await botFunctions.getParticipantValue(interaction.user.id, 'health')
        if int(health) <= 0:
            embed = discord.Embed(title="",description="Your Hero is dead", color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
        
        victimName = str(self.values[0])
        if victimName == str(interaction.user.name):
            embed = discord.Embed(title="",description=f'You cannot attack yourself', color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return

        hasSelectedVictim, victimName2 = await botFunctions.hasSelectedVictim(interaction)
        if hasSelectedVictim == True:
            embed = discord.Embed(title="",description=f"You have already selected `{victimName2}` as a victim", color=colorBlack)
            await interaction.followup.send(embed=embed, ephemeral = True)
            return
        
        await botFunctions.setParticipantDictValue(interaction, 'victimName', victimName)
        embed = discord.Embed(title="",description=f"You have chosen to attack `{victimName}`", color=colorRed) #victimeName Doesnt work with ``
        await interaction.followup.send(embed=embed, ephemeral = True)



#This select is different, its a subclassed discord.ui.select, which means i can parse variables to it inside the init
class heroSelect(discord.ui.Select):
    def __init__(self, options) -> None:
      super().__init__(
        custom_id = 'gw4dd12r21ed13',
        placeholder = "Select a Hero",
        options = options
      )
    #Just callback for this method, not select_callback
    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True)

        uniqueHeroClass = self.values[0] #Only way that works to get label and name
        for option in self.options:
            if option.value == uniqueHeroClass:
                heroName = option.label
                break

        heroData = await botFunctions.getHeroData(heroName, uniqueHeroClass, interaction.user.id)
        
        if 'knight' in uniqueHeroClass:
            embed = discord.Embed(title=heroName, description=f"`Attack: {heroData['attack']}\nDefence: {heroData['defence']}\nRight Scabbard: {heroData['rightScabbard']}\nLeft Scabbard: {heroData['leftScabbard']}`", color=colorBlack)
            embed.set_image(url = str(heroData['image']))
            embed.set_thumbnail(url = "https://i.postimg.cc/J7kFc3cP/knight-shield.png")

        if 'druid' in uniqueHeroClass:
            embed = discord.Embed(title=heroName, description=f"`Attack: {heroData['attack']}\nDefence: {heroData['defence']}\nStaff: {heroData['staff']}\nSpell: {heroData['spell']}\nWeapon: {heroData['weapon']}`", color=colorBlack)
            embed.set_image(url = str(heroData['image']))
            embed.set_thumbnail(url = "https://i.postimg.cc/Kv3fPQ4Z/druid-orb.png")

        view = discord.ui.View()
        options = await botFunctions.getHeroOptions(interaction.user.id)
        currentHeroOptionsPosition = await botFunctions.get_hero_options_position(interaction.user.id)
        options2 = options[int(currentHeroOptionsPosition)]
        select = heroSelect(options=options2)
        view.add_item(select)

        if int(currentHeroOptionsPosition) > 0:
            button = theButton(label="⬅️", custom_id='dawd21', style=discord.ButtonStyle.blurple)
            view.add_item(button)

        if int(currentHeroOptionsPosition) + 1 < len(options):
            button = theButton(label="➡️", custom_id='awdf2e1', style=discord.ButtonStyle.blurple)
            view.add_item(button)

        button = theButton(label="Select Hero", custom_id='awdwadaf3g', heroName=heroName, uniqueHeroClass=uniqueHeroClass, style=discord.ButtonStyle.green)
        view.add_item(button)

        await interaction.followup.edit_message(message_id = interaction.message.id, embed=embed, view=view)


class theButton(discord.ui.Button):
    def __init__(self, label, custom_id, style, heroName=None, uniqueHeroClass=None) -> None:
        super().__init__(
            label=label,
            custom_id=custom_id,
            style=style
        )
        self.heroName = heroName
        self.uniqueHeroClass = uniqueHeroClass

    async def callback(self, interaction: discord.Interaction):
        
        #Dont add defer here, because some functions accessed here have their own defers

        if self.label == "Select Hero":
            await interaction.response.defer(ephemeral=True)

            heroName = str(self.heroName)
            isAlreadyParticipant = await botFunctions.newParticipant(interaction.user.name, interaction.user.id, self.heroName, self.uniqueHeroClass)
            battleMode = await botFunctions.getServerDictValue('battleMode')
            if isAlreadyParticipant == False and battleMode != 'ghost' and battleMode != '1v1':
                await botFunctions.updateBattleEmbed(interaction)
            
            embed = discord.Embed(description=f'You have joined the battle with `{heroName}`', color=colorGreen)
            await interaction.followup.send(embed=embed, ephemeral = True)

            participantsToStart = await botFunctions.getServerDictValue('participantsToStart')
            numberOfParticipants = await botFunctions.getAllParticipantIds()
            numberOfParticipants = str(len(numberOfParticipants))
            if battleMode == 'participants' and numberOfParticipants == participantsToStart:
                await botFunctions.startBattle(interaction.client)

            if battleMode == 'ghost':
                await botFunctions.startBattle(interaction.client)

            if battleMode == '1v1' and int(numberOfParticipants) == 2:
                await botFunctions.startBattle(interaction.client)

        if self.label == "Use A Spell":
            await interaction.response.defer(ephemeral=True)

            isParticipant = await botFunctions.isParticipant(interaction)
            if isParticipant == False:
                embed = discord.Embed(title="",description='You are not a participant of this battle', color=colorBlack)
                await interaction.followup.send(embed=embed, ephemeral = True)
                return
            
            health = await botFunctions.getParticipantValue(interaction.user.id, 'health')
            if int(health) <= 0:
                embed = discord.Embed(title="",description="Your Hero is dead", color=colorBlack)
                await interaction.followup.send(embed=embed, ephemeral = True)
                return
            
            view = discord.ui.View()
            options = await botFunctions.getSpellOptions(interaction.user.id)

            if len(options) == 0:
                embed = discord.Embed(title="You do not have any spells",description="Go to `heroesnft.app` to get a spell", color=colorBlack)
                view = discord.ui.View()
                url = 'https://heroesnft.app'
                view.add_item(discord.ui.Button(label = 'heroesnft.app', style = discord.ButtonStyle.link, url = url))
                await interaction.followup.send(embed=embed, view=view, ephemeral = True)
                return

            select = spellSelect(options=options)
            view.add_item(select)
            
            embed = discord.Embed(title="Select a spell below", color=colorGold)
            embed.set_thumbnail(url = "https://i.postimg.cc/NMQJjYjL/mystery-spell.webp")

            await interaction.followup.send(embed=embed, view=view, ephemeral = True)


        # if self.label == "Roll For Attack":
        #     await interaction.response.defer(ephemeral=True)

        #     isParticipant = await botFunctions.isParticipant(interaction)
        #     if isParticipant == False:
        #         embed = discord.Embed(title="",description='You are not a participant of this battle', color=colorBlack)
        #         await interaction.followup.send(embed=embed, ephemeral = True)
        #         return
            
        #     health = await botFunctions.getParticipantValue(interaction.user.id, 'health')
        #     if int(health) <= 0:
        #         embed = discord.Embed(title="",description="Your Hero is dead", color=colorBlack)
        #         await interaction.followup.send(embed=embed, ephemeral = True)
        #         return
            
        #     hasRolledForAttack, roll = await botFunctions.hasRolledForAttack(interaction)
        #     if hasRolledForAttack == True:
        #         embed = discord.Embed(title="",description=f'You have already rolled a `{roll}` for Attack', color=colorBlack)
        #         await interaction.followup.send(embed=embed, ephemeral = True)
        #         return

        #     random_number = random.randint(0, 100)
        #     await botFunctions.setParticipantDictValue(interaction, 'attackRoll', random_number)
        #     embed = discord.Embed(title="",description=f'You have rolled `{random_number}` for Attack', color=colorRed)
        #     await interaction.followup.send(embed=embed, ephemeral = True)

        # if self.label == "Roll For Defence":
        #     await interaction.response.defer(ephemeral=True)

        #     isParticipant = await botFunctions.isParticipant(interaction)
        #     if isParticipant == False:
        #         embed = discord.Embed(title="",description='You are not a participant of this battle', color=colorBlack)
        #         await interaction.followup.send(embed=embed, ephemeral = True)
        #         return
            
        #     health = await botFunctions.getParticipantValue(interaction.user.id, 'health')
        #     if int(health) <= 0:
        #         embed = discord.Embed(title="",description="Your Hero is dead", color=colorBlack)
        #         await interaction.followup.send(embed=embed, ephemeral = True)
        #         return
            
        #     hasRolledForDefence, roll = await botFunctions.hasRolledForDefence(interaction)
        #     if hasRolledForDefence == True:
        #         embed = discord.Embed(title="",description=f'You have already rolled a `{roll}` for Defence', color=colorBlack)
        #         await interaction.followup.send(embed=embed, ephemeral = True)
        #         return

        #     random_number = random.randint(0, 50)
        #     await botFunctions.setParticipantDictValue(interaction, 'defenceRoll', random_number)
        #     embed = discord.Embed(title="",description=f'You have rolled `{random_number}` for Defence', color=colorCyan)
        #     await interaction.followup.send(embed=embed, ephemeral = True)


        if self.label == "⬅️":
            await interaction.response.defer(ephemeral=True)

            view = discord.ui.View()
            options = await botFunctions.getHeroOptions(interaction.user.id)
            currentHeroOptionsPosition = await botFunctions.get_hero_options_position(interaction.user.id)
            updatedHeroOptionsPosition = int(currentHeroOptionsPosition) - 1
            await botFunctions.update_hero_options_position(interaction.user.id, updatedHeroOptionsPosition)

            options = options[int(updatedHeroOptionsPosition)]
            select = heroSelect(options=options)
            view.add_item(select)

            if int(updatedHeroOptionsPosition) > 0:
                button = theButton(label="⬅️", custom_id='dawd21', style=discord.ButtonStyle.blurple)
                view.add_item(button)

            if int(updatedHeroOptionsPosition) + 1 < len(options):
                button = theButton(label="➡️", custom_id='awdf2e1', style=discord.ButtonStyle.blurple)
                view.add_item(button)

            title = interaction.message.embeds[0].title
            if title != 'Select a Hero':
                button = theButton(label="Select Hero", custom_id=title, style=discord.ButtonStyle.green)
                view.add_item(button)

            await interaction.followup.edit_message(message_id = interaction.message.id, view = view)

        if self.label == "➡️":
            await interaction.response.defer(ephemeral=True)

            view = discord.ui.View()
            options = await botFunctions.getHeroOptions(interaction.user.id)
            
            currentHeroOptionsPosition = await botFunctions.get_hero_options_position(interaction.user.id)
            UpdatedHeroOptionsPosition = int(currentHeroOptionsPosition) + 1
            await botFunctions.update_hero_options_position(interaction.user.id, UpdatedHeroOptionsPosition)

            options2 = options[int(UpdatedHeroOptionsPosition)]
            select = heroSelect(options=options2)
            view.add_item(select)

            if int(UpdatedHeroOptionsPosition) > 0:
                button = theButton(label="⬅️", custom_id='dawd21', style=discord.ButtonStyle.blurple)
                view.add_item(button)

            if int(UpdatedHeroOptionsPosition) + 1 < len(options):
                button = theButton(label="➡️", custom_id='awdf2e1', style=discord.ButtonStyle.blurple)
                view.add_item(button)

            title = interaction.message.embeds[0].title
            if title != 'Select a Hero':
                button = theButton(label="Select Hero", custom_id=title, style=discord.ButtonStyle.green)
                view.add_item(button)

            await interaction.followup.edit_message(message_id = interaction.message.id, view = view)