import os
import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        print("Slash commands synced ✔")
    except Exception as e:
        print("tree sync failed:", e)

# ============================================================
# 🔥spam — سبام خاص + سيرفر
# ============================================================
@bot.tree.command(name="🔥spam", description="🔥 يسبام يوزر في الخاص أو في السيرفر 30 رسالة")
@app_commands.describe(
    user="اليوزر اللي هيتسبام",
    message="الرسالة اللي هتتبعت",
    channel="القناة في السيرفر (اختياري — لو مش محدد هيبعت في الخاص)"
)
@app_commands.checks.has_permissions(administrator=True)
async def spam_cmd(
    interaction: discord.Interaction,
    user: discord.User,
    message: str,
    channel: discord.TextChannel = None
):
    await interaction.response.defer(ephemeral=True)

    spam_count = 30
    success = 0
    failed = 0

    if channel:
        # سبام في قناة السيرفر
        for _ in range(spam_count):
            try:
                await channel.send(f"{user.mention} {message}")
                await asyncio.sleep(0.5)
                success += 1
            except discord.HTTPException as e:
                if e.status == 429:
                    await asyncio.sleep(float(getattr(e, "retry_after", 3.0)) + 1.0)
                    try:
                        await channel.send(f"{user.mention} {message}")
                        success += 1
                    except:
                        failed += 1
                else:
                    failed += 1
    else:
        # سبام في الخاص DM
        try:
            dm = await user.create_dm()
            for _ in range(spam_count):
                try:
                    await dm.send(message)
                    await asyncio.sleep(0.5)
                    success += 1
                except discord.HTTPException as e:
                    if e.status == 429:
                        await asyncio.sleep(float(getattr(e, "retry_after", 3.0)) + 1.0)
                        try:
                            await dm.send(message)
                            success += 1
                        except:
                            failed += 1
                    elif e.status == 403:
                        # الخاص مقفول
                        failed += spam_count - success
                        break
                    else:
                        failed += 1
        except discord.Forbidden:
            return await interaction.followup.send(
                "❌ الخاص مقفول، مش قادر يبعت له.",
                ephemeral=True
            )

    await interaction.followup.send(
        f"✅ خلص:\n• ✉️ اتبعتوا: {success} رسالة\n• ❌ فشلوا: {failed} رسالة",
        ephemeral=True
    )

# ============================================================
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
    raise SystemExit("⚠️ مفيش توكن!")
bot.run(TOKEN)
