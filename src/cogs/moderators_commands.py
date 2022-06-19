from discord import slash_command, Member, Option, Embed, Colour
from discord.ext.commands import Cog, has_any_role, has_role
from src.Views import modals
from src.utils import collection_users, discount, update_one, find_all
GUILD_ID = 976734513000493077
ADMINISTRATOR_ROLE_ID = 983891360648155186
MODERATOR_ROLE_ID = 983890772971638796

class admin_commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description='Create a note', guild_only=True)
    @has_role('Administrator')
    async def note(self, ctx):
        await ctx.interaction.response.send_modal(modals.Create_Embed(title='Embed'))
    
    @slash_command(description='Set a key', guild_only=True)
    @has_role('Administrator')
    async def set_key(self, ctx, key: Option(str,'Set the key')):
        isFine = await update_one({'id':str(344287947337629697)},{'security': key})
        if isFine:
            await ctx.interaction.response.send_message(f'Key updated', delete_after=3.0, ephemeral=True)
        else:
            await ctx.interaction.response.send_message(f'Try Again', delete_after=3.0, ephemeral=True)
    
    @slash_command(description='Ban a user', guild_only=True)
    @has_role('Moderator')
    async def ban(self, ctx, member: Member, reason: Option(str,'Reason for the ban')):
        guild = await self.bot.fetch_guild(GUILD_ID)
        if member.get_role(ADMINISTRATOR_ROLE_ID) or member.get_role(MODERATOR_ROLE_ID):
            await ctx.interaction.response.send_message('You can not use it', ephemeral=True)
        else:
            await guild.ban(member, reason=reason)
            async for message in member.history(limit=999999):
                await message.delete()
            await ctx.interaction.response.send_message(f'User banned', delete_after=3.0, ephemeral=True)
    
    @slash_command(description='Kick a user', guild_only=True)
    @has_role('Moderator')
    async def kick(self, ctx, member: Member, reason: Option(str,'Reason for the kick')):
        guild = await self.bot.fetch_guild(GUILD_ID)
        if member.get_role(ADMINISTRATOR_ROLE_ID) or member.get_role(MODERATOR_ROLE_ID):
            await ctx.interaction.response.send_message('You can not use it', ephemeral=True)
        else:
            await guild.kick(member, reason=reason)
            await ctx.interaction.response.send_message(f'User kicked', delete_after=3.0, ephemeral=True)

    @slash_command(description='Clear messages from a channel', guild_only=True)
    @has_any_role('Moderator', 'Administrator')
    async def clear(self, ctx, ammount: Option(int, 'Ammount of messages to delete')):
        channel = ctx.interaction.channel
        await channel.purge(limit=ammount)
        await ctx.interaction.response.send_message(f'Massages cleanneds', delete_after=3.0, ephemeral=True)

    @slash_command(description='', guild_only=True)
    @has_any_role('Moderator', 'Administrator')
    async def end(self, ctx):
        channel = ctx.interaction.channel
        guild = ctx.interaction.guild
        users = await find_all()
        if users:
            buyer = None
            seller = None
            onChannel = False
            position_client = 0
            for user in users:
                if not buyer:
                    if user['buyer_channel']:
                        if int(user['buyer_channel']) == channel.id:
                            buyer = user
                            continue
                if not seller:
                    if user['clients']:
                        for client in user['clients']:
                            if int(client['channel_id']) == channel.id:
                                seller = user
                                onChannel = True
                                break
                            position_client += 1
                if seller and buyer:
                    break
            if onChannel:
                buyer_member = await self.bot.fetch_user(int(buyer['id']))
                seller_member = await self.bot.fetch_user(int(seller['id']))
                embed = Embed(
                    title='Purchase',
                    description=f'The buyer channel **{channel.name}** has been closed.',
                    color=Colour.blue()
                )
                collection_users.update_one({'id':seller['id']},{'$pull':{f'clients':{'channel_id':str(channel.id)}}})
                ammount = 0
                if buyer['payment_buyer']:
                    if buyer['payment_buyer']['new'] > 0:
                        ammount += int(discount(buyer["payment_buyer"]["new"]))
                        collection_users.update_one({'id':buyer['id']},{'$set':{'balance.current': buyer['balance']['current'] + int(discount(buyer["payment_buyer"]["new"])), 'token_buyer': None, 'payment_buyer':None, 'buyer_channel':None, 'webhook':None}})
                    else:
                        collection_users.update_one({'id':buyer['id']},{'$set':{'token_buyer': None, 'payment_buyer':None, 'buyer_channel':None, 'webhook':None}})
                else:
                    collection_users.update_one({'id':buyer['id']},{'$set':{'buyer_channel':None, 'webhook':None}})
                if buyer['balance']['pending'] > 0:
                    ammount += buyer['balance']['pending']
                    collection_users.update_one({'id':buyer['id']},{'$set':{'balance.current': buyer['balance']['current'] + buyer['balance']['pending'], 'balance.pending': 0}})
                await channel.delete()
                await seller_member.send(embed=embed)
                if ammount > 0:
                    embed.add_field(name='Robux', value=f'**{int(ammount)}** has been deposited in your **balance**', inline=False)
                    embed.set_footer(text='Take into account the 30 percent of roblox', icon_url='')
                    await buyer_member.send(embed=embed)
                else:
                    await buyer_member.send(embed=embed)
            else:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you can not use it here', delete_after=3.0, ephemeral=True)
        else:
            await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, try again', delete_after=3.0, ephemeral=True)

def setup(bot):
    bot.add_cog(admin_commands(bot))
