import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN") or "YOUR_TOKEN_HERE"
VERIFY_ROLE_ID = int(os.getenv("VERIFY_ROLE_ID") or 1486195995548188843)

# ================= KEEP ALIVE =================

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ================= BOT =================

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

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
                await interaction.response.send_message(
                    "כבר מאומת 😎",
                    ephemeral=True
                )
                return

            await interaction.user.add_roles(role)

        await interaction.response.send_message(
            "אומתת בהצלחה ✅",
            ephemeral=True
        )

# ================= COMMAND =================

@tree.command(name="verifypanel", description="יוצר פאנל אימות")
async def verifypanel(interaction: discord.Interaction):

    # ✅ רק אדמין
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ רק אדמין יכול להשתמש בזה",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="מערכת אימות 🔐",
        description="על מנת לראות את חדרי השרת אנא לחץ על הכפתור למטה בשביל לאמת את עצמך",
        color=0x1fff00
    )

    embed.set_footer(
        text="שוויוניזם בע\"מ",
        icon_url="https://cdn.discordapp.com/icons/1486194979910062120/28b0ddee69d7a4d738c15b5181b66e3d.webp?size=80&quality=lossless"
    )

    embed.set_thumbnail(
        url="https://cdn.discordapp.com/icons/1486194979910062120/28b0ddee69d7a4d738c15b5181b66e3d.webp?size=80&quality=lossless"
    )

    # ❗ שולח את הפאנל לחדר
    await interaction.channel.send(
        embed=embed,
        view=VerifyView()
    )

    # ✅ מחזיר תשובה רק למי שהפעיל
    await interaction.response.send_message(
        "✅ הפאנל נשלח בהצלחה",
        ephemeral=True
    )

# ================= READY =================

@bot.event
async def on_ready():
    await tree.sync()
    bot.add_view(VerifyView())
    print(f"Logged in as {bot.user}")

# ================= RUN =================

keep_alive()
bot.run(TOKEN)
