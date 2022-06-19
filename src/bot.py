from discord import Bot, Member, PermissionOverwrite
from src.Views import buttons
from discord.ext.commands import MissingRole, CommandOnCooldown
import re
from src.utils import collection_users


SELLER_ROLE_ID = 977025090313142322
BUYER_ROLE_ID = 981616570876969080
MEMBER_ROLE_ID = 977023989035720755
GUILD_ID = 976734513000493077
VERIFY_ID = 984311672376262677
VERIFY_ID_MESSAGE = 985541899500781578
SUPPORT_ID_MESSAGE = 986721831849439342
TICKET_ID_CATEGORY = 986711748398698586

class JCommerce(Bot):

    def __init__(self, *args, **options):
        super().__init__(*args, **options)

    async def on_ready(self):
        self.add_view(buttons.Button_Buy())
        print('Is already On')

    async def on_member_remove(self,member):
        user = collection_users.find_one({'id': str(member.id)})
        if user:
            if user['shop']:
                if user['shop']['channel']['id']:
                    guild = self.get_guild(GUILD_ID)
                    channel_user = await guild.fetch_channel(user['shop']['channel']['id'])
                    await channel_user.delete()
                    collection_users.update_one({'id':str(member.id)},{'$set':{f'shop.channel.id':None, 'shop.channel.messages': [None,None,None,None,None]}})
            if not user['buyer_channel']:
                collection_users.delete_one({'id': str(member.id)})

    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) == '👍' and payload.message_id == VERIFY_ID_MESSAGE:
            guild = self.get_guild(GUILD_ID)
            member_role = guild.get_role(MEMBER_ROLE_ID)
            buyer_role = guild.get_role(BUYER_ROLE_ID)
            seller_role = guild.get_role(SELLER_ROLE_ID)
            support_channel = await guild.fetch_channel(983857249313230898)
            message = await support_channel.fetch_message(985541899500781578)
            await message.remove_reaction(payload.emoji, payload.member)
            permissions = PermissionOverwrite()
            permissions.send_messages = True
            permissions.read_messages = True
            permissions.read_message_history = True
            user = collection_users.find_one({'id': str(payload.member.id)})
            if user:
                await payload.member.add_roles(member_role, buyer_role)
                if user['buyer_channel']:
                    channel = await guild.fetch_channel(int(user['buyer_channel']))
                    await channel.set_permissions(payload.member,overwrite=permissions)
                if user['shop']:
                    await payload.member.add_roles(seller_role)
                    if user['clients']:
                        for client in user['clients']:
                            channel = await guild.fetch_channel(int(client['channel_id']))
                            await channel.set_permissions(payload.member,overwrite=permissions)
            else:
                await payload.member.add_roles(member_role)
        elif str(payload.emoji) == '🔧' and payload.message_id == SUPPORT_ID_MESSAGE:
            member: Member = payload.member
            guild = self.get_guild(GUILD_ID)
            support_channel = await guild.fetch_channel(983858927773040661)
            message = await support_channel.fetch_message(SUPPORT_ID_MESSAGE)
            await message.remove_reaction(payload.emoji, member)
            ticket_category = await guild.fetch_channel(TICKET_ID_CATEGORY)
            channel = await ticket_category.create_text_channel(name=member.name)
            permissions = PermissionOverwrite()
            permissions.send_messages = True
            permissions.read_messages = True
            permissions.read_message_history = True
            permissions.attach_files = True
            permissions.manage_channels = True
            await channel.set_permissions(member,overwrite=permissions)

        #Guardar el estado del botón
        #self.add_view(buttons.Button_Create_Shop())
        #Checar si el canal create-shop existe

    async def on_application_command_error(self,ctx,error):
        if isinstance(error,MissingRole):
            if re.search('Buyer',str(error)):
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you have to verify yourself to use this', delete_after=3.0)
            elif re.search('Seller',str(error)):
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you need to have a shop, use "/shop create" to create one', delete_after=3.0)
            elif re.search('Administrator',str(error)) or re.search('Moderator',str(error)):
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you do not have permissions to use it', delete_after=3.0)
        if isinstance(error,CommandOnCooldown):
            if error.retry_after < 60:
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you need to wait **{round(error.retry_after)} seconds** to use it again', delete_after=3.0)
            else:
                minutes = error.retry_after//60
                seconds = error.retry_after%60
                await ctx.interaction.response.send_message(f'{ctx.interaction.user.mention}, you need to wait **{round(minutes)}.{round(seconds)} minutes** to use it again', delete_after=3.0)
