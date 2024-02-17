import discord 
from discord.ext import commands, tasks
import sys, os, json

# Import Encoder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from EnCoder import EnCoder, Constructor



# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Task: Check For Files to Upload
@tasks.loop(seconds=5)
async def check_for_files():
    
    Files = 'Files'
    for file in os.listdir(Files):# Loop through the files in the Files directory
        FileData = {
            'FileName': file,
            'FileType': file.split('.')[-1],
            'FileSize': f'{round(os.path.getsize(f"{Files}/{file}") / 1000000, 2)} Mb',
            'Chuncks': []
        }
        FullPath = f'{Files}/{file}'
        coder = EnCoder(FullPath)
        Chuncks = coder.ByteSplit(coder.BYTES, 25, coder.MbSize()) # Split into 25MB chunks
        Files = coder.SaveToFile(Chuncks) # Save the chuncks to files

        for file in Files: # Upload the chuncks to discord
            ChannelID = 1208379305634299934
            channel = bot.get_channel(ChannelID)

            if channel:
                try:
                    message = await channel.send(file=discord.File(file))
                    FileData['Chuncks'].append([message.id, file])

                    # Remove the file from the Files directory
                    os.remove(file)
                    print(f'Removed {file}')
                except discord.HTTPException as e:
                    print(f"Failed to upload file {file}: {e}")
            else:
                print(f"Channel with ID {ChannelID} not found.")

        # Add to StoreFiles.json
        with open('FrontEnd/StoreFiles.json', 'r') as f:
            data = json.load(f)
        data.append(FileData)
        with open('FrontEnd/StoreFiles.json', 'w') as f:
            json.dump(data, f, indent=4)

        # Remove the file from the Files directory
        os.remove(FullPath)
        print(f'Removed {FullPath}')

            



# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    check_for_files.start()


# Command: Store Files
@bot.command()
async def store(ctx, *args):
    await ctx.message.delete()

    # Load StoreFiles.json
    with open('FrontEnd/StoreFiles.json', 'r') as f:
        data = json.load(f)

    # Send the files
    Message = ''
    for file in data:
        Message += f'**{file["FileName"]}** | **{file["FileType"]}** | **{file["FileSize"]}** | **{len(file["Chuncks"])}** chuncks\n'

    await ctx.send(Message)



@bot.command()
async def download(ctx, *args):
    await ctx.message.delete()

    # Load StoreFiles.json
    with open('FrontEnd/StoreFiles.json', 'r') as f:
        data = json.load(f)

    Chuncks = None  # Initialize as None or an empty list
    # Find the file
    for file in data:
        if file['FileName'] == args[0]:
            Chuncks = file['Chuncks']

    if Chuncks is not None:
        # Download the chuncks
        for chunck in Chuncks:
            message = await ctx.fetch_message(chunck[0])
            await message.attachments[0].save(f'{chunck[1]}')


        # Rebuild Original File
        print(Chuncks)
        build = Constructor(Chuncks, args[0])
        build.SaveFile()

        # Clean up 
        for chunck in Chuncks:
            os.remove(chunck[1])





bot.run('Token Here')