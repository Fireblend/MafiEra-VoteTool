import re
import json
import urllib.request
import dateutil.parser
from datetime import datetime
from requests_futures.sessions import FuturesSession

from bs4 import BeautifulSoup, SoupStrainer

############################################
####            GLOBAL VARIABLES
############################################

#Era Base URLs
era_url = 'https://www.resetera.com/'
base_thread_url = era_url+'threads/'

#Outer Mafia Base URLs
om_url = 'https://outermafia.com'
om_thread_url = om_url+'/index.php?threads/'

#Vote Tool Base URLs
vt_url = 'https://vote.fireblend.com/'

#Commands
command_vote= "vote:"
command_vote_num= "(vote(\d+):)"
command_vote_nk= "vote: no kill"
command_doublevote= "double:"
command_triplevote= "triple:"
command_unvote= "unvote"
command_day_ends= "(day (.+) ends)"
command_day_begins= "(day (.+) begins)"
command_reset = "votes have been reset"

command_checkpoint= "checkpoint"
command_players= "!player_list"
command_pairs= "!pair_list"
command_death= "((.+) has died)"
command_victory= "((.+) has won)"
command_player= "(\[(.+)\] (.+) - (.+))"
command_player_nick= "((.+)\|(.+))"
command_pair= "(.+) and (.+)"
command_replaced= "(\[(.+)\] (.+) - (.+) has replaced (.+))"

# No active day atm
current_day = None

# Main Day List

# This list is an ordered LIST OF DAYS.
# Each DAY is a dictionary, with PLAYER NAMES as the keys and a LIST OF VOTES as the value.

# Each VOTE is a dictionary with the following properties:
#       sender:         the player who made the vote
#       active:         a boolean value that marks whether the vote is active or not
#       value:          a number that expresses the value of the vote (set to 1 by default, unless the double or triple command is used)
#       vote_link:      a link to the vote post
#       vote_num:       the post number of the vote
#       unvote_link:    None if the vote is active, or a link to the post that made it inactive (either an unvote command, or a vote for another player)
#       unvote_num:     None if the vote is active, or the post number of the post that made it inactive.

days = []

# Day Info List
# Stores a LIST of DAY INFO dictionaries. each DAY INFO contains the following properties:
#       day_start_l:    link to the day start post
#       day_end_l:      link to the day end post
#       day_start_n:    number of the day start post
#       day_start_n:    number of the day end post
#       page_start:     page number where the day start post is located
#       page_end:       page number where the day end post is located

days_info = []


# Day Info List
# Stores a LIST of POST COUNT dictionaries. Each POST COUNT dictionary correspond to one day.
# Each POST COUNT dictionary uses PLAYER NAMES as keys, and a number (of posts) as its value.

days_posts = []

# players
# General player info dictionary
#       pronouns:       Preferred player pronouns
#       timezone:       Timezone
#       replaces:       If this player is a replacement, who they are replacing
#       status:         Alive, Dead, Replaced
#       death_post:     Role flip post number
#       partner:        Partner for pair games

players = {}

# other_actions
# A list of other actions (dictionaries) to be shown in a timeline
#       sender
#       target
#       action
#       phase
#       timestamp

other_actions = []

############################################
####     SOME USEFUL FUNCTIONS
############################################

#This strainer acts as a filter for the parser. We only care about divs whose classes are any of these:
message_list_strainer = SoupStrainer(["div", "ul"],  {"class" : ["bbWrapper", "message-userDetails", "message-attribution-opposite message-attribution-opposite--list", "message-attribution-main"]})

#This is the same thing, except for OuterMafia, since some divs have different names due to the theme difference:
mo_message_list_strainer = SoupStrainer(["a", "time", "div"],  {"class" : ["u-concealed", "username", "u-dt", "bbWrapper","message-userDetails" ]})

# Returns a soup object from a URL
def getSoup(url, isMessage=False, isOM=False):
    #Load URL using Request library
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    f = urllib.request.urlopen(req)
    #Transform it into a Soup object
    result = getSoupFromText(f, isMessage, isOM)
    f.close()
    return result

# Returns a soup object from text
def getSoupFromText(f, isMessage=False, isOM=False):
    #If it's a thread page (isMessageFlag), we use the strainer we defined to only parse
    #what we care about. If not, we parse the entire page.

    #Use the OuterMafia strainer if this is an OM page.
    if isMessage and isOM:
        result = BeautifulSoup(f, 'lxml', parse_only=mo_message_list_strainer)
    #If not, use the regular strainer.
    elif isMessage:
        result = BeautifulSoup(f, 'lxml', parse_only=message_list_strainer)
    else:
        result = BeautifulSoup(f, 'lxml')
    return result

# Marks a vote as innactive
def removeActiveVote(user, day, link, post_num, timestamp, store=False, other_actions=None, day_num=None):
    print(day)
    for player in day:
        for vote in day[player]:
            #There should only be one active vote per player at a time
            #so once we find an active vote with the specified user as the sender,
            #we mark it as inactive and update its unvote data.
            if vote['sender'] == user and vote['active']:
                vote['active'] = False
                vote['unvote_link'] = link
                vote['unvote_num'] = post_num
                vote['unvote_timestamp'] = timestamp
                if(store):
                    toAppend = {'sender':user, 'target':player, 'action':'unvote', 'post_num':post_num, 'post_link':link, 'timestamp':timestamp, 'phase':day_num}
                    other_actions.append(toAppend)

# Adds a new vote
def addActiveVote(user, target, day, link, post_num, timestamp, value=1):
    toAppend = {'action':'vote', 'target': target, 'sender': user, 'active': True, 'post_link': link, 'unvote_link':None, 'post_num': post_num, 'unvote_num':None, 'value':value, 'timestamp':timestamp, 'unvote_timestamp':None }
    if target in day:
        day[target].append(toAppend)
    else:
        day[target] = [toAppend]

# This function runs on the background for each page that is loaded asynchronically.
def getSoupInBackground(sess, resp, isOM):
    # Loads the page into soup
    era_page = getSoupFromText(resp.text, True, isOM)

    #These are the posts
    posts = era_page.find_all("div", {"class" : "bbWrapper"})
    #These are the users
    users = era_page.find_all("div", {"class" : "message-userDetails"})
    #These are the links
    links = era_page.find_all("ul", {"class" : "message-attribution-opposite message-attribution-opposite--list"})
    #These are the timestamps
    timestamps = era_page.find_all("div", {"class" : "message-attribution-main"})

    #We use an alternative div name for OM since it's different there.
    if(isOM):
        posts = era_page.find_all("div", {"class" : "bbWrapper"})
        users = era_page.find_all("div", {"class" : "message-userDetails"})
        links = era_page.find_all("a", {"class" : "u-concealed"})
        timestamps = era_page.find_all("time", {"class" : "u-dt"})

    #Readies the data for this page in the background
    resp.data = {"posts":posts, "users":users, "links":links, "timestamps":timestamps}

############################################
####     MAIN SCRAPING FUNCTION
############################################

def scrapeThread(thread_id, om=False):
    # Store page in variable
    thread_url = base_thread_url+thread_id
    if om:
        thread_url = om_thread_url+thread_id
    era_page = getSoup(thread_url, False)

    # Find out how many pages there are
    numPages = 1

    if om:
        pages = era_page.find("a", {"class" : "pageNavSimple-el"})
        if(pages != None):
            nav = pages.contents[0].split(" ")
            numPages = int(nav[2])
    else:
        aList = era_page.find_all('a', {'class':'pageNavSimple-el pageNavSimple-el--current'})
        for a in aList:
            numPages = int(a.get_text(strip=True).split(" of ")[1])
            break

    print("lastPage is "+str(numPages))

    #Let's initialize some variables with empty values
    current_day = None
    current_day_info = None
    current_day_posts = None
    current_day_name = None
    days = []
    days_info = []
    days_posts = []
    players = {}
    other_actions = []
    countdown = None
    #Banner
    banner_url = None

    #By default, the scraper should start scanning on page 1, and have no
    #reference to the last day end post scanned.
    lastPage = 1
    lastPost = None

    checkpoint = False

    #Check if there's a file corresponding to this game already
    #if so, we load all game info and set variables so the scraper knows
    #which page and post to start scraping from.
    try:
        file = open("gamecache/"+thread_id.replace("/", "")+".json", "r")
        text = file.read()
        data = json.loads(text)
        days = data["days"]
        days_info = data["days_info"]
        days_posts = data["days_posts"]
        banner_url = data["banner_url"]
        players = data["players"]
        other_actions = data["other_actions"]

        #We find out the last day end page and post numbers, so we can start scraping from that point.
        if(len(days_info) > 0):
            if(days_info[len(days_info)-1]['page_end'] != None):
                lastPage = days_info[len(days_info)-1]['page_end']
                lastPost = days_info[len(days_info)-1]['day_end_n']
            else:
                lastPage = days_info[len(days_info)-1]['page_checkpoint']
                lastPost = days_info[len(days_info)-1]['post_checkpoint']

                current_day = days[len(days)-1]
                current_day_info =  days_info[len(days_info)-1]
                current_day_posts = days_posts[len(days_posts)-1]

                checkpoint = True

        file.close()
    except Exception as e:
        print("No file found, or error loading file: ")
        print (e)

    # Load pages asynchronically, I'm a mad scientist
    session = FuturesSession(max_workers=10)
    requests = []

    for p in range(lastPage, numPages + 1):
        # Each page request gets added to the session, as well as the getSoupInBackground
        # function which lets us do some additional stuff on the background
        page_url = thread_url + "page-" + str(p)
        requests.append(session.get(page_url, background_callback=lambda sess, resp: getSoupInBackground(sess, resp, om)))


    checkpointPage = 4

    # For each page:
    for p in range(0, len(requests)):
        #Wait if needed for the request to complete. By the time it's done we should have
        #access to the posts, users and links as parsed by the getSoupInBackground function
        pageData = requests[p].result().data

        #These are the posts
        posts = pageData["posts"]
        #These are the users
        users = pageData["users"]
        #These are the links
        links = pageData["links"]
        #These are the timestamps
        timestamps = pageData["timestamps"]

        if(not om):
            i = 0
            while(i != len(links)):
                linkBlock = links[i].findAll("li")
                link = linkBlock[len(linkBlock)-1]
                lstr = link.find("a")['href'].partition("/permalink")[0]
                if("#" in lstr or "threadmarks" in lstr):
                    links.pop(i)
                    i = i - 1
                i = i+1

        #Let's skip the first 3 posts in the thread (usually rules)
        startPost = 0
        if p+lastPage == 1:
            #Try to grab a banner from the first post
            img = posts[0].find("img")
            banner_url = img["src"]
            if '/' == banner_url[-1]:
                banner_url[-1] = ' '
            startPost = 3

            if(len(players) == 0):
                action = "span"
                if(om):
                    action = "strong"
                action_list = posts[0].find_all(action) + posts[1].find_all(action) + posts[2].find_all(action)

                pCount = 0
                cCount = 0
                for action in action_list:
                    #Check for color tags
                    if (False) or (action.has_attr('class') and 'bbHighlight' in action['class']):
                        #I'm removing bold tags here to simplify the command matching procedure
                        for e in action.findAll('br'):
                            e.extract()
                        for match in action.findAll('b'):
                            match.replaceWithChildren()
                        #Check for valid commands
                        for line in str(action).splitlines():
                            if command_players in line:
                                pCount += 1
                            elif (bool(re.search(command_player, line, re.IGNORECASE)) and pCount == 1):
                                m = re.search(command_player, line, re.IGNORECASE)
                                pronouns = m.group(2)
                                player_name = m.group(3)
                                timezone = m.group(4)
                                nickname = None
                                if(bool(re.search(command_player_nick, player_name, re.IGNORECASE))):
                                    n = re.search(command_player_nick, player_name, re.IGNORECASE)
                                    player_name = n.group(2)
                                    nickname = n.group(3)
                                players[player_name.lower()] = {"pronouns":pronouns.strip(), "name":player_name.strip(), "nickname":nickname, "timezone":timezone.strip(), "status": "alive", "flip_post":None, "replaces":None, "replaced_by":None}
                                if(nickname != None):
                                    players[nickname.lower()] = {"username":player_name.lower()}
                            elif command_pairs in line:
                                cCount += 1
                            elif (bool(re.search(command_pair, line, re.IGNORECASE)) and cCount == 1):
                                m = re.search(command_pair, line, re.IGNORECASE)
                                player_1 = m.group(1)
                                player_2 = m.group(2)
                                players[player_1.lower()]["partner"] = player_2.lower()
                                players[player_2.lower()]["partner"] = player_1.lower()
                if(len(players) > 0):
                    players["no kill"] = {"nokill":True, "name": "No kill"}
                    players["no lynch"] = {"username":"no kill"}
                    try:
                        file = open("gamecache/"+thread_id.replace("/", "")+".json", "w")
                        text = json.dumps({"days":days, "days_info":days_info, "days_posts":days_posts, "banner_url":banner_url, "players":players})
                        file.write(text)
                        file.close()
                    except Exception as e:
                        print("No file found, or error loading file: ")
                        print (e)


        #For each post in this page:
        for i in range(startPost, len(posts)):
            nextPost = False
            #Get the current post's content, the user, the link and the post number
            link = links[i]
            if(not om):
                linkBlock = link.findAll("li")
                link = linkBlock[len(linkBlock)-1]

            currentPost = posts[i]
            currentUser = users[i].find("a", {"class": "username"}).get_text(strip=True).lower();
            currentTimestamp = ""
            if (om):
                currentLink = om_url+link['href'];
                currentTimestamp = timestamps[i].get_text(strip=True)
                currentPostNum = "0"
            else:
                currentLink = era_url+link.find("a")['href'].partition("/permalink")[0];
                currentTimestamp = timestamps[i].find("time")['datetime']
                currentTimestamp = dateutil.parser.parse(currentTimestamp).strftime("%x %X")
                currentPostNum = link.find("a").string;

            currentPostNum = currentPostNum.strip()
            currentLink = currentLink.strip()

            if current_day_posts != None and (currentUser in players or len(players)==0):
                if currentUser not in current_day_posts:
                    current_day_posts[currentUser] = 1
                else:
                    current_day_posts[currentUser] += 1

            # If we set a last day end post, meaning we loaded some previous game data,
            # skip all posts until the one after it, by comparing post numbers.
            if (lastPost != None):
                currentPostInt = int(currentPostNum.replace("#", "").replace(",", "").strip())
                lastPostInt = int(lastPost.replace("#", "").replace(",", "").strip())

                #Ignore the post if its number is lower than last post
                if(currentPostInt <= lastPostInt):
                    continue
                #Mark last post as none so we don't have to make this comparison for future posts
                else:
                    lastPost = None


            #Extract quotes so we don't accidentally count stuff in quotes
            hasQuote = currentPost.findAll("div", {"class": "bbCodeBlock-expandContent"})
            if(om):
                hasQuote = currentPost.findAll("blockquote")
            for quote in hasQuote: # Skips quoted posts
                quote.extract()

            if(checkpointPage == p and i == 0 and current_day != None):
                checkpointPage += 4
                current_day_info['post_checkpoint'] = currentPostNum
                current_day_info['page_checkpoint'] = p+lastPage

                if(not checkpoint):
                    #Add the gathered data to the big response variables
                    days.append(current_day)
                    days_info.append(current_day_info)
                    days_posts.append(current_day_posts)
                else:
                    # Replace checkpointed data with new checkpointed data
                    days[len(days)-1] = current_day
                    days_info[len(days_info)-1] = current_day_info
                    days_posts[len(days_posts)-1] = current_day_posts

                #Update this game's file with day info
                try:
                    file = open("gamecache/"+thread_id.replace("/", "")+".json", "w")
                    text = json.dumps({"days":days, "days_info":days_info, "days_posts":days_posts, "banner_url":banner_url, "players":players, "other_actions":other_actions})
                    file.write(text)
                    file.close()
                except Exception as e:
                    print("No file found, or error loading file: ")
                    print (e)

            #Find all potential "actions"
            action_list = currentPost.find_all("span")
            if(om):
                action_list = currentPost.find_all("strong")
            if len(action_list) > 0:
                for action in action_list:

                    for e in action.findAll('strong'):
                        e.extract()
                    if nextPost:
                        break
                    #Check for color tags
                    if (action.has_attr('style') and 'color' in action['style']) or (action.has_attr('class') and 'bbHighlight' in action['class']):
                        #I'm removing bold tags here to simplify the command matching procedure
                        for match in action.findAll('b'):
                            match.replaceWithChildren()
                        #Check for valid commands
                        for line in str(action).splitlines():
                            origLine = line
                            line = line.lower()
                            if nextPost:
                                break

                            #Handle victory command
                            if(bool(re.search(command_victory, line, re.IGNORECASE)) and len(players)>0):

                                m = re.search(command_victory, line, re.IGNORECASE)
                                winner = m.group(2).partition('>')[2].strip()
                                winner = winner.strip().lower()

                                if not(winner in players):
                                    continue
                                if ("username" in players[winner]):
                                    winner = players[winner]["username"]

                                players[winner]["status"] = "victory"
                                players[winner]["flip_post"] = currentLink
                                if(players[winner]["replaces"] != None):
                                    second = players[winner]["replaces"]
                                    players[second]["flip_post"] = currentLink
                                toAppend = {'sender':None, 'target':winner, 'action':'victory', 'post_num':currentPostNum, 'post_link':currentLink, 'timestamp':currentTimestamp, 'phase':len(days)}
                                other_actions.append(toAppend)

                                if(current_day != None):
                                    for player in current_day:
                                        for vote in current_day[player]:
                                            if(vote["sender"]==winner.lower()):
                                                removeActiveVote(winner.lower(), current_day, currentLink, currentPostNum, currentTimestamp)

                            #Handle death command
                            if(bool(re.search(command_death, line, re.IGNORECASE)) and len(players)>0):

                                m = re.search(command_death, line, re.IGNORECASE)
                                dead = m.group(2).partition('>')[2].strip()
                                dead = dead.strip().lower()

                                if not(dead in players):
                                    continue
                                if ("username" in players[dead]):
                                    dead = players[dead]["username"]

                                players[dead]["status"] = "dead"
                                players[dead]["flip_post"] = currentLink
                                if(players[dead]["replaces"] != None):
                                    second = players[dead]["replaces"]
                                    players[second]["flip_post"] = currentLink
                                toAppend = {'sender':None, 'target':dead, 'action':'death', 'post_num':currentPostNum, 'post_link':currentLink, 'timestamp':currentTimestamp, 'phase':len(days)}
                                other_actions.append(toAppend)

                                if(current_day != None):
                                    for player in current_day:
                                        for vote in current_day[player]:
                                            if(vote["sender"]==dead.lower()):
                                                removeActiveVote(dead.lower(), current_day, currentLink, currentPostNum, currentTimestamp)

                            #Handle replacement command
                            if(bool(re.search(command_replaced, line, re.IGNORECASE)) and len(players)>0):
                                m = re.search(command_replaced, origLine, re.IGNORECASE)
                                pronoun = m.group(2)
                                newplayer = m.group(3)
                                timezone = m.group(4)
                                replaced = m.group(5).partition('<')[0].strip()
                                nickname = None
                                if(bool(re.search(command_player_nick, newplayer, re.IGNORECASE))):
                                    n = re.search(command_player_nick, newplayer, re.IGNORECASE)
                                    newplayer = n.group(2)
                                    nickname = n.group(3)

                                if ("username" in players[replaced.lower()]):
                                    replaced = players[replaced.lower()]["username"]

                                players[newplayer.lower()] = {"pronouns":pronoun, "name":newplayer, "nickname":nickname, "timezone":timezone, "status": "alive", "flip_post":None, "replaces":replaced.lower(), "replaced_by":None}
                                players[replaced.lower()]["status"] = "replaced"
                                players[replaced.lower()]["replaced_by"] = newplayer.lower()

                                if(nickname != None):
                                    players[nickname.lower()]={"username":newplayer.lower()}

                                if("partner" in players[replaced.lower()]):
                                    players[newplayer.lower()]["partner"] = players[replaced.lower()]["partner"]
                                    players[players[replaced.lower()]["partner"]]["partner"] = newplayer.lower()

                                toAppend = {'sender':replaced.lower(), 'target':newplayer.lower(), 'action':'replacement', 'post_num':currentPostNum, 'post_link':currentLink, 'timestamp':currentTimestamp, 'phase':len(days)}
                                other_actions.append(toAppend)

                                if(current_day != None):
                                    for player in current_day:
                                        for vote in current_day[player]:
                                            if(vote["sender"]==replaced.lower()):
                                                removeActiveVote(replaced.lower(), current_day, currentLink, currentPostNum, currentTimestamp)

                            #If the day is starting, set the current day variable to a new day
                            if(bool(re.search(command_day_begins, line, re.IGNORECASE))):
                                print("New day begins on post "+currentPostNum+"("+currentLink+")")
                                #This is to use the day identifier as part of the title
                                #of this day phase in the view of the data.
                                m = re.search(command_day_begins, line, re.IGNORECASE)
                                current_day_name = m.group(2)

                                #Initialize new variables for the new day.
                                current_day_posts = {}
                                current_day_info = {"day_name":current_day_name, "day_start_l":currentLink, "day_end_l":None, "day_start_n":currentPostNum, "day_end_n":None, "page_start":p, "page_end":None}
                                current_day = {}
                                nextPost = True

                                toAppend = {'sender':None, 'target':None, 'action':'day_start', 'post_num':currentPostNum, 'post_link':currentLink, 'day_name':current_day_name, 'timestamp':currentTimestamp, 'phase':len(days)}

                                other_actions.append(toAppend)

                                imgList = posts[i].findAll("img")

                                for img in imgList:
                                    if(img != None and img.has_attr('src') and ("countdown" in img["src"])):
                                        countdown = img["src"]
                                break
                            #If the day has ended, append the current day to the days variable and then clear it
                            if(bool(re.search(command_day_ends, line, re.IGNORECASE))):
                                print("Day ends on "+currentPostNum+"("+currentLink+")")
                                current_day_info['day_end_l'] = currentLink
                                current_day_info['day_end_n'] = currentPostNum
                                current_day_info['page_end'] = p+lastPage

                                if(not checkpoint):
                                    #Add the gathered data to the big response variables
                                    days.append(current_day)
                                    days_info.append(current_day_info)
                                    days_posts.append(current_day_posts)
                                else:
                                    # Replace checkpointed data with end-of-day info
                                    days[len(days)-1] = current_day
                                    days_info[len(days_info)-1] = current_day_info
                                    days_posts[len(days_posts)-1] = current_day_posts

                                toAppend = {'sender':None, 'target':None, 'action':'day_end', 'post_num':currentPostNum, 'post_link':currentLink, 'day_name':current_day_name, 'timestamp':currentTimestamp, 'phase':len(days)}
                                other_actions.append(toAppend)

                                #Update this game's file with day info
                                try:
                                    file = open("gamecache/"+thread_id.replace("/", "")+".json", "w")
                                    text = json.dumps({"days":days, "days_info":days_info, "days_posts":days_posts, "banner_url":banner_url, "players":players, "other_actions":other_actions})
                                    file.write(text)
                                    file.close()
                                except Exception as e:
                                    print("No file found, or error loading file: ")
                                    print (e)

                                imgList = posts[i].findAll("img")

                                for img in imgList:
                                    if(img != None and img.has_attr('src') and ("countdown" in img["src"])):
                                        countdown = img["src"]

                                #Set day-related variables to none, since we're not in an active day phase
                                current_day = None
                                current_day_info = None
                                current_day_posts = None
                                current_day_name = None
                                nextPost = True
                                break

                            #Handle vote reset command
                            elif(command_reset in line):
                                if current_day == None:
                                    continue
                                current_day = {}
                                print("Votes have been reset!")
                                nextPost = True
                                break
                            #Handle unvote command
                            elif(command_unvote in line):
                                if current_day == None or (not currentUser in players and len(players) > 1):
                                    continue
                                print(currentUser+" UNVOTED"+ " (Post: "+str(currentPostNum)+", Link: "+currentLink+")")
                                removeActiveVote(currentUser, current_day, currentLink, currentPostNum, currentTimestamp,store=True, other_actions=other_actions, day_num=len(days))
                            #Handle multi-value vote command_
                            elif(bool(re.search(command_vote_num, line, re.IGNORECASE))):
                                if current_day == None or (not currentUser in players and len(players) > 1):
                                    continue
                                try:
                                    m = re.search(command_vote_num, line, re.IGNORECASE)

                                    command = m.group(1)
                                    number = int(m.group(2))

                                    target = str(line).lower().partition(command)[2].partition('<')[0].strip()
                                    if not target in players and len(players) > 0:
                                        continue
                                    if ("username" in players[target]):
                                        target = players[target]["username"]

                                    print(currentUser+" VOTED ["+str(number)+"] FOR: "+ target + " (Post: "+str(currentPostNum)+", Link: "+currentLink+")")

                                    removeActiveVote(currentUser, current_day, currentLink, currentPostNum, currentTimestamp)
                                    addActiveVote(currentUser, target, current_day, currentLink, currentPostNum, currentTimestamp, number)
                                except:
                                    continue
                            #Handle vote command
                            elif(command_vote in line):
                                if current_day == None or (not currentUser in players and len(players) > 1):
                                    continue
                                target = str(line).lower().partition(command_vote)[2].partition('<')[0].strip()
                                if not target in players and len(players) > 0:
                                    continue
                                if ("username" in players[target]):
                                    target = players[target]["username"]

                                print(currentUser+" VOTED FOR: "+ target + " (Post: "+str(currentPostNum)+", Link: "+currentLink+")")

                                removeActiveVote(currentUser, current_day, currentLink, currentPostNum, currentTimestamp)
                                addActiveVote(currentUser, target, current_day, currentLink, currentPostNum, currentTimestamp)
                            #Handle doublevote command
                            elif(command_doublevote in line):
                                if current_day == None or (not currentUser in players and len(players) > 1):
                                    continue
                                target = str(line).lower().partition(command_doublevote)[2].partition('<')[0].strip()
                                if not target in players and len(players) > 0:
                                    continue
                                if ("username" in players[target]):
                                    target = players[target]["username"]
                                print(currentUser+" DOUBLE-VOTED FOR: "+ target + " (Post: "+str(currentPostNum)+", Link: "+currentLink+")")

                                removeActiveVote(currentUser, current_day, currentLink, currentPostNum, currentTimestamp)
                                addActiveVote(currentUser, target, current_day, currentLink, currentPostNum, currentTimestamp, 2)
                            #Handle triple vote command
                            elif(command_triplevote in line):
                                if current_day == None or (not currentUser in players and len(players) > 1):
                                    continue
                                if ("username" in players[target]):
                                    target = players[target]["username"]
                                target = str(line).lower().partition(command_triplevote)[2].partition('<')[0].strip()

                                if not target in players and len(players) > 0:
                                    continue

                                print(currentUser+" TRIPLE-VOTED FOR: "+ target + " (Post: "+str(currentPostNum)+", Link: "+currentLink+")")

                                removeActiveVote(currentUser, current_day, currentLink, currentPostNum, currentTimestamp)
                                addActiveVote(currentUser, target, current_day, currentLink, currentPostNum, currentTimestamp, 3)

    if(current_day != None):
        days.append(current_day)
        days_info.append(current_day_info)
        days_posts.append(current_day_posts)
    return {"days":days, "days_info":days_info, "days_posts":days_posts, "banner_url":banner_url, "players":players, "other_actions":other_actions, "countdown":countdown}
