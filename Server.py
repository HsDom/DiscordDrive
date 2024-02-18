import discord
from discord.ext import commands, tasks
from flask import Flask, request, render_template
import threading
import asyncio
import sys
import os
import json
from werkzeug.serving import run_simple


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from EnCoder import EnCoder, Constructor




# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")


@tasks.loop(seconds=60)
async def background_task():        
    print("Background task running")


# Flask setup
app = Flask(__name__)


@app.route('/')
def home():
    # Load Files From Json
    JSON = r"FrontEnd\StoreFiles.json"
    data = {}
    with open(JSON, 'r') as f:
        data = json.load(f)

    return render_template('index.html', data=data)


@app.route('/download', methods=['POST'])
def download():
    # Download File From Server
    FILENAME = request.form['FileName']

    data = None # Initialize as None or an empty list
    with open('FrontEnd/StoreFiles.json', 'r') as f:
        data = json.load(f)

    Chuncks = None  # Initialize as None or an empty list

    # Find the file
    for file in data:
        if file['FileName'] == FILENAME:
            Chuncks = file['Chuncks'] # This is a list of chuncks

    ChannelID = 1208379305634299934 # Temporary
    channel = bot.get_channel(ChannelID)
    if Chuncks is not None:
        # Download the chuncks
        for chunck in Chuncks:
            message = asyncio.run_coroutine_threadsafe(channel.fetch_message(chunck[0]), bot.loop).result()
            attachment = message.attachments[0]
            asyncio.run_coroutine_threadsafe(attachment.save(f'{chunck[1]}'), bot.loop).result()

        # Rebuild Original File
        print(Chuncks)
        build = Constructor(Chuncks, FILENAME)
        build.SaveFile()

        # Clean up
        for chunck in Chuncks:
            os.remove(chunck[1])

    return render_template('downloading.html')


def run_flask():
    run_simple('127.0.0.1', 5000, app, use_reloader=False, use_debugger=True)


async def run_bot():
    background_task.start()
    await bot.start('Token Here')

if __name__ == '__main__':
    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start the Discord bot in the main thread using the event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())