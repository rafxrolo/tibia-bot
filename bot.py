import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
SERVER = 'Solidera'

last_deaths = []

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

def get_recent_deaths(server):
    url = f"https://www.tibia.com/community/?subtopic=worlds&world={server}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    death_table = soup.find('div', class_='TableContentContainer').find('table')
    deaths = []

    if not death_table:
        return deaths

    rows = death_table.find_all('tr')[1:]  # skip header row
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            time = cols[0].text.strip()
            desc = cols[1].text.strip()
            deaths.append((time, desc))

    return deaths

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    check_server_deaths.start()

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Estoy vivo.")

@bot.command()
async def ultimas(ctx):
    deaths = get_recent_deaths(SERVER)
    if not deaths:
        await ctx.send("No se encontraron muertes recientes.")
        return

    msg = "**💀 Últimas muertes en Solidera:**\n"
    for time, desc in deaths[:5]:
        msg += f"🕒 {time} — {desc}\n"
    await ctx.send(msg)

@tasks.loop(minutes=5)
async def check_server_deaths():
    global last_deaths
    new_deaths = get_recent_deaths(SERVER)
    channel = bot.get_channel(CHANNEL_ID)

    for death in new_deaths:
        if death not in last_deaths:
            time, desc = death
            msg = f"💀 **Nueva muerte en {SERVER}**\n🕒 {time} — {desc}"
            await channel.send(msg)

    last_deaths = new_deaths[:20]

bot.run(TOKEN)
