import json

from google_currency import convert
import os
import json
import datetime
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()


def getEUR_HUF_exhange_rate():
    exchange_rate = convert('eur', 'huf', 1)
    rate_json = json.loads(exchange_rate)
    save_exchange_rate(rate_json["amount"])
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




def generate_embed():
    embed = discord.Embed(
        title="Doktorminiszterelnökúr, a mostani jelentés készen van",
        colour=discord.Color.from_rgb(46, 26, 71)  # AB7FBC
    )
    embed.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Parliament_Building%2C_Budapest%2C_outside.jpg/1200px-Parliament_Building%2C_Budapest%2C_outside.jpg")
    embed.add_field(
        name="EUR <-> HUF",
        value=getEUR_HUF_exhange_rate()
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
    await channel.send \
        (embed=generate_embed())


@client.event
async def send_message(message):
    pass


client.run(TOKEN)


def printExchangeRate():
    # Converted without comma like 70000.00
    print(convert('huf', 'eur', 1))

    # Converted amount with comma like 70,000.00
    print(convert('eur', 'huf', 1))
