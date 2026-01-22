import discord
import sqlite3
from discord.ext import commands
import datetime
import asyncio
import os
from dotenv import load_dotenv
import re
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


# To run the bot:
# 1. Navigate to the project directory:
#    cd Webscrapin/TheAlgoritihim/'DanganRP Bot'/
# 2. Activate the virtual environment:
#    source myenv/bin/activate
# 3. Run the bot:
#    python bot.py
#to stop the bot: Ctrl + C
intents = discord.Intents.default()
intents.messages = True #To access Messages I beleive 
intents.message_content = True  # Needed to read messages

bot = commands.Bot(command_prefix='coffee: ', intents=intents)

#conn = sqlite3.connect('messages.db') #command to access the database, if generalized, need to term which database
#cursor = conn.cursor() #the cursor allowing it to browse through the data 
#conn.commit() #committs a change to the data set
#conn.close() closes data set
#cursor.execute(''' 
#    CREATE TABLE IF NOT EXISTS messages( 
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#        char_name TEXT,
#        content TEXT,
#        timestamp TEXT,
#        channel_name TEXT,
#        Char_key TEXT DEFAULT 'NA'
#   )
#''')
conn = sqlite3.connect('master.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS master(
        server_id INTEGER PRIMARY KEY,
        server_name TEXT,
        timezone TEXT DEFAULT 'PST',
        db_path TEXT,
        password TEXT,
        setup_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        
    )
''')
conn.commit()
conn.close()
#creates table messages with id(likely just to organize data, not needed?), char_name (tupper name), content(message),
#timestamp of message (In utc + 11 if my calculations are correct), channel name, and character key to designated multiple tuppers as same character
#to be set later on

#conn.commit() #this command finalizes a change to a data set
def server_find(guild_id):
    #curr_server = f"server_{guild.id}.db"
    conn = sqlite3.connect('master.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT db_path FROM master WHERE server_id = ?""", (guild_id,))
    target_db = cursor.fetchone()
    conn.close()
    if target_db is None:
        return None
    return(target_db[0])
#overall, will likely need to change this to an on start/setup command, assuming this wil be a bot that runs constantly, only needed once

async def auth_user(ctx, target_db):
    await ctx.send(f"this command requires a password! Please respond with the correct password")
    conn = sqlite3.connect('master.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT password FROM master WHERE db_path = ?""", (target_db,))
    corr_pass = cursor.fetchone()[0]
    conn.close()
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        att_pass = await bot.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("Authentication timed out, please try again!")
        return 2
    if att_pass.content == corr_pass:
        return 1
    else: 
        await ctx.send(f"Inccorect password! please enter command again")
        return 2 

def check(m):
    return m.author == ctx.author and m.channel == ctx.channel
    
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx): #server creation process, to be ran first

    server = ctx.guild
    exists = ctx.guild.id
    conn = sqlite3.connect('master.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT server_name FROM master WHERE server_id = ?''', (exists,))
    if cursor.fetchone() is not None: 
        await ctx.send(f"Setup for this server has already been detected, if you want to change information, Please use coffee: settings")
    admin = ctx.author 

    await ctx.send(f"Welcome To Coffee Bot! In this setup process, I will ask you a few short questions so that you can get started with data collections! Please make sure we are in a private channel as securit details may be shared!")

    await ctx.send(f"First things first, Please select what timezone you want your messages localized in? Current supported options: PST, UTC, CST, MST")

    timezone_msg = await bot.wait_for('message', check=lambda m: m.author == admin and m.channel == ctx.channel)
    timezone = timezone_msg.content

    await ctx.send(f"Next up! please set a password needed to access data manipulation/deletion, make sure to store this in a secure place!")

    password_msg = await bot.wait_for('message', check=lambda m: m.author == admin and m.channel == ctx.channel)
    password = password_msg.content
    await ctx.send(f"Password has been sent as **{password}**, please store this in a safe, secure place!")

    db_name = f"server_{ctx.guild.id}.db"

    conn = sqlite3.connect('master.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO master (server_id, server_name, timezone, db_path, password, setup_by) VALUES (?, ?, ?, ?, ?, ?)
    ''', (ctx.guild.id, ctx.guild.name, timezone, db_name, password, admin.id))
    conn.commit()
    conn.close()

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            char_name TEXT,
            content TEXT,
            timestamp TEXT,
            channel_name TEXT,
            char_key TEXT DEFAULT "NA" 
        )
    ''')
    conn.commit()
    conn.close()

    await ctx.send(f'Server set up complete! for a brief tutorial type "Coffee: tutorial", to view commands run "Coffee: commands". I recommend starting with adding channels using "Coffee: channels" Have fun data collecting!')


        
        
#@bot.event
#async def on_ready():
#    conn = sqlite3.connect('master.db')
#    cursor = conn.cursor()
#    cursor.execute('''
#        ALTER TABLE master
#        ADD COLUMN scrape_trgt TEXT DEFAULT ""
#    ''')
#    conn.commit()
#    conn.close()
    

@bot.event #discord command designating a bot occasion
async def on_ready(): #this is when the bot goes online, 
    print(f'Logged in as {bot.user}')  # Confirms bot is online, prints in terminal

#THIS SPOT RESERVED FOR EVENTUAL SETUP HOOK

@bot.command() #designates a command
async def scrape(ctx, channel: discord.TextChannel): #collects message history from mentioned channel, Coffee: scrape @channel
    target_db = server_find(ctx.guild.id)
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')
        return
    result = await auth_user(ctx, target_db)
    if result == 2:
        return
    await ctx.send(f'Remembering the good times from {channel.mention}...') #ctx.send means sending a message
   

    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()
    

    count = 0 #count initalized to prevent scraping limits and getting bot banned
    async for message in channel.history(limit=None): #access channel.history
        if message.webhook_id is not None: #if a webhook
            char_name = message.author.name #works to collect name even with nature of tupper
            content = message.content
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            channel_name = message.channel.name
            if isinstance(message.channel, discord.Thread) and message.channel.parent:
                channel_name = message.channel.parent.name

            cursor.execute("""
                SELECT 1 FROM messages WHERE char_name = ? AND content = ? AND timestamp = ? AND channel_name = ?
            """, (char_name, content, timestamp, channel_name))

            if cursor.fetchone() is None:  # If no duplicate exists, insert it
                cursor.execute("""
                    INSERT INTO messages (char_name, content, timestamp, channel_name) VALUES (?, ?, ?, ?)
                """, (char_name, content, timestamp, channel_name))
                
            
            count += 1
        if count % 50 == 0:
            await asyncio.sleep(1)
    conn.commit()
    conn.close()
    await ctx.send(f'I collected {count} messages from {channel.mention}!')







@bot.command()
async def channels(ctx):
    target_db = server_find(ctx.guild.id)
    
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')

    result = await auth_user(ctx, target_db)
    if result == 2:
        return

    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()
    await ctx.send(f'Welcome to your channels! this is where you can view/add/remove which channels this bot collects messages from! please respond with what action you would like to take: \n "view": view currently registered channels. \n "add": add new channels to the list. \n "remove": remove channels from the list')
    chaction_msg = await ctx.bot.waitfor('message', check=lambda m: m.author == admin and m.channel == ctx.channel)
    chaction = str(chaction_msg.content)

    if chaction == 'view':
        #view_channels()
    if chaction == 'add': 
        #add_channels()
    if chaction == 'remove':
        #remove_channels()
    










@bot.command()
async def num(ctx, tup_name: str): #counts num of mssgs from specific tupper
    target_db = server_find(ctx.guild.id)
    
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')

    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()
    await ctx.send(f'searching for messages from {tup_name}')
    try:

        cursor.execute("SELECT Count(*) FROM messages WHERE char_name = ?", (tup_name,))
        result = cursor.fetchone()

        conn.close()

        if result and result[0] > 0:
            await ctx.send(f" **{tup_name}** has sent {result[0]} messages!")
        else:
            await ctx.send(f"No messages found! are you sure your using the right name?")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")   #works as intended
@bot.command() #WILl NEED TO MAKE THIS A ADMIN ONLY COMMAND
async def soft_reset(ctx, date: str):  
    """
    Deletes messages before a given date (YYYY-MM-DD).
    Example usage: coffee: soft_reset 2024-03-01
    """
    target_db = server_find(ctx.guild.id)
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')
        return
    result = await auth_user(ctx, target_db)
    if result == 2:
        return
    
    
    

    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    try:
        # Convert input to a valid datetime
        reset_date = datetime.datetime.strptime(date, "%Y-%m-%d")

        def delete_old_messages():
            with sqlite3.connect(target_db) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE timestamp < ?", (reset_date.strftime("%Y-%m-%d %H:%M:%S"),))
                conn.commit()

        # Run deletion asynchronously
        await asyncio.get_running_loop().run_in_executor(None, delete_old_messages)

        await ctx.send(f"Messages before {date} have been deleted!")

    except ValueError:
        await ctx.send("Invalid date format! Use YYYY-MM-DD.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def word_count(ctx, phrase: str, tup_name: str = None):
    """
    Counts the number of times a word or phrase appears in a tupper's messages.
    Example usage: coffee: word_count "hello world" TupperName
    """
    target_db = server_find(ctx.guild.id)
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')
        return
        
    phrase = phrase.lower()

    try:
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        
        if tup_name:
            cursor.execute("SELECT content FROM messages WHERE char_name = ? AND LOWER(content) LIKE ?", (tup_name, f'%{phrase.lower()}%'))
        else:
            cursor.execute("SELECT char_name, content FROM messages WHERE LOWER(content) LIKE ?", (f'%{phrase.lower()}%',))
        messages = cursor.fetchall()
        conn.close()

        pattern = re.compile(rf'(?<!\w)[\*_]*{re.escape(phrase)}[\*_]*(?!\w)', re.IGNORECASE) #tells discord to ignore these symbols when next

        if tup_name: 
            total = sum(len(pattern.findall(msg[0].lower())) for msg in messages)     
            await ctx.send(f"**{tup_name}** has said \"{phrase}\" {total} times!")
        else: 
            counts = {}
            for char_name, msg in messages:
                matches = len(pattern.findall(msg.lower()))
                if matches > 0:
                    counts[char_name] = counts.get(char_name, 0) + matches
            if not counts: 
                await ctx.send(f"No one has said \"{phrase}\" yet...")
                return
                
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse =True)
            top_results = "\n".join(f"**{name}** - {count} times" for name, count in sorted_counts[:10])
            grd_total = 0
            for name, count in sorted_counts:
                grd_total += count

            await ctx.send(f"\"{phrase}\" has been sent {grd_total} times! heres a leaderboard: \n{top_results}")
                
    except Exception as e:
        await ctx.send(f"⚠️ Error while counting phrase: {e}")

@bot.command()
async def longest_average(ctx):
    """
    finds the tupper with the longest average message length
    command: coffee: longest_average
    """
    target_db = server_find(ctx.guild.id)
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')
        return
    try: 
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT char_name, AVG(LENGTH(content)) AS avg_length
            FROM messages
            GROUP BY char_name
            ORDER BY avg_length DESC
            LIMIT 20
            
        """)

        result = cursor.fetchall()
        conn.close()
        
        if result:
            leadb = ''
            for char_name, avg_length in result:
                leadb += (f"**{char_name}**: {round(avg_length, 2)} characters \n")
            await ctx.send(f"top 20 yappers:\n {leadb}")
        else:
            await ctx.send("no messages found.")
    except Exception as e:
        await ctx.send(F"An error occured: {e}")            

@bot.command()
async def sthread(ctx, thread: discord.Thread):
    """
    Scrapes messages from a specific thread only, with rate limit safety.
    Usage: coffee: scrape_thread #thread-name
    """
    target_db = server_find(ctx.guild.id)
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')
        return
    result = await auth_user(ctx, target_db)
    if result == 2:
        return
    
    await ctx.send(f"Remembering the good times from {thread.name}...")

    count = 0
    async for message in thread.history(limit=None):
        if message.webhook_id is not None:
            char_name = message.author.name
            content = message.content
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            channel_name = message.channel.name
            if isinstance(message.channel, discord.Thread) and message.channel.parent:
                channel_name = message.channel.parent.name

            with sqlite3.connect(target_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 1 FROM messages WHERE char_name = ? AND content = ? AND timestamp = ? AND channel_name = ?
                """, (char_name, content, timestamp, channel_name))

                if cursor.fetchone() is None:
                    cursor.execute("""
                        INSERT INTO messages (char_name, content, timestamp, channel_name)
                        VALUES (?, ?, ?, ?)
                    """, (char_name, content, timestamp, channel_name))
                    count += 1

            # 💤 Prevent rate limits every 50 messages
            if count % 50 == 0:
                await asyncio.sleep(1)

    await ctx.send(f"✅ Remebered {count} messages from thread: {thread.name}")

@bot.command()
async def scrape_from(ctx, *, since: str):
    '''
    Scrapes from a list of designated channels and threads after specific date
    Example: coffee: scrape_from 2025-04-20 13:45
    '''
    target_db = server_find(ctx.guild.id)
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')
        return
    result = await auth_user(ctx, target_db)
    if result == 2:
        return
    try:
        since_dt = datetime.datetime.strptime(since, "%Y-%m-%d %H:%M")

        #STORE CHANNELS HERE
        designated_channel_ids = [
            #1347331669371125940,  # Replace with your channel IDs
            #1333126407819100245,
            #1333126458247479379,
            #1348054596999712828,
            #1348054634471620780,
            #1348054707184074862,
            #1348054736024375462,
            #1358485739154964572,
            #1348049895897956473,
            #1348049946594639955,
            #1348049991968624744,
            #1348050051523416095,
            #1348050107546730506,
            #1348050132343717908,
            #1348050170348175381,
            #1347335979295313931,
            #1347336033725055008,
            #1347336059557777500,
            #1347336085889486882,
            #1347336113274228776,
            #1347336310440071301,
            #1347336144106553505,
            #1347336167909228614,
            #1347336194140405820,
            #1347336218140082356,
            #1347336242445947021,
            #1348052535142907964,
            #1348052472845045760,
            #1348052560426045523,
            #1348052588158914620,
            #1348052609130303518,
            #1348053296413409331,
            #1348053328696840223,
            #1348053360808296548,
            #1341163088757522452,
            #1348055404365479976,
            #1348055575308537856,
            #1348055638475014154,
            #1394035389919920218,
            #1394035414402203668,
            #1394036402911707267,
            #1394036554967814268,
            #1394036626040033401
            #1394036476190261362

        ] 

        total_count = 0

        for channel_id in designated_channel_ids:
            channel = bot.get_channel(channel_id)
            if channel is None:
                await ctx.send(f" couldn't access {channel_id}.")
                continue

            await ctx.send(f"Rembering from {channel.name}...")

            count = await scrape_one_channel(channel, since_dt)
            total_count += count
            
            threads = channel.threads 
            for thread in threads:
                count = await scrape_one_channel(thread, since_dt)
                total_count += count
            await asyncio.sleep(1)
        
        await ctx.send(f"Scraped a total of {total_count} messages from designated channels and threads since {since_dt}.")

    except ValueError:
        await ctx.send("Invalid date format! Use YYYY-MM-DD HH:MM.")

async def scrape_one_channel(channel, since_dt):
    target_db = server_find(ctx.guild.id)
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')
        return
    result = await auth_user(ctx, target_db)
    if result == 2:
        return
    
    count = 0
    async for message in channel.history(limit=None, after=since_dt):
        if message.webhook_id is not None:
            char_name = message.author.name
            content = message.content
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')

            channel_name = channel.name
            if isinstance(channel, discord.Thread) and channel.parent:
                channel_name = channel.parent.name

            with sqlite3.connect(target_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 1 FROM messages WHERE char_name = ? AND content = ? AND timestamp = ? AND channel_name = ?
                """, (char_name, content, timestamp, channel_name))

                if cursor.fetchone() is None:
                    cursor.execute("""
                        INSERT INTO messages (char_name, content, timestamp, channel_name)
                        VALUES (?, ?, ?, ?)
                    """, (char_name, content, timestamp, channel_name))
                    count += 1
        if count % 50 == 0:
            await asyncio.sleep(1)
    
    return count
@bot.command()
async def heatmap(ctx):
    """used as an analytic to show what hours of the day have the most activity"""
    target_db = server_find(ctx.guild.id)
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')
        return
    try:
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT strftime('%H', datetime(timestamp, '-7 hours')) AS hour, COUNT(*) AS message_count 
            FROM messages
            GROUP BY hour
            ORDER BY hour ASC
        """)

        result = cursor.fetchall()
        conn.close()

        if result:
            output = "Activity by Hour (PST): \n"
            for hour, count in result:
                output += f"**{hour}:00** {count} messages \n"
            await ctx.send(output)
        else: 
            await ctx.send("no messages found to analyze!")

    except Exception as e:
        await ctx.send(f"Error while generating heatmap: {e}")

@bot.command()
async def reply_cutoff(ctx): #cleans the code
    target_db = server_find(ctx.guild.id)
    if target_db is None:
        await ctx.send(f'Server not detected! please setup server with Coffee setup')
        return
    result = await auth_user(ctx, target_db)
    if result == 2:
        return
    try:
        conn = sqlite.connect(target_db)
        cursor = conn.cursor()

        cursor.execute("SELECT rowid, content FROM messages")
        rows = cursor.fetchall()

        total_checked = 0
        total_cleaned = 0

        for rowid, content in rows:
            lines = content.split('\n')
            total_checked += 1

            if len(lines) >= 2 and lines[0].startswith('> [Reply to]'):
                cleaned_content = '\n'.join(lines[2:])

                cursor.execute("UPDATE messages SET content = ? WHERE rowid = ?", (cleaned_content, rowid))
                total_cleaned += 1 
                if total_cleaned % 100 == 0: 
                    print(f"Cleaned {total_cleaned} messages so far...")

        await ctx.send(f"{total_checked} messages were checked and {total_cleaned} messages are about to be edited. if you are sure you want to do this {ctx.author.mention}? type YES/NO to confirm.")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
 
        try: 
            msg = await bot.wait_for("message", check=check, timeout=30.0)
            content = msg.content

            if content == "YES":
                await ctx.send("confirmed, data has been cleaned!")
                conn.commit()
                conn.close()
            elif content == "NO":
                await ctx.send("Action aborted.")
                return
            else:
                await ctx.send("I dont think I understand you, please run this command again.")

        except asyncio.TimeoutError: 
            await ctx.send("You took to long, nevermind...")
            return

    except Exception as e:
        await ctx.send(f"Error during reply cleanup: {e}")

      
        



bot.run(TOKEN)
