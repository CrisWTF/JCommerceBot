from discord import Intents
from src.bot import JCommerce
bot = JCommerce(intents=Intents.all())

cogs_list = [
    'users_commands',
    'moderators_commands',
]

for cog in cogs_list:
    bot.load_extension(f'src.cogs.{cog}')
    
bot.run('OTc2NzM2NjEwNDc5NjUyOTA0.GVuKBU.MZDRENGnSrOZ0RRltvsLWHF657G-HXhaG88cbU')