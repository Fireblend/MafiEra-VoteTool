import re
import json
import urllib.request
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
om_url = 'https://outermafia.com/'
om_thread_url = om_url+'index.php?threads/'

#Vote Tool Base URLs
vt_url = 'https://vote.fireblend.com/move/'

#Commands
command_move= "move:"
command_day_ends= "(day (.+) ends)"
command_day_begins= "(day (.+) begins)"

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

############################################
####     SOME USEFUL FUNCTIONS
############################################

#This strainer acts as a filter for the parser. We only care about divs whose classes are any of these:
message_list_strainer = SoupStrainer("div", {"class" : ["bbWrapper", "message-userDetails", "message-attribution-opposite"]})

#This is the same thing, except for OuterMafia, since some divs have different names due to the theme difference:
mo_message_list_strainer = SoupStrainer("div", {"class" : ["messageContent", "messageUserInfo", "messageDetails"]})

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
def removeActiveVote(user, day, link, post_num):
    for player in day:
        for vote in day[player]:
            #There should only be one active vote per player at a time
            #so once we find an active vote with the specified user as the sender,
            #we mark it as inactive and update its unvote data.
            if vote['sender'] == user and vote['active']:
                vote['active'] = False
                vote['unvote_link'] = link
                vote['unvote_num'] = post_num

# Adds a new vote
def addActiveVote(user, target, day, link, post_num, value=1):
    toAppend = {'sender': user, 'active': True, 'vote_link': link, 'unvote_link':None, 'vote_num': post_num, 'unvote_num':None, 'value':value }
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
    links = era_page.find_all("div", {"class" : "message-attribution-opposite"})

    #We use an alternative div name for OM since it's different there.
    if(isOM):
        posts = era_page.find_all("div", {"class" : "messageContent"})
        users = era_page.find_all("div", {"class" : "messageUserInfo"})
        links = era_page.find_all("div", {"class" : "messageDetails"})

    #Readies the data for this page in the background
    resp.data = {"posts":posts, "users":users, "links":links}

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
        pages = era_page.find("span", {"class" : "pageNavHeader"})
        if(pages != None):
            nav = pages.contents[0].split(" ")
            numPages = int(nav[3])
    else:
        aList = era_page.find_all('a', {'class':'pageNavSimple-el pageNavSimple-el--current'})
        for a in aList:
            numPages = int(a.get_text(strip=True).split(" of ")[1])
            break

    #Let's initialize some variables with empty values
    current_day = None
    current_day_info = None
    current_day_posts = None
    current_day_name = None
    days = []
    days_info = []
    days_posts = []

    #Banner
    banner_url = None

    #By default, the scraper should start scanning on page 1, and have no
    #reference to the last day end post scanned.
    lastPage = 1
    lastPost = None

    #Check if there's a file corresponding to this game already
    #if so, we load all game info and set variables so the scraper knows
    #which page and post to start scraping from.
    try:
        file = open("gamecache/track_"+thread_id.replace("/", "")+".json", "r")
        text = file.read()
        data = json.loads(text)
        days = data["days"]
        days_info = data["days_info"]
        days_posts = data["days_posts"]
        banner_url = data["banner_url"]
        #We find out the last day end page and post numbers, so we can start scraping from that point.
        lastPage = days_info[len(days_info)-1]['page_end']
        lastPost = days_info[len(days_info)-1]['day_end_n']

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

        #Let's skip the first 3 posts in the thread (usually rules)
        startPost = 0
        if p+lastPage == 1:
            #Try to grab a banner from the first post
            img = posts[0].find("img")
            if(img != None and img.has_attr('src')):
                banner_url = img["src"]
                if '/' == banner_url[-1]:
                    banner_url[-1] = ' '
                startPost = 3

        #For each post in this page:
        for i in range(startPost, len(posts)):
            nextPost = False
            #Get the current post's content, the user, the link and the post number
            currentPost = posts[i]
            currentUser = users[i].find("a", {"class": "username"}).get_text(strip=True).lower();
            currentLink = era_url+links[i].find("a")['href'].partition("/permalink")[0];
            if (om):
                currentLink = om_url+links[i].find("a")['data-href'].partition("/permalink")[0];
            currentPostNum = links[i].find("a").string;

            if current_day_posts != None:
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
            hasQuote = currentPost.findAll("div", {"class": " bbCodeBlock bbCodeBlock--expandable bbCodeBlock--quote"})
            if(om):
                hasQuote = currentPost.findAll("div", {"class": "bbCodeBlock bbCodeQuote"})
            for quote in hasQuote: # Skips quoted posts
                quote.extract()

            #Find all potential "actions"
            action_list = currentPost.find_all("span")
            if(om):
                action_list = currentPost.find_all("strong")
            if len(action_list) > 0:
                for action in action_list:
                    if nextPost:
                        break
                    #Check for color tags
                    if (action.has_attr('style') and 'color' in action['style']) or (action.has_attr('class') and 'bbHighlight' in action['class']):
                        #I'm removing bold tags here to simplify the command matching procedure
                        for match in action.findAll('b'):
                            match.replaceWithChildren()
                        #Check for valid commands
                        for line in str(action).lower().splitlines():
                            if nextPost:
                                break
                            #If the day is starting, set the current day variable to a new day
                            if(bool(re.search(command_day_begins, line, re.IGNORECASE))):
                                print("New day begins on post "+currentPostNum+"("+currentLink+")")

                                print(line)

                                #This is to use the day identifier as part of the title
                                #of this day phase in the view of the data.
                                m = re.search(command_day_begins, line, re.IGNORECASE)
                                current_day_name = m.group(2)

                                #Initialize new variables for the new day.
                                current_day_posts = {}
                                current_day_info = {"day_name":current_day_name, "day_start_l":currentLink, "day_end_l":None, "day_start_n":currentPostNum, "day_end_n":None, "page_start":p, "page_end":None}
                                current_day = {}
                                nextPost = True
                                break
                            #If the day has ended, append the current day to the days variable and then clear it
                            if(bool(re.search(command_day_ends, line, re.IGNORECASE))):
                                if current_day == None:
                                    continue
                                print("Day ends on "+currentPostNum+"("+currentLink+")")
                                current_day_info['day_end_l'] = currentLink
                                current_day_info['day_end_n'] = currentPostNum
                                current_day_info['page_end'] = p+lastPage

                                #Add the gathered data to the big response variables
                                days.append(current_day)
                                days_info.append(current_day_info)
                                days_posts.append(current_day_posts)

                                #Update this game's file with day info
                                try:
                                    file = open("gamecache/track_"+thread_id.replace("/", "")+".json", "w")
                                    text = json.dumps({"days":days, "days_info":days_info, "days_posts":days_posts, "banner_url":banner_url})
                                    file.write(text)
                                    file.close()
                                except Exception as e:
                                    print("No file found, or error loading file: ")
                                    print (e)

                                #Set day-related variables to none, since we're not in an active day phase
                                current_day = None
                                current_day_info = None
                                current_day_posts = None
                                current_day_name = None
                                nextPost = True
                                break
                            #Handle vote command
                            elif(command_move in line):
                                if current_day == None:
                                    continue
                                target = str(line).lower().partition(command_move)[2].partition('<')[0].strip()
                                print(currentUser+" VOTED FOR: "+ target + " (Post: "+str(currentPostNum)+", Link: "+currentLink+")")
                                removeActiveVote(currentUser, current_day, currentLink, currentPostNum)
                                addActiveVote(currentUser, target, current_day, currentLink, currentPostNum)

    if(current_day != None):
        days.append(current_day)
        days_info.append(current_day_info)
        days_posts.append(current_day_posts)

    return {"days":days, "days_info":days_info, "days_posts":days_posts, "banner_url":banner_url}
