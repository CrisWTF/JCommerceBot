from discord import Option, OptionChoice, Embed, slash_command, Colour, SlashCommandGroup  #Option(type[value]) se le pone a los argumentos dentro del comando para definir el tipo de valor
from discord.ext.commands import Cog, has_role, cooldown, BucketType
from discord.ext import tasks
from src.utils import collection_users, discount, groupPayment, vipPayment, find_all
from src.Views import modals, selects
import requests
import datetime

SELLER_ROLE_ID = 977025090313142322
BUYER_ROLE_ID = 981616570876969080
MEMBER_ROLE_ID = 977023989035720755
GUILD_ID = 976734513000493077

async def delete_history(ctx, bot_id):
    user = ctx.interaction.user
    dm_channel = user.dm_channel
    if dm_channel == None:
        dm_channel = await user.create_dm()
    async for message in dm_channel.history(limit=None):
        if message.author.id == bot_id:
            await message.delete()

class seller_commands(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.check_tokens.start()

    shop_group = SlashCommandGroup(name='shop',description='Commands for buyers and sellers', guild_only=True)
    channel_subgroup = shop_group.create_subgroup('edit', description='Commands for edit your channel')

    @tasks.loop()
    async def check_tokens(self):
        users = await find_all()
        if users:
            for user in users:
                token_seller = user['token_seller'] if user['token_seller'] else None
                shop = user['shop'] if user['shop'] else None
                token_buyer = user['token_buyer'] if user['token_buyer'] else None
                buyer_channel = user['buyer_channel'] if user['buyer_channel'] else None
                if not buyer_channel and not shop:
                    guild = await self.bot.fetch_guild(GUILD_ID)
                    member = None
                    try:
                        member = await guild.fetch_member(int(user['id']))
                    except:
                        collection_users.delete_one({'id': user['id']})
                if token_seller:
                    guild = await self.bot.fetch_guild(GUILD_ID)
                    member = None
                    try:
                        member = await guild.fetch_member(int(user['id']))
                    except:
                        continue
                    if user['payment_seller']['new'] >=  int(user['payment_seller']['price']):
                        seller_role = guild.get_role(SELLER_ROLE_ID)
                        days = None
                        hour = None
                        if user['payment_seller']['price'] == '0':
                            hour = 1
                        elif user['payment_seller']['price'] == '60':
                            days = 3
                        elif user['payment_seller']['price'] == '120':
                            days = 7
                        elif user['payment_seller']['price'] == '400':
                            days = 30
                        elif user['payment_seller']['price'] == '25':
                            days = 1
                        #Aquí envía un embed si el pago es correcto y aquí crea la shop y borra el tokken seller
                        if user['shop']:
                            embed = Embed(
                                title='Shop',
                                description=f'Your payment has been successful\nYou have added **{days}** days to your shop',
                                color=Colour.blue()
                            )
                            collection_users.update_one({'id':user['id']},{'$set':{'token_seller': None, 'shop.finish': user['shop']['finish'] + datetime.timedelta(days=days), 'payment_seller': None}})
                            await member.send(embed=embed)
                        else:
                            embed = Embed(
                                title='Shop',
                                description='Your payment has been successful, now you can use "/shop edit"\nto edit your shop',
                                color=Colour.blue()
                            )
                            if days != None:
                                collection_users.update_one({'id':user['id']},{'$set':{'token_seller': None, 'shop': {'channel':{'id':None, 'messages': [None,None,None,None,None]},'created':datetime.datetime.now(),'finish':datetime.datetime.now()+datetime.timedelta(days=days)}, 'payment_seller': None, 'clients':[]}})
                            else:
                                collection_users.update_one({'id':user['id']},{'$set':{'token_seller': None, 'shop': {'channel':{'id':None, 'messages': [None,None,None,None,None]},'created':datetime.datetime.now(),'finish':datetime.datetime.now()+datetime.timedelta(hours=hour)}, 'payment_seller': None, 'clients':[]}})
                            await member.add_roles(seller_role)
                            await member.send(embed=embed)
                    if datetime.datetime.now() > token_seller['finish']:
                        embed = Embed(
                                title='Key',
                                description='Your **key** has expired',
                                color=Colour.blue()
                            )
                        collection_users.update_one({'id':user['id']},{'$set':{'token_seller':None, 'payment_seller':None}})
                        await member.send(embed=embed)
                if shop:
                    member = None
                    guild = await self.bot.fetch_guild(GUILD_ID)
                    seller_role = guild.get_role(SELLER_ROLE_ID)
                    if datetime.datetime.now() > shop['finish']:
                        embed = Embed(
                                title='Shop',
                                description='Your **shop** has expired',
                                color=Colour.blue()
                            )
                        collection_users.update_one({'id':user['id']},{'$set':{'shop':None}})
                        await member.remove_roles(seller_role)
                        channel = await guild.fetch_channel(user['shop']['channel']['id'])
                        if channel:
                            await channel.delete()
                        await member.send(embed=embed)
                    try:
                        member = await guild.fetch_member(int(user['id']))
                    except:
                        continue
                    has_seller_role = False
                    for role in member.roles:
                        if role.id == SELLER_ROLE_ID:
                            has_seller_role = True
                            break
                    if not has_seller_role:
                        await member.add_roles(seller_role)
                if token_buyer:
                    try:
                        guild = await self.bot.fetch_guild(GUILD_ID)
                        channel = await guild.fetch_channel(user['buyer_channel'])
                        if user['payment_buyer']['new'] >=  int(user['payment_buyer']['price']):
                            embed = Embed(
                                    title='Purchase',
                                    description='The payment has been successful, now you can trade safely',
                                    color=Colour.blue()
                                )
                            collection_users.update_one({'id':user['id']},{'$set':{'token_buyer': None, 'payment_buyer': None, 'balance.pending':int(user['balance']['pending'] + int(discount(int(user['payment_buyer']['price']))))}})
                            await channel.send(embed=embed)
                        if datetime.datetime.now() > token_buyer['finish']:
                            embed = Embed(
                                    title='Key',
                                    description='The **key** has expired',
                                    color=Colour.blue()
                                )
                            collection_users.update_one({'id':user['id']},{'$set':{'token_buyer':None, 'payment_buyer':None}})
                            await channel.send(embed=embed)
                    except:
                        pass

    @slash_command(description='Verify your account for buy or sell', guild_only=True)
    async def verify(self,ctx):
        #Delete the current messages on dm
        await delete_history(ctx,self.bot.user.id)
        
        await ctx.interaction.response.send_modal(modals.Verify_Modal(title='Verify Roblox Account'))

    @slash_command(description='A brief description of your data', guild_only=True)
    @has_role('Buyer')
    async def current(self,ctx):
        #Delete the current messages on dm
        await delete_history(ctx,self.bot.user.id)
        user = None
        try:
            user = collection_users.find_one({'id': str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        if user:
            response = requests.get("https://games.roblox.com/v1/games", params=f'universeIds={user["universe_id"]}', headers={'Content-Type': 'application/json'})
            place_id = response.json()['data'][0]['rootPlaceId']
            roblox_name = response.json()['data'][0]['creator']['name']
            roblox_id = response.json()['data'][0]['creator']['id']
            response = requests.get(f'https://thumbnails.roblox.com/v1/users/avatar?userIds={str(roblox_id)}&size=250x250&format=Png&isCircular=false')
            image = response.json()['data'][0]['imageUrl']
            embed = Embed(
                title='Current Data',
                description='A representation of your data',
                color=Colour.blue()
            )
            embed.add_field(name='Roblox User', value=f'[{roblox_name}](https://www.roblox.com/users/{roblox_id}/profile)', inline=False)
            embed.add_field(name='Place ID', value=str(place_id), inline=False)
            embed.add_field(name='Balance', value=str(int(user['balance']['current'])), inline=False)
            has_shop = user['shop']
            if has_shop:
                if has_shop['channel']['id']:
                    guild = ctx.interaction.guild
                    channel_user = await guild.fetch_channel(has_shop['channel']['id'])
                    embed.add_field(name='Shop', value=f'Name: *{str(channel_user)}*\nCreated: *{user["shop"]["created"].strftime("%Y-%B-%d %H:%M")}*\nFinish Date: *{user["shop"]["finish"].strftime("%Y-%B-%d %H:%M")}*', inline=False)
                else:
                    embed.add_field(name='Shop', value=f'Name: *None*\nCreated: *{user["shop"]["created"].strftime("%Y-%B-%d %H:%M")}*\nFinish Date: *{user["shop"]["finish"].strftime("%Y-%B-%d %H:%M")}*', inline=False)
            else:
                embed.add_field(name='Shop', value='None')
            embed.set_image(url=image)
            embed.set_footer(text='You can use "/verify" to update your data')
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, check your dm', delete_after=3.0, ephemeral=True)
            await ctx.interaction.user.send(embed=embed)
        else:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you have not current data, use "/verify" to create one', delete_after=3.0, ephemeral=True)
            

    @shop_group.command(description='Create a shop')
    @has_role('Buyer')
    async def create(self, ctx):
        #Delete the current messages on dm
        await delete_history(ctx,self.bot.user.id)
        user = None
        try:
            user = collection_users.find_one({'id':str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        if user:
            shop = user['shop']
            if shop:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you already have a shop', delete_after=3.0, ephemeral=True)
            else:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, check your dm', delete_after=3.0, ephemeral=True)
                await ctx.interaction.user.send(view=selects.Slots_Option())
        else:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you have not current data, use "/verify" to create one', delete_after=3.0, ephemeral=True)

    @shop_group.command(description='Upgrade the days for you shop')
    @has_role('Seller')
    async def upgrade(self, ctx):
        #Delete the current messages on dm
        await delete_history(ctx,self.bot.user.id)
        user = None
        try:
            user = collection_users.find_one({'id':str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        if user:
            shop = user['shop']
            if shop:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, check your dm', delete_after=3.0, ephemeral=True)
                await ctx.interaction.user.send(view=selects.Slots_Upgrade())
            else:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you have not a shop, use "/shop create" to create one', delete_after=3.0, ephemeral=True)
        else:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you have not current data, use "/verify" to create one', delete_after=3.0, ephemeral=True)
            
    @channel_subgroup.command(description='Change the name of your channel')
    @has_role('Seller')
    @cooldown(1,900,BucketType.user)
    async def name(self,ctx):
        await delete_history(ctx,self.bot.user.id)
        await ctx.interaction.response.send_modal(modals.Change_Name(title='Channel Name'))

    @channel_subgroup.command(description='Change the messages from your channel')
    @has_role('Seller')
    async def messages(self,ctx, slot: Option(str, 'Choose the slot to modify', required=True, choices=[OptionChoice(name='Slot 1', value=str(0)),OptionChoice(name='Slot 2', value=str(1)),OptionChoice(name='Slot 3', value=str(2)),OptionChoice(name='Slot 4', value=str(3)),OptionChoice(name='Slot 5', value=str(4))])):
        await delete_history(ctx,self.bot.user.id)
        user = None
        try:
            user = collection_users.find_one({'id':str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        channel = user['shop']['channel']
        if not channel['id']:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you must create your channel using "/shop edit name"', delete_after=3.0, ephemeral=True)
        else:
            await ctx.interaction.response.send_modal(modals.Slot(slot, title='Message'))

    @shop_group.command(description='Delete a message from your channel')
    @has_role('Seller')
    async def delete(self,ctx,slot: Option(str, 'Choose the slot to modify', required=True, choices=[OptionChoice(name='Slot 1', value=str(0)),OptionChoice(name='Slot 2', value=str(1)),OptionChoice(name='Slot 3', value=str(2)),OptionChoice(name='Slot 4', value=str(3)),OptionChoice(name='Slot 5', value=str(4))])):
        await delete_history(ctx,self.bot.user.id)
        user = None
        try:
            user = collection_users.find_one({'id':str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        channel = user['shop']['channel']
        guild = ctx.interaction.guild
        if not channel['id']:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you must create your channel using "/shop edit name"', delete_after=3.0, ephemeral=True)
        else:
            if not channel['messages'][int(slot)]:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you do not have a message in this slot"', delete_after=3.0, ephemeral=True)
            else:
                channel_user = await guild.fetch_channel(channel['id'])
                message = await channel_user.fetch_message(channel['messages'][int(slot)])
                await message.delete()
                collection_users.update_one({'id':str(ctx.interaction.user.id)},{'$set':{f'shop.channel.messages.{int(slot)}':None}})
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, your message has been deleted successfully', delete_after=3.0, ephemeral=True)
    
    @shop_group.command(description='Remove your channel')
    @has_role('Seller')
    async def remove(self,ctx):
        await delete_history(ctx,self.bot.user.id)
        user = None
        try:
            user = collection_users.find_one({'id':str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        channel = user['shop']['channel']
        guild = ctx.interaction.guild
        if not channel['id']:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you do not have a channel"', delete_after=3.0, ephemeral=True)
        else:
            channel_user = await guild.fetch_channel(channel['id'])
            await channel_user.delete()
            collection_users.update_one({'id':str(ctx.interaction.user.id)},{'$set':{f'shop.channel.id':None, 'shop.channel.messages': [None,None,None,None,None]}})
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, your channel has been removed successfully', delete_after=3.0, ephemeral=True)

    @slash_command(description='Create a key', guild_only=True)
    @has_role('Seller')
    async def create_key(self, ctx, price: Option(int,'The price of the product')):
        channel = ctx.interaction.channel
        seller = None
        try:
            seller = collection_users.find_one({'id':str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        buyer = None
        buyer_mongo = None
        onChannel = False
        for client in seller['clients']:
            if int(client['channel_id']) == channel.id:
                buyer = await self.bot.fetch_user(int(client['buyer_id']))
                buyer_mongo = collection_users.find_one({'id': client['buyer_id']})
                onChannel = True
        if onChannel:
            if buyer_mongo['token_buyer']:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you already created a key', delete_after=3.0, ephemeral=True)
            else:
                key = f'{price}-{buyer.id}-buyer'
                embed = Embed(
                    title='Key',
                    description=f'The buyer key is **{key}**, pls introduce it into the game to buy the purchase',
                    color=Colour.blue()
                )
                embed.add_field(name='Game',value='[link](https://www.roblox.com/games/9906346613/JCommerce)')
                embed.set_footer(text='You just have one day to introduce your "key". Pay in that time, there will be no refunds')
                collection_users.update_one({'id':str(buyer.id)},{'$set':{'token_buyer':{'token':key,'created':datetime.datetime.now(),'finish':datetime.datetime.now()+datetime.timedelta(days=1.0)}, 'payment_buyer':{'price':str(price),'old': 0, 'new': 0}}})
                await channel.send(embed=embed)
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you have created a key', delete_after=3.0, ephemeral=True)
        else:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you must to use it on a buyer channel', delete_after=3.0, ephemeral=True)

    @slash_command(description='Cancel a key already created', guild_only=True)
    @has_role('Seller')
    async def cancel_key(self, ctx):
        channel = ctx.interaction.channel
        seller = None
        try:
            seller = collection_users.find_one({'id':str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        buyer = None
        buyer_mongo = None
        onChannel = False
        for client in seller['clients']:
            if int(client['channel_id']) == channel.id:
                buyer = await self.bot.fetch_user(int(client['buyer_id']))
                buyer_mongo = collection_users.find_one({'id': client['buyer_id']})
                onChannel = True
        if onChannel:
            if not buyer_mongo['token_buyer']:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you have not created a key', delete_after=3.0, ephemeral=True)
            else:
                embed = Embed(
                    title='Key',
                    description=f'The **buyer key** has been canceled',
                    color=Colour.blue()
                )
                if buyer_mongo['payment_buyer']:
                    if int(buyer_mongo['payment_buyer']['new']) > 0:
                        collection_users.update_one({'id':str(buyer.id)},{'$set':{'balance.current': buyer_mongo['balance']['current'] + int(discount(int(buyer_mongo['payment_buyer']['new'])))}})
                        embed.add_field(name='Robux', value=f'**{int(discount(int(buyer_mongo["payment_buyer"]["new"])))}** has been deposited in the **balance** of the buyer', inline=False)
                        embed.set_footer(text='Take into account the 30 percent of roblox', icon_url='')
                collection_users.update_one({'id':str(buyer.id)},{'$set':{'token_buyer':None, 'payment_buyer':None}})
                await channel.send(embed=embed)
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you have canceled a key', delete_after=3.0, ephemeral=True)
        else:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you must to use it on a buyer channel', delete_after=3.0, ephemeral=True)

    @slash_command(description='Confirm a purchase', guild_only=True)
    @has_role('Buyer')
    async def confirm(self, ctx):
        channel = ctx.interaction.channel
        user = None
        try:
            user = collection_users.find_one({'id':str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        buyer = None
        seller = None
        try:
            if user['buyer_channel']:
                if int(user['buyer_channel']) == channel.id:
                    buyer = user
                    users = collection_users.find()
                    for user in users:
                        try:
                            if user['clients']:
                                for client in user['clients']:
                                    if int(client['channel_id']) == channel.id:
                                        seller = user
                                        break
                                break
                        except:
                            continue
                    if buyer['balance']['pending'] > 0:
                        if not buyer['token_buyer']:
                            collection_users.update_one({'id':seller['id']},{'$set':{'balance.current': seller['balance']['current'] + buyer['balance']['pending']}})
                            collection_users.update_one({'id':buyer['id']},{'$set':{'balance.pending': 0}})
                            embed = Embed(
                                title='Key',
                                description=f'The payment has been confirmed.\n**{int(buyer["balance"]["pending"])}** has been deposited in the **balance** of the seller.',
                                color=Colour.blue()
                            )
                            embed.set_footer(text='Take into account the 30 percent of roblox', icon_url='')
                            await channel.send(embed=embed)
                            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you have confirmed a payment', delete_after=3.0, ephemeral=True)
                        else:
                            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you need to complete the payment or the seller have to use "/cancel_key"', delete_after=3.0, ephemeral=True)
                    else:
                        await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you do not have a pending payment', delete_after=3.0, ephemeral=True)
                else:
                    await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you can not use it here', delete_after=3.0, ephemeral=True)
            else:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you do not have a purchase channel', delete_after=3.0, ephemeral=True)
        except:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you do not have a purchase channel', delete_after=3.0, ephemeral=True)

    @slash_command(description='Close a purchase channel', guild_only=True)
    @has_role('Buyer')
    async def close(self, ctx):
        channel = ctx.interaction.channel
        user = None
        try:
            user = collection_users.find_one({'id':str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        buyer = None
        seller = None
        position_client = 0
        if user['buyer_channel']:
            if int(user['buyer_channel']) == channel.id:
                buyer = user
                users = await find_all()
                if users:
                    for user in users:
                        try:
                            if user['clients']:
                                for client in user['clients']:
                                    if int(client['channel_id']) == channel.id:
                                        seller = user
                                        break
                                    position_client += 1
                                break
                        except:
                            continue
                else:
                    await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True) 
                if buyer['balance']['pending'] == 0 and not buyer['token_buyer']:
                    seller_member = await self.bot.fetch_user(int(seller['id']))
                    embed = Embed(
                        title='Purchase',
                        description=f'The buyer channel **{channel.name}** has been closed.',
                        color=Colour.blue()
                    )
                    collection_users.update_one({'id':buyer['id']},{'$set':{'buyer_channel':None, 'webhook':None}})
                    collection_users.update_one({'id':seller['id']},{'$pull':{f'clients':{'channel_id':str(channel.id)}}})
                    await channel.delete()
                    await seller_member.send(embed=embed)
                    await ctx.interaction.user.send(embed=embed)
                else:
                    await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you must to complete/confirm the payment or call a moderator to close it and get your robux back', delete_after=3.0, ephemeral=True)
            else:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you can not use it here', delete_after=3.0, ephemeral=True)
        else:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you do not have a purchase channel', delete_after=3.0, ephemeral=True)
        if not buyer:
            if user['clients']:
                onChannel = False
                for client in user['clients']:
                    if int(client['channel_id']) == channel.id:
                        buyer = collection_users.find_one({'id':client['buyer_id']})
                        seller = user
                        onChannel = True
                        break
                    position_client += 1
                if onChannel:
                    buyer_member = await self.bot.fetch_user(int(buyer['id']))
                    embed = Embed(
                        title='Purchase',
                        description=f'The buyer channel **{channel.name}** has been closed.',
                        color=Colour.blue()
                    )   
                    collection_users.update_one({'id':seller['id']},{'$pull':{f'clients':{'channel_id':str(channel.id)}}})
                    amount = 0
                    if buyer['payment_buyer']:
                        if buyer['payment_buyer']['new'] > 0:
                            amount += int(discount(buyer["payment_buyer"]["new"]))
                            collection_users.update_one({'id':buyer['id']},{'$set':{'balance.current': buyer['balance']['current'] + int(discount(buyer["payment_buyer"]["new"])), 'token_buyer': None, 'payment_buyer':None, 'buyer_channel':None, 'webhook':None}})
                        else:
                            collection_users.update_one({'id':buyer['id']},{'$set':{'token_buyer': None, 'payment_buyer':None, 'buyer_channel':None, 'webhook':None}})
                    else:
                        collection_users.update_one({'id':buyer['id']},{'$set':{'buyer_channel':None, 'webhook':None}})
                    if buyer['balance']['pending'] > 0:
                        amount += buyer['balance']['pending']
                        collection_users.update_one({'id':buyer['id']},{'$set':{'balance.current': buyer['balance']['current'] + buyer['balance']['pending'], 'balance.pending': 0}})
                    await channel.delete()
                    await ctx.interaction.user.send(embed=embed)
                    if amount > 0:
                        embed.add_field(name='Robux', value=f'**{int(amount)}** has been deposited in your **balance**', inline=False)
                        embed.set_footer(text='Take into account the 30 percent of roblox', icon_url='')
                        await buyer_member.send(embed=embed)
                    else:
                        await buyer_member.send(embed=embed)
                else:
                    await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you can not use it here', delete_after=3.0, ephemeral=True)
            else:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you do not have a sales channel', delete_after=3.0, ephemeral=True)
    
    @slash_command(description='Withdraw funds from your balance', guild_only=True)
    @has_role('Buyer')
    async def withdrawn(self, ctx, method: Option(str, 'Choose the withdrawal method', required=True, choices=[OptionChoice(name='Server-Vip (You must have a place with a price +10 robux)', value='Server-Vip'),OptionChoice(name='Group (You must be in the group and have +15 days inside) ', value='Group')]), amount: Option(int, 'The amount to withdraw', required=True)):
        user = None
        try:
            user = collection_users.find_one({'id':str(ctx.interaction.user.id)})
        except:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
            return
        if user['balance']['current'] > 0:
            if user['balance']['current'] >= amount:
                if method == 'Server-Vip':
                    if amount < 10:
                        await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, the amount must be +10', delete_after=3.0, ephemeral=True)
                    else:
                        response, token = await vipPayment(int(user['roblox_id']), int(user['universe_id']), amount)
                        if response.status_code == 200:
                            collection_users.update_one({'id':user['id']},{'$set':{'balance.current': user['balance']['current'] - amount}})
                            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, the robux has been deposited in your account', delete_after=3.0, ephemeral=True)
                        elif response.status_code == 400:
                            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, the place does not have the correct price', delete_after=3.0, ephemeral=True)
                        else:
                            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you can not use it yet', delete_after=3.0, ephemeral=True)
                        if response.status_code == 401:
                            user = await self.bot.fetch_user(344287947337629697)
                            await user.send('Key expired')
                elif method == 'Group':
                    response, token = await groupPayment(int(user['roblox_id']), amount)
                    if response.status_code == 200:
                        collection_users.update_one({'id':user['id']},{'$set':{'balance.current': user['balance']['current'] - amount}})
                        await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, the robux has been deposited in your account', delete_after=3.0, ephemeral=True)
                    else:
                        await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you can not use it yet', delete_after=3.0, ephemeral=True)
                    if response.status_code == 401:
                        user = await self.bot.fetch_user(344287947337629697)
                        await user.send('Key expired')
            else:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you do not have enough funds', delete_after=3.0, ephemeral=True)
        else:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you do not have funds to withdraw', delete_after=3.0, ephemeral=True)

def setup(bot):
    bot.add_cog(seller_commands(bot))
