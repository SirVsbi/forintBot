from __future__ import annotations

from cmath import sin
from enum import Enum, unique
import json
from pathlib import Path

from discord.ext.commands import bot
from google_currency import convert
import os
import json
from datetime import datetime, timedelta
import discord
from dotenv import load_dotenv
import asyncio
from discord.ext import commands, tasks

from .visualize import ExchangeRateHistory


_JSON_PATH = Path("data.json")
_GRAPH_PATH = Path("graph.png")


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_ID = os.getenv('CHANNEL_ID')

client = commands.Bot(command_prefix='/')


def getEUR_HUF_exchange_rate() -> float:
    exchange_rate = convert('eur', 'huf', 1)
    rate_json = json.loads(exchange_rate)
    save_exchange_rate(rate_json["amount"])
    return rate_json["amount"]


def get_any_to_any_exchange_rate(currency_from: str, currency_to: str, amount: float) -> float:
    exchange_rate = convert(currency_from, currency_to, amount)
    rate_json = json.loads(exchange_rate)
    return rate_json["amount"]


def save_exchange_rate(rate):
    timestamp = str(datetime.utcnow().timestamp())
    filename = "data.json"
    data = {}

    # Check if file exists
    if os.path.isfile(filename) is False:
        raise Exception("File not found")

    # Read JSON file
    with open(filename) as fp:
        data = json.load(fp)

    data[timestamp] = rate
    with open(filename, 'w') as json_file:
        json.dump(data, json_file,
                  indent=4,
                  separators=(',', ': '))


@unique
class LastInterval(Enum):
    HOUR = timedelta(hours=1)
    DAY = timedelta(days=1)
    WEEK = timedelta(days=7)
    MONTH = timedelta(days=30)
    YEAR = timedelta(days=365)

    @classmethod
    def fromString(string: str) -> LastInterval:
        match string:
            case "órai":
                return LastInterval.HOUR
            case "napi":
                return LastInterval.DAY
            case "heti":
                return LastInterval.WEEK
            case "havi":
                return LastInterval.MONTH
            case "évi":
                return LastInterval.YEAR
            case _:
                raise ValueError(f"{string} cannot be converted to LastInterval")

def visualize_history(last: LastInterval) -> Path:
    now = datetime.utcnow()
    history = ExchangeRateHistory.fromJson(_JSON_PATH)
    history.plot(
        output=_GRAPH_PATH,
        since=now - last.value
    )
    return _GRAPH_PATH

def generate_embed(currency_from: str, currency_to: str, exchange_rate, text: str | None = None) -> discord.Embed:
    embed = discord.Embed(
        title="Doktorminiszterelnökúr, a mostani jelentés készen van",
        colour=discord.Color.from_rgb(46, 26, 71)  # AB7FBC
    )
    embed.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Parliament_Building%2C_Budapest%2C_outside.jpg/1200px-Parliament_Building%2C_Budapest%2C_outside.jpg")
    if text is None:
        embed.add_field(
            name=currency_from + "<->" + currency_to,
            value=exchange_rate
        )
    else:
        embed.add_field(
            name=text,
            value="Nem létezik ilyen valuta"
        )
    return embed


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


@client.command()
async def árfolyam(ctx, *args):
    lastInterval = None
    if len(args) == 0:
        exchange_rate = getEUR_HUF_exchange_rate()
        embed = generate_embed("EUR", "HUF", exchange_rate)
        lastInterval = LastInterval.WEEK
    elif len(args) == 1:
        if args[0].isdigit():
            embed = exchange_any_to_any(args[0])
        else:
            try:
                exchange_rate = getEUR_HUF_exchange_rate()
                embed = generate_embed("EUR", "HUF", exchange_rate)
                lastInterval = LastInterval.fromString(args[0])
            except ValueError:
                pass
    elif len(args) == 2:
        embed = exchange_any_to_any(args[0], args[1])
    elif len(args) == 3:
        embed = exchange_any_to_any(args[0], args[1], float(args[2]))
    channel = client.get_channel(990292982274097302)
    await ctx.channel.send(embed=embed)
    if lastInterval is not None:
        await ctx.channel.send(file=discord.File(visualize_history(lastInterval)))


def exchange_any_to_any(currency_from: str = "eur", currency_to: str = "huf", amount: float = 1) -> discord.Embed:
    exchange_rate = get_any_to_any_exchange_rate(currency_from, currency_to, amount)
    if exchange_rate == 0:
        return generate_embed(currency_from, currency_to, 0, "Hibás valuta")
    return generate_embed(currency_from, currency_to, exchange_rate)


@client.event
async def on_ready():
    send_exchange_rate.start()


@tasks.loop(hours=1.0)
async def send_exchange_rate():
    channel = client.get_channel(990292982274097302)
    await channel.send(embed=generate_embed("EUR", "HUF", getEUR_HUF_exchange_rate()))


client.run(TOKEN)
