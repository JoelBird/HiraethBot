import discord
from discord import ui
import json
import asyncio
import botFunctions
import requests
import views
import random
import datetime
import embeds
import nest_asyncio
nest_asyncio.apply() #used to fix twint RuntimeError: This event loop is already running in async function

colorCyan = discord.Colour.from_str('#00ffcd')
colorRed = discord.Colour.from_str('#FF272A')
colorOrange = discord.Colour.from_str('#FF7A59')
colorGreen = discord.Colour.from_str('#7DB980')
colorBlack = discord.Colour.from_str('#0e1522')
colorWhite = discord.Colour.from_str('#FFFFFF')
colorPink = discord.Colour.from_str('#ffc0d6')
colorGold = discord.Colour.from_str('#FDD835')



class createTask(ui.Modal, title = "Create Task"):

    taskTitle = ui.TextInput(label = "Task Title", style = discord.TextStyle.short, placeholder = "Gartic Bot", required = True, max_length = 25)
    taskDescription = ui.TextInput(label = "Short Description", style = discord.TextStyle.short, placeholder = "Participants play Gartic bot to earn Tokens", required = True, max_length = 100)
    participantInstructions = ui.TextInput(label = "Participant Instructions", style = discord.TextStyle.long, placeholder = "1️⃣ Win 3 Gartic Games \n2️⃣ Press the **Contribute** button below and submit your proof!", required = True, max_length = 800)
    tokenReward = ui.TextInput(label = "Token Reward Amount", style = discord.TextStyle.short, placeholder = "5", required = True, max_length = 2)
    taskImageUrl = ui.TextInput(label = "Task Image Link", style = discord.TextStyle.short, placeholder = "https://i.postimg.cc/c1cdQRkJ/Whitelist.png", required = False, max_length = 100)


    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True) 

        taskTitle = str(self.taskTitle)
        taskDescription = str(self.taskDescription)
        participantInstructions = str(self.participantInstructions)
        tokenReward = str(self.tokenReward)
        taskImageUrl = str(self.taskImageUrl)


         #Check that thumbnail_url points to valid image, else use default image - cant try except
        if 'https://' in str(self.taskImageUrl):
            image_formats = ("image/png", "image/jpeg", "image/jpg")
            r = requests.head(str(self.taskImageUrl))
            if r.headers["content-type"] in image_formats:
                taskImageUrl = str(self.taskImageUrl)
            else:
                taskImageUrl =  'https://i.postimg.cc/jjJ0wXgv/emojipng-com-7209894.png'      
        else:
            taskImageUrl =  'https://i.postimg.cc/jjJ0wXgv/emojipng-com-7209894.png'     

        try:
            int(tokenReward)
        except:
            
            tasksImageEmbed = discord.Embed(title='', color=openProjBlack)
            tasksImageEmbed.set_image(url = 'https://i.postimg.cc/T1MCMgFg/tasks.jpg')
            embed = discord.Embed(title='',description='Please insert a number into the **Token Reward Amount** field', color=openProjBlack)
            embedsList = [tasksImageEmbed, embed]
            await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = views.managerTasksGoBack())
            return


        f = open("serverAccounts.txt")
        s = f.read()
        serversDict = json.loads(s)

        for account in serversDict: ##  this method shit, should use setServerDict, no time
            if str(interaction.guild.id) == str(serversDict[account]['serverId']):
                serversDict[str(account)]['taskInfo'][taskTitle] = {}
                serversDict[str(account)]['taskInfo'][taskTitle]['taskDescription'] = taskDescription
                serversDict[str(account)]['taskInfo'][taskTitle]['participantInstructions'] = participantInstructions
                serversDict[str(account)]['taskInfo'][taskTitle]['tokenReward'] = tokenReward
                serversDict[str(account)]['taskInfo'][taskTitle]['taskImageUrl'] = taskImageUrl
                serversDict[str(account)]['taskInfo'][taskTitle]['isCustomTask'] = 'False'
                serversDict[str(account)]['taskInfo'][taskTitle]['status'] = 'enabled'
                serversDict[str(account)]['taskInfo'][taskTitle]['distributions'] = '0'
                serversDict[str(account)]['taskInfo'][taskTitle]['participants'] = []
                serversDict[str(account)]['taskInfo'][taskTitle]['tokensDistributed'] = '0'
                serversDict[str(account)]['listOfCustomTaskTitles'].append(taskTitle)

        with open('serverAccounts.txt', 'w') as f:
            json.dump(serversDict, f, indent=4)

    
        tasksImageEmbed = discord.Embed(title='', color=openProjBlack)
        tasksImageEmbed.set_image(url = 'https://i.postimg.cc/T1MCMgFg/tasks.jpg')
        embed = await botFunctions.embedMaker('managerTasks', 'black', interaction.guild)
        embedsList = [tasksImageEmbed, embed]
        button = views.theButton(label='Create Task', custom_id="31315578766", style=discord.ButtonStyle.grey)
        options = await botFunctions.getManagerTasksOptions(interaction.guild)
        view = discord.ui.View()
        select = views.managerTaskSelect(options)
        view.add_item(button)
        view.add_item(select)
        await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = view)




class addWinnerItemReward(ui.Modal, title = "Add Contest Item Reward"):

    
        rewardName = ui.TextInput(label = "Reward Name", style = discord.TextStyle.short, placeholder = "Whitelist", required = True, max_length = 25)
        rewardDescription = ui.TextInput(label = "Reward Description", style = discord.TextStyle.long, placeholder = "Secure your spot in the premint!", required = True, max_length = 300)
        rewardPositionsToReceive = ui.TextInput(label = "Leaderboard position/s to receive", style = discord.TextStyle.short, placeholder = "2,3,4", required = True, max_length = 50)
        rewardImageUrl = ui.TextInput(label = "Reward Image Link", style = discord.TextStyle.short, placeholder = "https://i.postimg.cc/c1cdQRkJ/Whitelist.png", required = True, max_length = 100)
 
        def __init__(self, title): #parse variables to modal

            self.title = title
            super().__init__(custom_id = '7876896569')

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True) 

            title = self.title

            rewardPositionsToReceive = str(self.rewardPositionsToReceive) 
            rewardPositionsToReceive = rewardPositionsToReceive.replace(' ', '')
            rewardPositionsToReceiveJustNumbers = str(rewardPositionsToReceive.replace(',', ''))
            rewardPositionsToReceiveLength = str(len(rewardPositionsToReceiveJustNumbers))

            try:
                int(rewardPositionsToReceiveJustNumbers)
            except:
                
                rewardsImageEmbed = discord.Embed(title='', color=openProjBlack)
                rewardsImageEmbed.set_image(url = 'https://i.postimg.cc/DwcTj1zc/rewards.jpg')
                embed = discord.Embed(title='',description='Please insert number/s seperated by commas into the **Leaderboard position/s to receive** field', color=openProjBlack)
                embedsList = [rewardsImageEmbed, embed]
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = views.managerRewardsGoBack())
                return
            
            rewardPositionsToReceiveList = rewardPositionsToReceive.split(',')
            rewardPositionsToReceiveList = [int(num) for num in rewardPositionsToReceiveList]  # Convert the strings to integers if needed
        
            
            
            #Check that thumbnail_url points to valid image, else use default image - cant try except
            if 'https://' in str(self.rewardImageUrl):
                image_formats = ("image/png", "image/jpeg", "image/jpg")
                r = requests.head(str(self.rewardImageUrl))
                if r.headers["content-type"] in image_formats:
                    rewardImageUrl = str(self.rewardImageUrl)
                else:
                    rewardImageUrl =  'https://i.postimg.cc/RFqcnQLW/566px-Tf-gift.png'      
            else:
                rewardImageUrl =  'https://i.postimg.cc/RFqcnQLW/566px-Tf-gift.png'      
        
            
            rewardNames = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardNames')
            if str(self.rewardName) in rewardNames: #Avoiding 'The specified option value is already used' error
                embed = discord.Embed(title='',description='You have already created a Reward with that name')
                await interaction.followup.edit_message(message_id = interaction.message.id, embed=embed, view = views.managerRewardsGoBack())
                return

            leaderboardPositionToReceive = await botFunctions.getServerDictValue(interaction.guild.id, 'leaderboardPositionToReceive')
            rewardDescriptions = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardDescriptions')
            rewardAmountToGiveaway = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardAmountToGiveaway')
            rewardDistributions = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardDistributions')
            rewardImageUrls= await botFunctions.getServerDictValue(interaction.guild.id, 'rewardImageUrls')
            poolPercents = await botFunctions.getServerDictValue(interaction.guild.id, 'poolPercents')
            rewardTypes = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardTypes')



            leaderboardPositionToReceive.append(rewardPositionsToReceiveList)
            rewardNames.append(str(self.rewardName))
            rewardDescriptions.append(str(self.rewardDescription))
            rewardAmountToGiveaway.append(rewardPositionsToReceiveLength)
            rewardDistributions.append('0')
            rewardImageUrls.append(rewardImageUrl)
            poolPercents.append('0')
            rewardTypes.append('item')


            await botFunctions.setServerDictValue(interaction.guild.id, 'leaderboardPositionToReceive', leaderboardPositionToReceive)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardNames', rewardNames)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardDescriptions', rewardDescriptions)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardAmountToGiveaway', rewardAmountToGiveaway)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardDistributions', rewardDistributions)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardImageUrls', rewardImageUrls)
            await botFunctions.setServerDictValue(interaction.guild.id, 'poolPercents', poolPercents)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardTypes', rewardTypes)


            menuStatus = await botFunctions.getServerDictValue(interaction.guild.id, 'menuStatus')
            enabledTasks = await botFunctions.getEnabledTasks(interaction.guild)
            if menuStatus == 'tokenConfig-rewards' and len(enabledTasks) == 0: #No enabled tasks
                await botFunctions.setServerDictValue(interaction.guild.id, 'menuStatus', 'tokenConfig-EnableATask')
            elif menuStatus == 'tokenConfig-rewards' and len(enabledTasks) != 0: #Has enabled tasks. skip
                await botFunctions.setServerDictValue(interaction.guild.id, 'menuStatus', 'distributionsEnabled')
            
            participationMode = await botFunctions.getServerDictValue(interaction.guild.id, 'participationMode')
            if participationMode == 'free':
                await botFunctions.generateManagerRewardsMenu(interaction, 'edit')
            if participationMode == 'fee':
                await botFunctions.generateManagerFeeRewardsMenu(interaction, 'edit')




class addWinnerPoolReward(ui.Modal, title = "Add Contest Pool Reward"):

        percentage = ui.TextInput(label = "Percent of Pool", style = discord.TextStyle.short, placeholder = "10", required = True, max_length = 2)
        rewardPositionsToReceive = ui.TextInput(label = "Leaderboard position/s to receive", style = discord.TextStyle.short, placeholder = "2,3,4", required = True, max_length = 50)
 
        def __init__(self): #parse variables to modal
            super().__init__(custom_id = 'eafdqd3fwdawd')

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True) 

            percentage = str(self.percentage)
            rewardPositionsToReceive = str(self.rewardPositionsToReceive) 

            poolPercents = await botFunctions.getServerDictValue(interaction.guild.id, 'poolPercents')
            if str(self.percentage) in poolPercents: #Avoiding 'The specified option value is already used' error
                embed = discord.Embed(title='',description='You have already created a Reward with that percent')
                await interaction.followup.edit_message(message_id = interaction.message.id, embed=embed, view = views.managerRewardsGoBack())
                return
            
            rewardPositionsToReceive = rewardPositionsToReceive.replace(' ', '')
            rewardPositionsToReceiveJustNumbers = str(rewardPositionsToReceive.replace(',', ''))
            rewardPositionsToReceiveLength = str(len(rewardPositionsToReceiveJustNumbers))

            try:
                int(rewardPositionsToReceiveJustNumbers)
            except:
                rewardsImageEmbed = discord.Embed(title='', color=openProjBlack)
                rewardsImageEmbed.set_image(url = 'https://i.postimg.cc/DwcTj1zc/rewards.jpg')
                embed = discord.Embed(title='',description='Please insert number/s seperated by commas into the **Leaderboard position/s to receive** field', color=openProjBlack)
                embedsList = [rewardsImageEmbed, embed]
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = views.managerRewardsGoBack())
                return
            
            try:
                int(percentage)
            except:
                rewardsImageEmbed = discord.Embed(title='', color=openProjBlack)
                rewardsImageEmbed.set_image(url = 'https://i.postimg.cc/DwcTj1zc/rewards.jpg')
                embed = discord.Embed(title='',description='You must insert a number into the **Percent of Pool** field', color=openProjBlack)
                embedsList = [rewardsImageEmbed, embed]
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = views.managerRewardsGoBack())
                return
            

            totalPoolAllocated = await botFunctions.getTotalPoolAlocated(interaction.guild)
            newtotalPoolAllocated = int(percentage) * int(rewardPositionsToReceiveLength) + totalPoolAllocated
                
            if newtotalPoolAllocated > 100:
                rewardsImageEmbed = discord.Embed(title='', color=openProjBlack)
                rewardsImageEmbed.set_image(url = 'https://i.postimg.cc/DwcTj1zc/rewards.jpg')
                embed = discord.Embed(title='',description='This allocation will exceed the total maximum allocation of 100% of the Entrants Fees and is not allowed', color=openProjBlack)
                embedsList = [rewardsImageEmbed, embed]
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = views.managerRewardsGoBack())
                return
                
            
            rewardPositionsToReceiveList = rewardPositionsToReceive.split(',')
            rewardPositionsToReceiveList = [int(num) for num in rewardPositionsToReceiveList]  # Convert the strings to integers if needed
        
            rewardImageUrl =  'https://i.postimg.cc/52gsFF6b/matic-coins2.png'      
            rewardName = percentage + '% of Entrants Pool Matic'
            rewardPositionsString = await botFunctions.getRewardPositionsString(rewardPositionsToReceiveList)
            rewardDescription = str(rewardPositionsString) + ' will be sent the Matic on end of Contest'


            leaderboardPositionToReceive = await botFunctions.getServerDictValue(interaction.guild.id, 'leaderboardPositionToReceive')
            rewardNames = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardNames')
            rewardDescriptions = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardDescriptions')
            rewardAmountToGiveaway = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardAmountToGiveaway')
            rewardDistributions = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardDistributions')
            rewardImageUrls = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardImageUrls')
            poolPercents = await botFunctions.getServerDictValue(interaction.guild.id, 'poolPercents')
            rewardTypes = await botFunctions.getServerDictValue(interaction.guild.id, 'rewardTypes')


            leaderboardPositionToReceive.append(rewardPositionsToReceiveList)
            rewardNames.append(rewardName)
            rewardDescriptions.append(rewardDescription)
            rewardAmountToGiveaway.append(rewardPositionsToReceiveLength)
            rewardDistributions.append('0')
            rewardImageUrls.append(rewardImageUrl)
            rewardTypes.append('pool')
            poolPercents.append(percentage)


            await botFunctions.setServerDictValue(interaction.guild.id, 'leaderboardPositionToReceive', leaderboardPositionToReceive)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardNames', rewardNames)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardDescriptions', rewardDescriptions)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardAmountToGiveaway', rewardAmountToGiveaway)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardDistributions', rewardDistributions)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardImageUrls', rewardImageUrls)
            await botFunctions.setServerDictValue(interaction.guild.id, 'poolPercents', poolPercents)
            await botFunctions.setServerDictValue(interaction.guild.id, 'rewardTypes', rewardTypes)


            menuStatus = await botFunctions.getServerDictValue(interaction.guild.id, 'menuStatus')
            if menuStatus == 'tokenConfig-rewards' and newtotalPoolAllocated == 100:
                await botFunctions.setServerDictValue(interaction.guild.id, 'menuStatus', 'tokenConfig-EnableATask')

            participationMode = await botFunctions.getServerDictValue(interaction.guild.id, 'participationMode')
            if participationMode == 'free':
                await botFunctions.generateManagerRewardsMenu(interaction, 'edit')
            if participationMode == 'fee':
                await botFunctions.generateManagerFeeRewardsMenu(interaction, 'edit')


class addPoolAllocation(ui.Modal, title = "Add Pool Allocation"):

        percentage = ui.TextInput(label = "Percent of Pool", style = discord.TextStyle.short, placeholder = "10", required = True, max_length = 2)
        walletAddress = ui.TextInput(label = "Polygon Matic Wallet Address", style = discord.TextStyle.short, placeholder = "0xf48B3847936bB9cc96A3cFB0F01Eb1057cCFa349", required = True, max_length = 42)
 
        def __init__(self):
            super().__init__(custom_id = 'awdd213rfrwcawffq')

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True) 

            percentage = str(self.percentage) 
            walletAddress = str(self.walletAddress) 

            web3 = await botFunctions.getWeb3()
            if not web3.is_address(walletAddress):
                rewardsImageEmbed = discord.Embed(title='', color=openProjBlack)
                rewardsImageEmbed.set_image(url = 'https://i.postimg.cc/DwcTj1zc/rewards.jpg')
                embed = discord.Embed(title='',description='You did not insert a valid Polygon Matic address', color=openProjBlack)
                embedsList = [rewardsImageEmbed, embed]
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = views.managerRewardsGoBack())
                return

            if not web3.is_checksum_address(walletAddress): #checksum is correct format for addresses, they need capitalisation on certain letters, some people dont add
                walletAddress = web3.to_checksum_address(walletAddress)

            try:
                int(percentage)
            except:
                rewardsImageEmbed = discord.Embed(title='', color=openProjBlack)
                rewardsImageEmbed.set_image(url = 'https://i.postimg.cc/DwcTj1zc/rewards.jpg')
                embed = discord.Embed(title='',description='You must insert a number into the **Percent of Pool** field', color=openProjBlack)
                embedsList = [rewardsImageEmbed, embed]
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = views.managerRewardsGoBack())
                return

            
            totalPoolAllocated = await botFunctions.getTotalPoolAlocated(interaction.guild)
            newtotalPoolAllocated = int(percentage) + totalPoolAllocated
                
            if newtotalPoolAllocated > 100:
               
                rewardsImageEmbed = discord.Embed(title='', color=openProjBlack)
                rewardsImageEmbed.set_image(url = 'https://i.postimg.cc/DwcTj1zc/rewards.jpg')
                embed = discord.Embed(title='',description='This allocation will exceed the total maximum allocation of 100% of the Entrants Fees and is not allowed', color=openProjBlack)
                embedsList = [rewardsImageEmbed, embed]
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = views.managerRewardsGoBack())
                return
                

            await botFunctions.setServerDictValue(interaction.guild.id, 'poolAllocations', percentage, walletAddress)

            menuStatus = await botFunctions.getServerDictValue(interaction.guild.id, 'menuStatus')
            if menuStatus == 'tokenConfig-rewards' and newtotalPoolAllocated == 100:
                await botFunctions.setServerDictValue(interaction.guild.id, 'menuStatus', 'tokenConfig-EnableATask')
            
            participationMode = await botFunctions.getServerDictValue(interaction.guild.id, 'participationMode')
            if participationMode == 'free':
                await botFunctions.generateManagerRewardsMenu(interaction, 'edit')
            if participationMode == 'fee':
                await botFunctions.generateManagerFeeRewardsMenu(interaction, 'edit')



class tokenConfigTokenName(ui.Modal, title = "Insert Token Name"):

    input = ui.TextInput(label = "Token Name", style = discord.TextStyle.short, placeholder = "$Dabloon", required = True, max_length = 50)

    async def on_submit(self, interaction: discord.Interaction):
        await botFunctions.setServerDictValue(interaction.guild.id, 'tokenName', str(self.input))
        
        embed = await botFunctions.embedMaker('setTokenName', 'cyan')
        toolsImageEmbed = discord.Embed(title='', color=openProjBlack)
        toolsImageEmbed.set_image(url = 'https://i.postimg.cc/wTxDtwX3/tools.jpg')
        embedsList = [toolsImageEmbed, embed]
        
        await interaction.response.edit_message(embeds=embedsList)

        menuStatus = await botFunctions.getServerDictValue(interaction.guild.id, 'menuStatus')
        if menuStatus == 'tokenConfig-tokenName':
            await botFunctions.setServerDictValue(interaction.guild.id, 'menuStatus', 'tokenConfig-rewards')



class setServerDescription(ui.Modal, title = "Set Server Description"):

    input = ui.TextInput(label = "Server Description", style = discord.TextStyle.long, placeholder = "Bunny Bebes is a collection of 5000 Fantastic Furballs living on the Polygon blockchain!", required = True, max_length = 200)

    async def on_submit(self, interaction: discord.Interaction):
        await botFunctions.setServerDictValue(interaction.guild.id, 'serverDescription', str(self.input))
        
        embed = await botFunctions.embedMaker('setServerDescription', 'cyan')
        toolsImageEmbed = discord.Embed(title='', color=openProjBlack)
        toolsImageEmbed.set_image(url = 'https://i.postimg.cc/wTxDtwX3/tools.jpg')
        embedsList = [toolsImageEmbed, embed]
        
        await interaction.response.edit_message(embeds=embedsList)

class tokenConfigProjectTwitterHandle(ui.Modal, title = "Project Twitter Handle"):

    input = ui.TextInput(label = "Insert this project's Twitter Handle", style = discord.TextStyle.short, placeholder = "@BunnyBebesNFT", required = True, max_length = 50)

    async def on_submit(self, interaction: discord.Interaction):
        await botFunctions.setServerDictValue(interaction.guild.id, 'projectTwitterHandle', str(self.input))

        embed = await botFunctions.embedMaker('setProjectTwitterHandle', 'cyan')

        toolsImageEmbed = discord.Embed(title='', color=openProjBlack)
        toolsImageEmbed.set_image(url = 'https://i.postimg.cc/wTxDtwX3/tools.jpg')
        embedsList = [toolsImageEmbed, embed]

        await interaction.response.edit_message(embeds=embedsList)

        menuStatus = await botFunctions.getServerDictValue(interaction.guild.id, 'menuStatus')
        if menuStatus == 'tokenConfig-projectTwitterHandle':
            await botFunctions.setServerDictValue(interaction.guild.id, 'menuStatus', 'tokenConfig-EnableATask')




class enableTwitterShillModal(ui.Modal, title = "Enable Twitter Shill"):

    shillMessageInput = ui.TextInput(label = "Shill Message", style=discord.TextStyle.paragraph, placeholder = "Bunny Bebes is a collection of 5000...", required = True, max_length = 220)
    twitterHandleInput = ui.TextInput(label = "Projects Twitter Handle (Include @ Sign)", style = discord.TextStyle.short, placeholder = "@BunnyBebesNFT", required = True, max_length = 20)

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)  # Defer tells discord to wait for us to process and we'll followup

        listOfInputs = []
        listOfInputs.append(str(self.shillMessageInput))
        listOfInputs.append(str(self.twitterHandleInput))

        f = open("serverAccounts.txt")
        s = f.read()
        serverAccounts = json.loads(s)

        #Updating server account
        for account in serverAccounts:
            if str(interaction.guild.id) == str(serverAccounts[account]['serverId']):

                serverAccounts[account]['twitterShillTaskInputs'] = listOfInputs

                with open('serverAccounts.txt', 'w') as f:
                    json.dump(serverAccounts, f, indent=4)


       
        await botFunctions.enableTask(interaction)


class enableDiscordCollabModal(ui.Modal, title = "Enable Discord Collab"):

    templateInput = ui.TextInput(label = "Collab Template", style = discord.TextStyle.paragraph, placeholder = "Bunny Bebes is a collection of 5000...", required = True) #max 4000 chars, defaults to max
  
    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)  # Defer tells discord to wait for us to process and we'll followup

        f = open("serverAccounts.txt")
        s = f.read()
        serverAccounts = json.loads(s)

        #Updating server account
        for account in serverAccounts:
            if str(interaction.guild.id) == str(serverAccounts[account]['serverId']):
                serverAccounts[account]['discordCollabTaskInput'] = str(self.templateInput)

                s = json.dumps(serverAccounts)
                with open("serverAccounts.txt", "w") as f:
                    f.write(s)


        await botFunctions.enableTask(interaction)



class enableTwitterPostModal(ui.Modal, title = "Enable Twitter Post"):

    bodyInput = ui.TextInput(label = "Tweet Body", style = discord.TextStyle.paragraph, placeholder = "Bunny Bebes is a collection of 5000...", required = True, max_length = 220)
    handleInput = ui.TextInput(label = "Project Twitter Handle (Include @ Sign)", style=discord.TextStyle.short, placeholder = "@BunnyBebesNFT", required = True, max_length = 20)
    hashtagsInput = ui.TextInput(label = "Project Hashtags (Seperated by spaces)", style = discord.TextStyle.short, placeholder = "#NFT #NFTCommunity #NFTGiveaway", required = True, max_length = 40)

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)  # Defer tells discord to wait for us to process and we'll followup

        listOfInputs = []
        listOfInputs.append(str(self.bodyInput))
        listOfInputs.append(str(self.handleInput))
        listOfInputs.append(str(self.hashtagsInput))

        f = open("serverAccounts.txt")
        s = f.read()
        serverAccounts = json.loads(s)

        #Updating server account
        for account in serverAccounts:
            if str(interaction.guild.id) == str(serverAccounts[account]['serverId']):

                serverAccounts[account]['twitterPostTaskInputs'] = listOfInputs


                with open('serverAccounts.txt', 'w') as f:
                    json.dump(serverAccounts, f, indent=4)


        await botFunctions.enableTask(interaction)


class enableDistributeFeedModal(ui.Modal, title = "Enable Distribute Feed"):

    channel_1 = ui.TextInput(label = "Channel 1 ID", style = discord.TextStyle.short, placeholder = "1091506452344082503", required = True, max_length = 19)
    channel_2 = ui.TextInput(label = "Channel 2 ID (Optional)", style = discord.TextStyle.short, placeholder = "1091506452344082503", required = False, max_length = 19)
   
    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)  # Defer tells discord to wait for us to process and we'll followup

        f = open("serverAccounts.txt")
        s = f.read()
        dict3 = json.loads(s)

        #Verifying submitted channel IDs:
        enabledChannels1 = []
        enabledChannels2 = []
        enabledChannels3 = [] 
        enabledChannels4 = []

        enabledChannels1.append(self.channel_1)
        enabledChannels1.append(self.channel_2)

        for item in enabledChannels1:
            if len(str(item)) > 0: #Discarding empty fields
                enabledChannels2.append(item.value)

        for item in enabledChannels2:

            errorMessage1 = 'Task Enable Failed'
            errorMessage2 = 'Provided Channel ID **' + str(item) + '** is not a channel ID\nPlease ensure all inserted channel IDs are correct and try again'
            errorEmbed = discord.Embed(title=errorMessage1, description=errorMessage2, color=openProjBlack)
            errorEmbed.set_thumbnail(url = "https://i.postimg.cc/vBQtrmxv/X-Circle-512-1974688460.png")

            #Making sure only numbers
            try:
                int(item)
            except:
                await interaction.followup.send(embed = errorEmbed, ephemeral = True)
                return

            #Making sure provided id points to channel
            channel = interaction.client.get_channel(int(item))
            if str(channel) == 'None':
                await interaction.followup.send(embed = errorEmbed, ephemeral = True) 
                return
            else:
                enabledChannels3.append(channel.id)
                enabledChannels4.append(channel)

            #Testing if bot has submitted channel permissions
            try:
                embed = await embeds.testEmbed()
                testingEmbed = await channel.send(embed = embed)
                await testingEmbed.delete()

            except:
                errorMessage1 = 'Task Enable Failed'
                errorMessage2 = 'OpenProjBot is not able to send embed message to **' + str(channel.name) + '**\nPlease enable **Send Messages, View Channel, Embed Links and Read Message History** permissions for OpenProjBot and try again.'
                errorEmbed = discord.Embed(title=errorMessage1, description=errorMessage2, color=openProjBlack)
                errorEmbed.set_thumbnail(url = "https://i.postimg.cc/vBQtrmxv/X-Circle-512-1974688460.png")
                await interaction.followup.send(embed = errorEmbed, ephemeral = True) 
                return

        #Updating server account
        for account in dict3:
            if str(interaction.guild.id) == str(dict3[account]['serverId']):

                dict3[account]['isDistributeFeedEnabled'] = 'True'
                dict3[account]['distributeFeedChannels'] = enabledChannels3

                with open('serverAccounts.txt', 'w') as f:
                    json.dump(dict3, f, indent=4)

        
        await botFunctions.enableTask(interaction)



class enableNotificationsModal(ui.Modal, title = "Enable Notifications"):

    channel_1 = ui.TextInput(label = "Channel 1 ID", style = discord.TextStyle.short, placeholder = "1091506452344082503", required = True, max_length = 19)
   
    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)  # Defer tells discord to wait for us to process and we'll followup
        f = open("serverAccounts.txt")
        s = f.read()
        dict3 = json.loads(s)

        #Verifying submitted channel IDs:
        enabledChannels1 = []
        enabledChannels2 = []
        enabledChannels3 = [] 
        enabledChannels4 = []

        enabledChannels1.append(self.channel_1)

        for item in enabledChannels1:
            if len(str(item)) > 0: #Discarding empty fields
                enabledChannels2.append(item.value)

        for item in enabledChannels2:

            toolsImageEmbed = discord.Embed(title='', color=openProjBlack)
            toolsImageEmbed.set_image(url = 'https://i.postimg.cc/wTxDtwX3/tools.jpg')

            errorMessage1 = 'Notification Enable Failed'
            errorMessage2 = 'Provided Channel ID **' + str(item) + '** is not a channel ID\nPlease ensure inserted channel ID is correct and try again'
            errorEmbed = discord.Embed(title=errorMessage1, description=errorMessage2, color=openProjBlack)
            errorEmbed.set_thumbnail(url = "https://i.postimg.cc/vBQtrmxv/X-Circle-512-1974688460.png")

            list = [toolsImageEmbed, errorEmbed]


            #Making sure only numbers
            try:
                int(item)
            except:
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds = embedsList, view = views.goBackManagerToolsView())
                return

            #Making sure provided id points to channel
            channel = interaction.client.get_channel(int(item))
            if str(channel) == 'None':
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds = embedsList, view = views.goBackManagerToolsView())
                return
            else:
                enabledChannels3.append(channel.id)
                enabledChannels4.append(channel)

            #Testing if bot has submitted channel permissions
            try:
                embed = await embeds.testEmbed()
                testingEmbed = await channel.send(embed = embed)
                await testingEmbed.delete()

            except:
                errorMessage1 = 'Notification Enable Failed'
                errorMessage2 = 'OpenProjBot is not able to send message to **' + str(channel.name) + '**\nPlease enable **Send Messages, View Channel, Embed Links and Read Message History** permissions for OpenProjBot and try again.'
                errorEmbed = discord.Embed(title=errorMessage1, description=errorMessage2, color=openProjBlack)
                errorEmbed.set_thumbnail(url = "https://i.postimg.cc/vBQtrmxv/X-Circle-512-1974688460.png")
                embedsList = [toolsImageEmbed, errorEmbed]
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds = embedsList, view = views.goBackManagerToolsView())
                return

        #Updating server account
        for account in dict3:
            if str(interaction.guild.id) == str(dict3[account]['serverId']):

                dict3[account]['isNotificationEnabled']['Giveaway is live'] = 'True'
                dict3[account]['notificationChannels'] = enabledChannels3

                with open('serverAccounts.txt', 'w') as f:
                    json.dump(dict3, f, indent=4)

        embed = await botFunctions.embedMaker('notifications', 'cyan', interaction.guild)
        embedsList = [toolsImageEmbed, embed]
        await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList)


        embed = await embeds.giveawayNotifier(interaction.guild)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label = 'OpenProj Server', style = discord.ButtonStyle.link, url = 'https://discord.gg/9a8JRYuedF'))
        await botFunctions.enableRecurringNotification.start(embed, interaction, view)


        #await botFunctions.enableTask(interaction)
        


class enableChattingModal(ui.Modal, title = "Enable Chatting"):
    
    channel_1 = ui.TextInput(label = "Channel 1 ID", style = discord.TextStyle.short, placeholder = "1091506452344082503", required = True, max_length = 19)
    channel_2 = ui.TextInput(label = "Channel 2 ID (Optional)", style = discord.TextStyle.short, placeholder = "1091506452344082503", required = False, max_length = 19)
    channel_3 = ui.TextInput(label = "Channel 3 ID (Optional)", style = discord.TextStyle.short, placeholder = "1091506452344082503", required = False, max_length = 19)
    channel_4 = ui.TextInput(label = "Channel 4 ID (Optional)", style = discord.TextStyle.short, placeholder = "1091506452344082503", required = False, max_length = 19)
    channel_5 = ui.TextInput(label = "Channel 5 ID (Optional)", style = discord.TextStyle.short, placeholder = "1091506452344082503", required = False, max_length = 19)

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True) 

        f = open("serverAccounts.txt")
        s = f.read()
        dict3 = json.loads(s)

        chattingEnabledChannels1 = []
        chattingEnabledChannels2 = []
        chattingEnabledChannels3 = [] 
        chattingEnabledChannels4 = []

        chattingEnabledChannels1.append(self.channel_1)
        chattingEnabledChannels1.append(self.channel_2)
        chattingEnabledChannels1.append(self.channel_3)
        chattingEnabledChannels1.append(self.channel_4)
        chattingEnabledChannels1.append(self.channel_5)

        for item in chattingEnabledChannels1:
            if len(str(item)) > 0:
                chattingEnabledChannels2.append(item.value)

        for item in chattingEnabledChannels2:

            errorMessage1 = 'Task Enable Failed'
            errorMessage2 = 'Provided Channel ID **' + str(item) + '** is not a channel ID\nPlease ensure all inserted channel IDs are correct and try again'
            errorEmbed = discord.Embed(title=errorMessage1, description=errorMessage2, color=openProjBlack)
            errorEmbed.set_thumbnail(url = "https://i.postimg.cc/vBQtrmxv/X-Circle-512-1974688460.png")

            tasksImageEmbed = discord.Embed(title='', color=openProjBlack)
            tasksImageEmbed.set_image(url = 'https://i.postimg.cc/T1MCMgFg/tasks.jpg')

            embedsList = [tasksImageEmbed, errorEmbed]
            try:
                int(item)
            except:
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds = embedsList, view = views.goBackTaskView()) 
                return

            channel = interaction.client.get_channel(int(item))
            if str(channel) == 'None':
                await interaction.followup.edit_message(message_id = interaction.message.id, embeds = embedsList, view = views.goBackTaskView()) 
                return
            else:
                chattingEnabledChannels3.append(str(channel.id))
                chattingEnabledChannels4.append(channel)

            embed = await embeds.testEmbed()
            for channel in chattingEnabledChannels4:
                try:#Testing bot can send and read messages in this channel
                    testingEmbed = await channel.send(embed = embed)
                    await testingEmbed.delete()
                    messages = [message async for message in channel.history(oldest_first=False, limit=5)]


                except:
                    errorMessage1 = 'Chatting Task Enable Failed'
                    errorMessage2 = 'OpenProjBot is not able to read messages in **' + str(channel.name) + '**\nPlease enable **Send Messages, View Channel, Embed Links and Read Message History** permissions for OpenProjBot and try again.'
                    errorEmbed = discord.Embed(title=errorMessage1, description=errorMessage2, color=openProjBlack)
                    errorEmbed.set_thumbnail(url = "https://i.postimg.cc/vBQtrmxv/X-Circle-512-1974688460.png")
                    embedsList = [tasksImageEmbed, errorEmbed]
                    await interaction.followup.edit_message(message_id = interaction.message.id, embeds = embedsList, view = views.goBackTaskView())
                    return

                


        for account in dict3: # IF: Cannot send an empty message THEN TRY: Ensure server is in server accounts. Ensure you havent had multiple same name servers
            if str(interaction.guild.id) == str(dict3[account]['serverId']):
                dict3[account]['chattingEnabledChannels'] = chattingEnabledChannels3

                with open('serverAccounts.txt', 'w') as f:
                    json.dump(dict3, f, indent=4)

        await botFunctions.enableTask(interaction)



class setPaypalEmailModal(ui.Modal, title = "Set Paypal Email"):

    paypalEmail = ui.TextInput(label = "Earnings will be sent to this Paypal account", style = discord.TextStyle.short, required = True)

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)  
        
        paypalEmail = str(self.paypalEmail)
        await botFunctions.setServerDictValue(interaction.guild.id, 'paypalEmail', paypalEmail)
        await botFunctions.enableTask(interaction)


class setWalletAddressModal(ui.Modal, title = "Set Polygon Wallet Address"):

    walletAddress = ui.TextInput(label = "Wallet Address", style = discord.TextStyle.short, placeholder = "0x63C18042Ff056493c62bc74d04A32F03a5813798", required = True, max_length = 42, min_length = 42)

    def __init__(self, amount): #parse variables to modal

            self.amount = amount
            super().__init__(custom_id = '124134321313')


    async def on_submit(self, interaction: discord.Interaction):
        
        walletAddress = str(self.walletAddress)

        await interaction.response.defer(ephemeral=True)  # Defer tells discord to wait for us to process and we'll followup
            
        web3 = await botFunctions.getWeb3()
        if not web3.is_address(walletAddress):
            rewardsImageEmbed = discord.Embed(title='', color=openProjBlack)
            rewardsImageEmbed.set_image(url = 'https://i.postimg.cc/DwcTj1zc/rewards.jpg')
            embed = discord.Embed(title='',description='You did not insert a valid Polygon Matic address', color=openProjBlack)
            embedsList = [rewardsImageEmbed, embed]
            await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = views.managerRewardsGoBack())
            return

        if not web3.is_checksum_address(walletAddress): #checksum is correct format for addresses, they need capitalisation on certain letters, some people dont add
            walletAddress = web3.to_checksum_address(walletAddress)

        #API CALL
        
        embed = discord.Embed(title='Matic is being sent to you', description = '' , color=openProjBlack)
        embed.add_field(name='Status', value='pending', inline=False)
        embed.add_field(name='Transaction ID', value=transactionID, inline=False)

        imageEmbed = discord.Embed(title='', color=openProjBlack)
        imageEmbed.set_image(url = 'https://i.postimg.cc/DwcTj1zc/rewards.jpg')
        # imageEmbed.set_footer(text = guild.id)

        embedsList = [imageEmbed, embed]

        view = discord.ui.View(timeout=None)
        button = views.theButton(label="Refresh Status", custom_id='awdawd222d', style=discord.ButtonStyle.blurple)
        view.add_item(button)
        interaction.client.add_view(view)
        
        await interaction.followup.edit_message(message_id = interaction.message.id, embeds=embedsList, view = view)

        

        



class setTwitterHandle(ui.Modal, title = "Set Twitter Handle"):

    twitterHandle = ui.TextInput(label = "Insert handle you will use to complete tasks", style = discord.TextStyle.short, placeholder = "@elonmusk", required = True, max_length = 30)

    async def on_submit(self, interaction: discord.Interaction):
        
        twitterHandle = str(self.twitterHandle)

        await interaction.response.defer(ephemeral=True)
        
        if '@' in twitterHandle:
            twitterHandle = twitterHandle[1:]
        # try: #Twint is shit, just stopped working, causing errors
        #     c = twint.Config()
        #     c.Username = twitterHandle
        #     twint.run.Lookup(c)
        # except:
        #     embed = await embeds.invalidTwitterHandle()
        #     await interaction.followup.edit_message(message_id = interaction.message.id, embed=embed)
        #     return
        await botFunctions.setMemberDictValue(interaction.user.id, 'twitterHandle', twitterHandle)

        embed = await embeds.completedTwitterHandle()
        await interaction.followup.edit_message(message_id = interaction.message.id, embed=embed)

        tasksChannel = discord.utils.get(interaction.guild.text_channels, name='🌀｜tasks')
        phrases = ['Happy Contributing!', 'Welcome to the Family!', 'Check out **🌀｜info** to learn how to Contribute', 'If you have questions, ask!', 'Anybody can Contribute, check out **🌀｜marketing-tasks** to find you can do']
        randomPhrase = random.choice(phrases)

        successEmbed = discord.Embed(title="You've earned the Participant role!", description = 'Now you can begin doing Tasks!', color=openProjCyan) #Cannot refer to member/channel in title/footer field, appears as id numbers
        successEmbed.set_footer(text = 'This channel will self-destruct in 30 Seconds', icon_url=None)
        successEmbed.set_thumbnail(url = "https://i.postimg.cc/Gm8KFRFT/tick-gif.gif")
        await interaction.channel.send(embed = successEmbed)
        await asyncio.sleep(30)
        await interaction.channel.delete()

        # messages = [message async for message in interaction.channel.history(oldest_first=True)]
        # await messages[3].edit(view=views.enableTaskView())


class enableTwitterRaidModal(ui.Modal, title = "Enable Twitter Raid"):

    tweetURL1 = ui.TextInput(label = "Insert URL of Tweet you want raided", style = discord.TextStyle.short, placeholder = "https://twitter.com/BunnyBebesNFT/status/1651689876285161475", required = True)
    tweetURL2 = ui.TextInput(label = "Insert URL of Tweet you want raided", style = discord.TextStyle.short, placeholder = "https://twitter.com/BunnyBebesNFT/status/1651689876285161475", required = False)
    tweetURL3 = ui.TextInput(label = "Insert URL of Tweet you want raided", style = discord.TextStyle.short, placeholder = "https://twitter.com/BunnyBebesNFT/status/1651689876285161475", required = False)
    tweetURL4 = ui.TextInput(label = "Insert URL of Tweet you want raided", style = discord.TextStyle.short, placeholder = "https://twitter.com/BunnyBebesNFT/status/1651689876285161475", required = False)
    tweetURL5 = ui.TextInput(label = "Insert URL of Tweet you want raided", style = discord.TextStyle.short, placeholder = "https://twitter.com/BunnyBebesNFT/status/1651689876285161475", required = False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)  # Defer tells discord to wait for us to process and we'll followup

        listOfTweetURLs = []
        listOfTweetURLs.append(self.tweetURL1)
        listOfTweetURLs.append(self.tweetURL2)
        listOfTweetURLs.append(self.tweetURL3)
        listOfTweetURLs.append(self.tweetURL4)
        listOfTweetURLs.append(self.tweetURL5)

        listOfTweetURLs2 = []

        for item in listOfTweetURLs:
            if len(str(item)) > 0:
                listOfTweetURLs2.append(item.value)

        await botFunctions.setServerDictValue(interaction.guild.id, 'Twitter Raid', listOfTweetURLs2, 'twitterRaidURLs')
        await botFunctions.enableTask(interaction)

        #await botFunctions.enableRecurringNotification.start(embed, interaction)


class createTaskModal(ui.Modal, title = "Create Task"):

    taskType = ui.TextInput(label = "Task Type (marketing or other)", style = discord.TextStyle.short, placeholder = "other", required = True, max_length = 9)
    taskTitle = ui.TextInput(label = "Task Title", style = discord.TextStyle.short, placeholder = "Art Contest!", required = True, max_length = 30)
    dollarReward = ui.TextInput(label = "Dollar Reward", style = discord.TextStyle.short, placeholder = "1.99", required = True, max_length = 7)
    description = ui.TextInput(label = "Task Description", style = discord.TextStyle.short, placeholder = "Best portrait of me wins!", required = True, max_length = 80)
    # maxThreads = ui.TextInput(label = "Max Threads", style = discord.TextStyle.short, placeholder = "1", required = True, max_length = 2)
    thumbnailUrl = ui.TextInput(label = "Thumbnail URL", style = discord.TextStyle.short, placeholder = "https://i.postimg.cc/Rh1QmQ2b/BB-ON.png", required = False, max_length = 100)


    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)  # Defer tells discord to wait for us to process and we'll followup

        await botFunctions.taskEnableChecks(interaction)

        errorMessage1 = 'Task Creation Failed'

        errorMessage2 = 'Provided Task Type **' + str(self.taskType) + '** is not acceptable\nPlease ensure inserted Task Type is either **other** or **marketing**'
        errorEmbed1 = discord.Embed(title=errorMessage1, description=errorMessage2, color=openProjBlack)
        errorEmbed1.set_thumbnail(url = "https://i.postimg.cc/vBQtrmxv/X-Circle-512-1974688460.png")

        errorMessage3 = 'Provided Dollar Reward **' + str(self.dollarReward) + '** is not acceptable"'
        errorEmbed2 = discord.Embed(title=errorMessage1, description=errorMessage3, color=openProjBlack)
        errorEmbed2.set_thumbnail(url = "https://i.postimg.cc/vBQtrmxv/X-Circle-512-1974688460.png")

        list = []
        list.append('marketing')
        list.append('other')

        if str(self.taskType.value) not in list:
            await interaction.followup.send(embed = errorEmbed1, ephemeral = True)
            return

        if str(self.taskType.value) == 'marketing':
            taskChannel = discord.utils.get(interaction.guild.text_channels, name='🌀｜marketing-tasks')

        if str(self.taskType.value) == 'other':
            taskChannel = discord.utils.get(interaction.guild.text_channels, name='🌀｜other-tasks')

        try:
            float(self.dollarReward.value)
        except:
            
            await interaction.followup.send(embed = errorEmbed2, ephemeral = True)
            return

        
        messages = [message async for message in taskChannel.history(oldest_first=True)]

        
        #Creating Task Embed
        newEmbed = discord.Embed(title=str(self.taskTitle), color=openProjCyan)
        newEmbed.add_field(name="Reward", value=str('$'+str(self.dollarReward)), inline=False)
        newEmbed.add_field(name="Task Description", value=str(self.description), inline=False)
        newEmbed.add_field(name="Task Creator", value=str(interaction.user.name), inline=False)
        newEmbed.add_field(name="Thread Count", value='0/1', inline=False)
        newEmbed.add_field(name="Thread Links", value="", inline=False)

        messageEmbeds = messages[0].embeds # return list of embeds
        
        #Check that thumbnail_url points to valid image, else use default image
        if 'https://' in str(self.thumbnailUrl):
            image_formats = ("image/png", "image/jpeg", "image/jpg")
            r = requests.head(str(self.thumbnailUrl))
            if r.headers["content-type"] in image_formats:
                newEmbed.set_thumbnail(url = str(self.thumbnailUrl))
            else:
                newEmbed.set_thumbnail(url = 'https://i.postimg.cc/3J6fTPp9/open-Proj-Logo-smaller.png')

        else:
            newEmbed.set_thumbnail(url = 'https://i.postimg.cc/3J6fTPp9/open-Proj-Logo-smaller.png')

        messageEmbeds.append(newEmbed)
        await messages[0].edit(embeds = messageEmbeds, content='')
        
        newTaskEmbed = discord.Embed(title=str(self.taskTitle), description=str(self.description), color=openProjCyan)
        newTaskEmbed.set_author(name = 'Task Enabled', icon_url='https://i.postimg.cc/Rh1QmQ2b/BB-ON.png')     
        await interaction.channel.send(embed=newTaskEmbed,view=views.disableGoBackTaskView())

        successMessage1 = 'Task Creation Success'
        successMessage2 = '<#' + str(taskChannel.id) + '>'
        successEmbed = discord.Embed(title=successMessage1, description=successMessage2, color=openProjCyan)
        successEmbed.set_thumbnail(url = "https://i.postimg.cc/Gm8KFRFT/tick-gif.gif")
        await interaction.followup.send('', embed=successEmbed, ephemeral = True)

