import discord
import json
import botFunctions
from smartContract import smartContractFunctions
import asyncio
from binance.client import Client
import datetime
import random
import requests
import embeds
import re

colorCyan = discord.Colour.from_str('#00ffcd')
colorRed = discord.Colour.from_str('#FF272A')
colorOrange = discord.Colour.from_str('#FF7A59')
colorGreen = discord.Colour.from_str('#7DB980')
colorBlack = discord.Colour.from_str('#0e1522')
colorWhite = discord.Colour.from_str('#FFFFFF')
colorPink = discord.Colour.from_str('#ffc0d6')
colorGold = discord.Colour.from_str('#FDD835')




#This select is different, its a subclassed discord.ui.select, which means i can parse variables to it inside the init
class victimSelect(discord.ui.Select):
    def __init__(self, options) -> None:
      super().__init__(
        custom_id = 'awdaf3r1231',
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
            embed = discord.Embed(title="",description=f'You cannot Attack yourself', color=colorBlack)
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
        placeholder = "Select a hero",
        options = options
      )
    #Just callback for this method, not select_callback
    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True)

        #await botFunctions.setServerDictValue(interaction.guild.id, 'participantsDict', cycledTimes, 'cycledTimes')
        heroName = str(self.values[0])
        heroData = await botFunctions.getHeroData(heroName, interaction.user.id)
        
        if 'Knight' in heroName:
            embed = discord.Embed(title=heroName, description=f"Attack: {heroData['attack']}\nDefence: {heroData['defence']}\nRight Scabbard: {heroData['rightScabbard']}\nLeft Scabbard: {heroData['leftScabbard']}", color=colorBlack)
            embed.set_image(url = str(heroData['image']))

        if 'Druid' in heroName:
            embed = discord.Embed(title=heroName, description=f"Attack: {heroData['attack']}\nDefence: {heroData['defence']}\nStaff: {heroData['staff']}\nSpell: {heroData['spell']}\nWeapon: {heroData['weapon']}", color=colorBlack)
            embed.set_image(url = str(heroData['image']))

        view = discord.ui.View()
        options = await botFunctions.getHeroOptions(interaction.user.id)
        heroOptionsPosition = await botFunctions.getMemberDictValue(interaction.user.id, 'heroOptionsPosition')
        options2 = options[int(heroOptionsPosition)]
        select = heroSelect(options=options2)
        view.add_item(select)

        if int(heroOptionsPosition) > 0:
            button = theButton(label="⬅️", custom_id='dawd21', style=discord.ButtonStyle.blurple)
            view.add_item(button)

        if int(heroOptionsPosition) + 1 < len(options):
            button = theButton(label="➡️", custom_id='awdf2e1', style=discord.ButtonStyle.blurple)
            view.add_item(button)

        button = theButton(label="Select Hero", custom_id=heroName, style=discord.ButtonStyle.green)
        view.add_item(button)

        await interaction.followup.edit_message(message_id = interaction.message.id, embed=embed, view=view)


class theButton(discord.ui.Button):
    def __init__(self, label, custom_id, style) -> None:
        super().__init__(
            label=label,
            custom_id=custom_id,
            style=style
        )

    async def callback(self, interaction: discord.Interaction):
        
        #Dont add defer here, because some functions accessed here have their own defers
        
        if self.label == "Join Battle":
            await interaction.response.defer(ephemeral=True)

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
            
            await botFunctions.newMemberFunc(str(interaction.user.id), str(interaction.user.name))

            ethereumWallet = await botFunctions.getMemberDictValue(interaction.user.id, 'ethereumWallet')
            polygonWallet = await botFunctions.getMemberDictValue(interaction.user.id, 'polygonWallet')

            if ethereumWallet and polygonWallet == 'false':
                embed = discord.Embed(title='You have not connected a wallet', description='Use `/connect_wallets`', color=colorBlack)
                await interaction.followup.send(embed=embed, ephemeral = True)
                return
            
            options = await botFunctions.getHeroOptions(interaction.user.id)
            options2 = options[0]
            totalHeroes = len(options2)

            if totalHeroes == 0:
                embed = discord.Embed(title='', description='We could not find any Knights/Druids in your wallets', color=colorBlack)
                await interaction.followup.send(embed=embed, ephemeral = True)
                return
        
            await botFunctions.setMemberDictValue(interaction.user.id, 'heroOptionsPosition', '0')
            view = discord.ui.View()
            select = heroSelect(options=options2)
            view.add_item(select)

            if len(options) > 1:
                button = theButton(label="➡️", custom_id='awdf2e1', style=discord.ButtonStyle.blurple)
                view.add_item(button)

            embed = discord.Embed(title='Select a hero', description='Select a hero to use in this battle with the dropdown below', color=colorRed)
            embed.set_thumbnail(url = "https://i.postimg.cc/wMJQnydT/fotor-ai-20240403211513.jpg")

            await interaction.followup.send(embed=embed, view=view, ephemeral = True)

        if self.label == "Select Hero":
            await interaction.response.defer(ephemeral=True)

            heroName = str(self.custom_id)
            isAlreadyParticipant = await botFunctions.newParticipant(interaction.user.name, interaction.user.id, heroName)
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

        if self.label == "Roll For Attack":
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
            
            hasRolledForAttack, roll = await botFunctions.hasRolledForAttack(interaction)
            if hasRolledForAttack == True:
                embed = discord.Embed(title="",description=f'You have already rolled a `{roll}` for Attack', color=colorBlack)
                await interaction.followup.send(embed=embed, ephemeral = True)
                return

            random_number = random.randint(0, 100)
            await botFunctions.setParticipantDictValue(interaction, 'attackRoll', random_number)
            embed = discord.Embed(title="",description=f'You have rolled `{random_number}` for Attack', color=colorRed)
            await interaction.followup.send(embed=embed, ephemeral = True)

        if self.label == "Roll For Defence":
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
            
            hasRolledForDefence, roll = await botFunctions.hasRolledForDefence(interaction)
            if hasRolledForDefence == True:
                embed = discord.Embed(title="",description=f'You have already rolled a `{roll}` for Defence', color=colorBlack)
                await interaction.followup.send(embed=embed, ephemeral = True)
                return

            random_number = random.randint(0, 100)
            await botFunctions.setParticipantDictValue(interaction, 'defenceRoll', random_number)
            embed = discord.Embed(title="",description=f'You have rolled `{random_number}` for Defence', color=colorCyan)
            await interaction.followup.send(embed=embed, ephemeral = True)


        if self.label == "⬅️":
            await interaction.response.defer(ephemeral=True)

            view = discord.ui.View()
            options = await botFunctions.getHeroOptions(interaction.user.id)
            heroOptionsPosition = await botFunctions.getMemberDictValue(interaction.user.id, 'heroOptionsPosition')
            if int(heroOptionsPosition) != 0:
                heroOptionsPosition = int(heroOptionsPosition) - 1
                await botFunctions.setMemberDictValue(interaction.user.id, 'heroOptionsPosition', str(heroOptionsPosition))

            options = options[int(heroOptionsPosition)]
            select = heroSelect(options=options)
            view.add_item(select)

            if int(heroOptionsPosition) > 0:
                button = theButton(label="⬅️", custom_id='dawd21', style=discord.ButtonStyle.blurple)
                view.add_item(button)

            if int(heroOptionsPosition) + 1 < len(options):
                button = theButton(label="➡️", custom_id='awdf2e1', style=discord.ButtonStyle.blurple)
                view.add_item(button)

            title = interaction.message.embeds[0].title
            if title != 'Select a hero':
                button = theButton(label="Select Hero", custom_id=title, style=discord.ButtonStyle.green)
                view.add_item(button)

            await interaction.followup.edit_message(message_id = interaction.message.id, view = view)

        if self.label == "➡️":
            await interaction.response.defer(ephemeral=True)

            view = discord.ui.View()
            options = await botFunctions.getHeroOptions(interaction.user.id)
            heroOptionsPosition = await botFunctions.getMemberDictValue(interaction.user.id, 'heroOptionsPosition')
            
            heroOptionsPosition = int(heroOptionsPosition) + 1
            await botFunctions.setMemberDictValue(interaction.user.id, 'heroOptionsPosition', str(heroOptionsPosition))

            options2 = options[int(heroOptionsPosition)]
            select = heroSelect(options=options2)
            view.add_item(select)

            if int(heroOptionsPosition) > 0:
                button = theButton(label="⬅️", custom_id='dawd21', style=discord.ButtonStyle.blurple)
                view.add_item(button)

            if int(heroOptionsPosition) + 1 < len(options):
                button = theButton(label="➡️", custom_id='awdf2e1', style=discord.ButtonStyle.blurple)
                view.add_item(button)

            title = interaction.message.embeds[0].title
            if title != 'Select a hero':
                button = theButton(label="Select Hero", custom_id=title, style=discord.ButtonStyle.green)
                view.add_item(button)

            await interaction.followup.edit_message(message_id = interaction.message.id, view = view)