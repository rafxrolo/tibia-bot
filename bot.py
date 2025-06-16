import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup
import os
from flask import Flask
import threading

# Mantener Replit activo
app = Flask('')
@app.route('/')
def home():
    return "Estoy vivo"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=3000)).start()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
SERVER = 'Solidera'

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
last_deaths = []

def get_recent_deaths(server):
    url = f"https://www.tibia.com/community/?subtopic=worlds&world={server}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'lxml')
    try:
        table = soup.select("table.TableContent")[1]
        rows = table.find_all('tr')[1:]
    except:
        return []
    deaths = [(r.find_all('td')[0].text.strip(), r.find_all('td')[1].text.strip()) for r in rows if len(r.find_all('td'))>=2]
    return deaths

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Estoy vivo.")

@bot.command()
async def ultimas(ctx):
    deaths = get_recent_deaths(SERVER)
    if not deaths:
        return await ctx.send("No se encontraron muertes recientes.")
    msg = "**💀 Últimas muertes en Solidera:**\n"
    for t,d in deaths[:5]:
        msg += f"🕒 {t} — {d}\n"
    await ctx.send(msg)

@tasks.loop(minutes=5)
async def check_server_deaths():
    global last_deaths
    new = get_recent_deaths(SERVER)
    channel = bot.get_channel(CHANNEL_ID)
    for death in new:
        if death not in last_deaths:
            time,desc = death
            await channel.send(f"💀 **Nueva muerte en {SERVER}**\n🕒 {time} — {desc}")
    last_deaths = new[:20]

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    check_server_deaths.start()

bot.run(TOKEN)
