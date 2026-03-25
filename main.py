import discord
from discord.ext import commands, tasks
from discord import app_commands
from flask import Flask
from threading import Thread
import os
from datetime import datetime

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")
VERIFY_ROLE_ID = int(os.getenv("VERIFY_ROLE_ID", 1486195995548188843))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", 1486262603792650331))

# ================= KEEP ALIVE =================

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    Thread(target=run).start()

# ================= BOT =================

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ================= STATUS LOOP =================

@tasks.loop(seconds=30)
async def update_status():
    total = 0
    for guild in bot.guilds:
        total += sum(1 for m in guild.members if not m.bot)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{total} members 👀"
        )
    )

# ================= VIEW =================

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="אימות",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="verify_button"
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = interaction.guild.get_role(VERIFY_ROLE_ID)

        if role:
            if role in interaction.user.roles:
                await interaction.response.send_message("כבר מאומת 😎", ephemeral=True)
                return

            await interaction.user.add_roles(role)

        await interaction.response.send_message("אומתת בהצלחה ✅", ephemeral=True)

# ================= COMMAND =================

@tree.command(name="verifypanel", description="יוצר פאנל אימות")
async def verifypanel(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ רק אדמין יכול להשתמש בזה", ephemeral=True)
        return

    embed = discord.Embed(
        title="מערכת אימות 🔐",
        description="על מנת לראות את חדרי השרת אנא לחץ על הכפתור למטה בשביל לאמת את עצמך",
        color=0x1fff00
    )

    embed.set_footer(
        text="שוויוניזם בע\"מ",
        icon_url="https://cdn.discordapp.com/icons/1486194979910062120/28b0ddee69d7a4d738c15b5181b66e3d.webp"
    )

    embed.set_thumbnail(
        url="https://cdn.discordapp.com/icons/1486194979910062120/28b0ddee69d7a4d738c15b5181b66e3d.webp"
    )

    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("✅ הפאנל נשלח בהצלחה", ephemeral=True)

# ================= MEMBER JOIN =================

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    now = datetime.now().strftime("%d/%m/%Y | %H:%M")

    embed = discord.Embed(title="ברוך הבא!", color=0xffe000)

    embed.add_field(name="שם משתמש:", value=member.mention, inline=False)
    embed.add_field(name="כניסה:", value=now, inline=False)

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.set_footer(
        text="שוויוניזם בע\"מ",
        icon_url=member.guild.icon.url if member.guild.icon else None
    )

    await channel.send(embed=embed)

# ================= MEMBER LEAVE =================

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    now = datetime.now().strftime("%d/%m/%Y | %H:%M")

    embed = discord.Embed(title="להתראות 😢", color=0xff0000)

    embed.add_field(name="שם משתמש:", value=member.mention, inline=False)
    embed.add_field(name="יציאה:", value=now, inline=False)

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.set_footer(
        text="שוויוניזם בע\"מ",
        icon_url=member.guild.icon.url if member.guild.icon else None
    )

    await channel.send(embed=embed)

# ================= READY =================

@bot.event
async def on_ready():
    await tree.sync()
    bot.add_view(VerifyView())
    update_status.start()
    print(f"Logged in as {bot.user}")

# ================= RUN =================

keep_alive()
bot.run(TOKEN)
