from discord.ui import View, button
from discord import ButtonStyle, Colour, Embed, PermissionOverwrite
from src.Views import modals
from src.utils import collection_users
from re import sub

SELLER_ROLE_ID = 977025090313142322
BUYER_ROLE_ID = 981616570876969080
MODERATOR_ROLE_ID = 983890772971638796
# ------------------------------- Create ---------------------------------------------

class Button_Buy(View):
    #Se coloca timeout=None para poder guardar el estado del botón, junto con un custom_id
    def __init__(self):
        super().__init__(timeout=None)

    @button(label='Buy',style=ButtonStyle.success, custom_id='button-buy')
    async def first_button_callback(self, button, interaction):
        try:
            channel_id = interaction.channel_id
            guild = interaction.guild
            buyer = interaction.user
            seller_discord = collection_users.find_one({'shop.channel.id':channel_id})
            if int(seller_discord['id']) != buyer.id:
                buyer_discord = collection_users.find_one({'id':str(buyer.id)})
                if buyer_discord:
                    if buyer_discord['buyer_channel']:
                        await interaction.response.send_message('You need to complete the buy first', ephemeral=True)
                    else:
                        seller = await guild.fetch_member(seller_discord['id'])
                        moderators = guild.get_role(MODERATOR_ROLE_ID)
                        permissions = PermissionOverwrite()
                        permissions.send_messages = True
                        permissions.read_messages = True
                        permissions.read_message_history = True
                        permissions.view_channel = True
                        permissions.use_slash_commands = True
                        overwrites = {
                            buyer: permissions,
                            seller: permissions,
                            moderators: permissions
                        }
                        embed = Embed(
                            title='Help',
                            description='This channel is private, only the moderators, seller and buyer can see it.\nTake into account the **30 percent** roblox charges.',
                            color=Colour.blue()
                        )
                        embed.add_field(name='Buyer:', value='1. If you pay something for robux and the seller has not made the trade, you can call a moderator in "#support" to cancel it and get your robux back.\n2. Once the purchase is made, you will not be able to use "/close", it is to secure the purchase.', inline=False)
                        embed.add_field(name='Seller:', value='1. If you sell something and the payment is not robux, we are not responsible. Otherwise, you can use "/create_key".\n2. Pls take the evidence when you make the exchange to avoid any inconvenience (Only if the payment was for robux).', inline=False)
                        elements = len(seller_discord['clients'])
                        channel_private = await guild.create_text_channel(buyer.name, position=0, overwrites=overwrites)
                        webhook = await channel_private.create_webhook(name='JCommerce Purchase')
                        url = sub("discord.com","hooks.hyra.io",webhook.url)
                        collection_users.update_one({'id':str(buyer.id)},{'$set':{'buyer_channel':str(channel_private.id), 'webhook':url}})
                        collection_users.update_one({'id':str(seller.id)},{'$set':{f'clients.{str(elements)}':{'channel_id':str(channel_private.id), 'buyer_id':str(buyer.id)}}})
                        await channel_private.send(embed=embed)
                        await interaction.response.send_message('You have created a channel to buy', ephemeral=True)
                else:
                    await interaction.response.send_message('You need to verify first', ephemeral=True)
            else:
                await interaction.response.send_message('You can not use it in your own shop', ephemeral=True)
        except:
            pass
        
        #Sólo los comandos o botones pueden mandar modals
        #await interaction.response.send_modal(MyModal(title="Modal via Button"))

# --------------------------- Verify ----------------------------------------

class Verify(View):
    
    def __init__(self, roblox_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roblox_id = roblox_id

    @button(label='Confirm',style=ButtonStyle.success, custom_id='verify-confirm')
    async def confirm_button(self,button,interaction):
        for child in self.children:
            child.disabled = True
            child.style = ButtonStyle.secondary
        # collection_users.insert_one({'id': interaction.user.id, 'roblox_id': })
        await interaction.message.edit(view=self)
        await interaction.response.send_modal(modals.Verify_Place(title='Verify Place', roblox_id=self.roblox_id))

    @button(label='Cancel',style=ButtonStyle.danger, custom_id='verify-cancel')
    async def cancel_button(self,button,interaction):
        await interaction.response.edit_message(delete_after=0.0)
