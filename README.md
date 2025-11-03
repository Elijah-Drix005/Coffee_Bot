Hello! this is my bot made as a way for me to learn python and SQL. 
as a avid user of discord, I thought being able to find a way to archive messages through the application would give me a good chance to collect both a wide array of data, preform various analysis
and at the same time, learn github! (hence why I am here) im not sure where this bot is going to go as of yet, but if you are reading this you likely have taken some interest in my work 
keep in mind, this is my first project, so many issues will likely arrive as I get comfortable with it

AS OF 10/29/30:
decided to fully commit to this project, bot in its current state is able to manually collect data through in message commands with manual input, 
-(errors arrise when collecting repeat messages though, will look into)
-server I used for this "experiment" is effectively dead, but it does leave me with a data base of ~15k messages do use for analysis should be good for honing functions of bot

-KEY GOALS:
>bot needs to be run through mac os, eventually want to make running, dependent thus on me. options to fix seem like they would all require some investment, so requires more private experiments
>messages all only save to one data base, easy for my own colletion, but if wanting to see full implementation as a bot, will ofcourse need to find way to make server unique databases, alongside this. channel ID implementation must be manually inserted into code, intend to make a longer setup process that allows to set these features up without my input.
>want to eventually aim for ~50 (currently 4/50) analysis commands that users can input through bot to indicate activity, trends, etc. also maybe even to figure out how to create AI versions of characters (ethics need to be checked on that)
>TL;DR: want to transition from MY tool to USABLE bot. to get more testing need to make appealing features 

BOT.PY FUNCTIONS:

-Scrape: collects all webhooks from a mentioned channel in the command but collects character name, the message, when it was sent
and the channel its sent in), updates user on what server its on and how many messages collected
ISSUES: currently freezes when going over duplicate messages, made obselete by scrapefrom
TODO: want to make message collection more user friendly, or automatic, and fix dupe issue

-num: gives the number of messages a specific tupper has sent. 
ISSUES: tupper requires exact name mention, if people deicde to change tupper name, multiple tuppers indicating same character, bot displays inaccurate count. 
TODO:this issue coincides with a data cleaning/organization issue

-word_count: gives the exact time a specific word was mention from a character. is able to discern different variations "abob", "BOB", "bob", "xBOBx" all count as "bob" when looking through data
ISSUES: of course if common word stems are looked up ("it" would detect an entry in titanic" for ex) data is inaccurate
TODO: more narrow parameters for word searching, yet have to consider fact that users formatting complicates this (if a users did **word** I need it to still count) 

-longest_average: gives a leaderboard of the top 20 message senders and their message count)
iSSUES: none as of right now 
TODO: possibly want to implement a manually implementable leaderboard length (like if you only want top 5)

-sthread: intends to escape a specific thread, intended for thread based server
ISSUES: base scrape effectively does this as well, little need for this command
TODO:find use for this function 

-scrape_from: upgrade of scrape, automatically scrapes from specified date time from all channels in list specified in commang, 
ISSUES: same as scrape, kind of a pain to use. specified channel IDS makes it highly incovenient
TODO: plays into main development. likely need to create a method of mutliple data bases (one to indicate data base used for channel + a passcode to be able to authorize an admin to use scrape commands + included channel IDS, another for the database itself) 

-soft_reset: intended to delete all mesages before a given date 
ISSUES: none with comamnd itself (as it seems)
TODO: no issue with command as of right now, does what is needed

-scrape_one_channel: designed to be functionally same as scrape, was an oversight in coding process,
TODO: figure out which one is needed, if either are really needed

-heatmap: designed to show what hours of the days have the most activity by scraping timestamps of database
ISSUE: only generalizes in PST, formatting is also suboptimal 
TODO: find a way to customize what time it is displayed in, fix formatting of output

CODECLEAN.PY:

>this function is ran just to clean data, namely funtions right now by finding which messages are replys (as when collected data they contain weird formatting that displays confouding entries such as original message previews and names). funciton is effective at getting rid of these, but realize that there is benefit in indicating what message is a reply to what.
-TODO:
>find alternate way to handle REPLYS (likely inserting a new column in databases that defaults NA)
>make this function a part of bot.py so it can be ran internally rather than needing to run externally
>how users format messages needs to be considered (emojis, punctuation, bolding messages, etc) likely the largest task of this function, but I believe keeping as is can lead to benefits in ML training

WEEKLY GOALS: 

-create 3 new analysis commands, and verify full functionality of existing ones
-go through code and add comments for my reunderstanding of code
-integrate codeclean into bot, create function that allows for combining of name terms (so multiple tuppers adressing same character can be treated as one. 
-add local enviroment handling so I dont leak my bot token and can make this github public





