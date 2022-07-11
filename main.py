import json

from discord.ext.commands import bot
from google_currency import convert
import os
import json
import datetime
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = commands.Bot(command_prefix='/')


def getEUR_HUF_exhange_rate():
    exchange_rate = convert('eur', 'huf', 1)
    rate_json = json.loads(exchange_rate)
    save_exchange_rate(rate_json["amount"])
    return rate_json["amount"]


def get_any_to_any_exchange_rate(currency_from: str, currency_to: str, amount: int) -> float:
    exchange_rate = convert(currency_from, currency_to, amount)
    rate_json = json.loads(exchange_rate)
    return rate_json["amount"]


def save_exchange_rate(rate):
    timestamp = str(datetime.datetime.utcnow().timestamp())
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
    channel = client.get_channel(990292982274097302)
    print(channel)


#   await channel.send(embed=generate_embed())


@client.event
async def send_message(message):
    pass


@client.command()
async def árfolyam(ctx, *args):
    if len(args) == 0:
        exchange_rate = getEUR_HUF_exhange_rate()
        embed = generate_embed("EUR", "HUF", exchange_rate)
    elif len(args) == 1:
        embed = exchange_any_to_huf(args[0])
    elif len(args):
        embed = exchange_any_to_any(args[0], args[1])
    channel = client.get_channel(990292982274097302)
    await ctx.channel.send(embed=embed)


def exchange_any_to_any(currency_from = "eur", currency_to = "huf", amount = 1) -> discord.Embed:
    exchange_rate = get_any_to_any_exchange_rate(currency_from, currency_to, amount)
    if exchange_rate == 0:
        return generate_embed(currency_from, "HUF", 0, "Hibás valuta")
    return generate_embed(currency_from, "HUF", exchange_rate)


client.run(TOKEN)


def printExchangeRate():
    # Converted without comma like 70000.00
    print(convert('huf', 'eur', 1))

    # Converted amount with comma like 70,000.00
    print(convert('eur', 'huf', 1))
