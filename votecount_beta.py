import re
import json
import urllib.request
import pandas as pd
import formatter
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
vt_url = 'https://vote.fireblend.com/'

#Commands
command_player_list= "!player_list"
command_dead= "((.+) has died!)"
command_won= "((.+) has won the game!)"
command_lost= "((.+) has lost the game!)"

command_vote= "vote:"
command_doublevote= "double:"
command_triplevote= "triple:"
command_unvote= "unvote"
command_day_ends= "(day (.+) ends)"
command_day_begins= "(day (.+) begins)"
command_reset = "votes have been reset"

# Dataframes
players_df = pd.DataFrame()
phases_df = pd.DataFrame()
votes_df = pd.DataFrame()

############################################
####     SOME USEFUL FUNCTIONS
############################################

#This strainer acts as a filter for the parser. We only care about divs whose classes are any of these:
message_list_strainer = SoupStrainer(["div", "header"], {"class" : ["bbWrapper", "message-userDetails", "message-attribution-opposite", "message-attribution"]})

#This is the same thing, except for OuterMafia, since some divs have different names due to the theme difference:
mo_message_list_strainer = SoupStrainer(["div", "span"], {"class" : ["messageContent", "messageUserInfo", "messageDetails", "DateTime"]})

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
def removeActiveVote(user, day, link, post_num, timestamp):
    global votes_df
    if(len(votes_df) == 0):
        return
    mask = (votes_df.sender_name==user) & votes_df.active & (votes_df.day == day)
    votes_df.loc[mask, "active"] = False
    votes_df.loc[mask, "unvote_timestamp"] = timestamp
    votes_df.loc[mask, "unvote_link"] = link
    votes_df.loc[mask, "unvote_num"] = post_num

# Adds a new vote
def addActiveVote(user, target, day, link, post_num, value, timestamp):
    global votes_df
    toAppend = {'sender_name': user,
                'target_name': target,
                'day': day,
                'active': True,
                'vote_link': link,
                'unvote_link':None,
                'vote_num': post_num,
                'unvote_num':None,
                'vote_timestamp':timestamp,
                'unvote_timestamp':None,
                'value':value }
    votes_df = votes_df.append(toAppend, ignore_index = True)

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
    #These are the timestamps
    timestamps = era_page.find_all("header", {"class" : "message-attribution"})

    #We use an alternative div name for OM since it's different there.
    if(isOM):
        posts = era_page.find_all("div", {"class" : "messageContent"})
        users = era_page.find_all("div", {"class" : "messageUserInfo"})
        links = era_page.find_all("div", {"class" : "messageDetails"})
        timestamps = era_page.find_all("span", {"class" : "DateTime"})

    #Readies the data for this page in the background
    resp.data = {"posts":posts, "users":users, "links":links, "timestamps":timestamps}

############################################
####     MAIN SCRAPING FUNCTION
############################################

def scrapeThread(thread_id, om=False):
    global players_df
    global votes_df
    global phases_df

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

    print("lastPage is "+str(numPages))


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
        players_df = pd.read_csv("gamecache_2.0/"+str(thread_id).replace("/","")+"_players.csv")
        phases_df = pd.read_csv("gamecache_2.0/"+str(thread_id).replace("/","")+"_phases.csv")
        votes_df = pd.read_csv("gamecache_2.0/"+str(thread_id).replace("/","")+"_votes.csv")

        #banner_url = data["banner_url"]

        #We find out the last day end page and post numbers, so we can start scraping from that point.
        lastPage = phases_df.phase_end_page.max()
        lastPost = phases_df.phase_end_number.max()

    except Exception as e:
        print("No file found, or error loading file: ")
        print (e)

    # Load pages asynchronically, I'm a mad scientist
    session = FuturesSession(max_workers=10)
    requests = []

    for p in range(int(lastPage), numPages + 1):
        # Each page request gets added to the session, as well as the getSoupInBackground
        # function which lets us do some additional stuff on the background
        page_url = thread_url + "page-" + str(p)
        requests.append(session.get(page_url, background_callback=lambda sess, resp: getSoupInBackground(sess, resp, om)))

    # For each page:
    for p in range(0, len(requests)):
        print("Page "+str(p))
        #Wait if needed for the request to complete. By the time it's done we should have
        #access to the posts, users and links as parsed by the getSoupInBackground function
        pageData = requests[p].result().data

        #These are the posts
        posts = pageData["posts"]
        #These are the users
        users = pageData["users"]
        #These are the links
        links = pageData["links"]
        #These are the links
        timestamps = pageData["timestamps"]

        if(not om):
            i = 0
            while(i != len(links)):
                lstr = links[i].find("a")['href'].partition("/permalink")[0]
                if("#" in lstr or "threadmarks" in lstr):
                    links.pop(i)
                    i = i - 1
                i = i+1

        # If there are no active phases yet, grab banner url
        if (len(phases_df) == 0):
            img = posts[0].find("img")
            if(img != None and img.has_attr('src')):
                banner_url = img["src"]
                if '/' == banner_url[-1]:
                    banner_url[-1] = ' '
                print(banner_url)

        #For each post in this page:
        for i in range(0, len(posts)):
            nextPost = False
            #Get the current post's content, the user, the link, timestamp and the post number
            currentPost = posts[i]
            currentUser = users[i].find("a", {"class": "username"}).get_text(strip=True).lower()
            currentLink = era_url+links[i].find("a")['href'].partition("/permalink")[0]
            currentTimestamp = timestamps[i].find("time")['datetime']

            if (om):
                currentLink = om_url+links[i].find("a")['data-href'].partition("/permalink")[0]
                currentTimestamp = timestamps[i].find("span")['title']

            currentPostNum = links[i].find("a").string;

            try:
                current_phase_info = phases_df.loc[phases_df.phase_number.idxmax()]
                phaseNum = phases_df.phase_number.max()
            except Exception as e:
                current_phase_info = pd.DataFrame()
                phaseNum = 0

            # Increment post count only if the latest phase is active
            if(len(current_phase_info) > 0 and pd.isnull(phases_df.loc[phases_df.phase_number.idxmax(), "phase_end_link"])):
                if(len(players_df) > 0 and len(players_df[players_df.name == currentUser]) > 0):
                    players_df.loc[players_df.name == currentUser, "post_count_"+str(current_phase_info.phase_number)] += 1
                else:
                    players_df = players_df.append({"name":currentUser, "post_count_"+str(current_phase_info.phase_number):1}, ignore_index = True)


            currentPostInt = int(currentPostNum.replace("#", "").replace(",", "").strip())
            # If we set a last day end post, meaning we loaded some previous game data,
            # skip all posts until the one after it, by comparing post numbers.
            if (lastPost != None):
                #Ignore the post if its number is lower than last post
                if(currentPostInt <= lastPost):
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

                                #This is to use the day identifier as part of the title
                                #of this day phase in the view of the data.
                                m = re.search(command_day_begins, line, re.IGNORECASE)
                                current_day_name = m.group(2)

                                phaseNum = 0

                                if(len(current_phase_info) > 0):
                                    phaseNum = current_phase_info.phase_number+1

                                new_day_info = {"phase_name":current_day_name, "phase_start_link":currentLink, "phase_start_number":currentPostInt, "phase_start_page":p+lastPage, "phase_start_timestamp":currentTimestamp, "phase_number":phaseNum, "phase_end_link":pd.np.nan, "phase_end_number":pd.np.nan, "phase_end_page":pd.np.nan, "phase_end_timestamp":pd.np.nan}
                                phases_df = phases_df.append(new_day_info, ignore_index = True)

                                current_phase_info = phases_df.loc[phases_df.phase_number.idxmax()]
                                players_df["post_count_"+str(current_phase_info.phase_number)] = 0
                                nextPost = True
                                break
                            #If the day has ended, append the current day to the days variable and then clear it
                            if(bool(re.search(command_day_ends, line, re.IGNORECASE))):
                                if len(current_phase_info) == 0:
                                    continue
                                print("Day ends on "+currentPostNum)
                                phases_df.loc[phases_df.phase_number.idxmax(), "phase_end_link"] = currentLink
                                phases_df.loc[phases_df.phase_number.idxmax(), "phase_end_number"] = currentPostInt
                                phases_df.loc[phases_df.phase_number.idxmax(), "phase_end_page"] = p+lastPage
                                phases_df.loc[phases_df.phase_number.idxmax(), "phase_end_timestamp"] = currentTimestamp

                                #Update this game's cache files with day info
                                phases_df.to_csv("gamecache_2.0/"+str(thread_id).replace("/","")+"_phases.csv",index=False)
                                players_df.to_csv("gamecache_2.0/"+str(thread_id).replace("/","")+"_players.csv",index=False)
                                votes_df.to_csv("gamecache_2.0/"+str(thread_id).replace("/","")+"_votes.csv",index=False)

                                break
                            #Handle vote reset command
                            elif(command_reset in line):
                                if len(current_phase_info) == 0:
                                    continue

                                votes_df = votes_df.drop(votes_df[votes_df.day == current_phase_info.phase_number].index)

                                print("Votes have been reset!")
                                nextPost = True
                                break
                            #Handle unvote command
                            elif(command_unvote in line):
                                if len(current_phase_info) == 0:
                                    continue
                                print(currentUser+" UNVOTED")
                                removeActiveVote(currentUser, phaseNum, currentLink, currentPostInt, currentTimestamp)
                            #Handle vote command
                            elif(command_vote in line):
                                if len(current_phase_info) == 0:
                                    continue
                                target = str(line).lower().partition(command_vote)[2].partition('<')[0].strip()
                                print(currentUser+" -> "+ target)
                                removeActiveVote(currentUser, phaseNum, currentLink, currentPostInt, currentTimestamp)
                                addActiveVote(currentUser, target, phaseNum, currentLink, currentPostInt, 1, currentTimestamp)
                            #Handle doublevote command
                            elif(command_doublevote in line):
                                if len(current_phase_info) == 0:
                                    continue
                                target = str(line).lower().partition(command_doublevote)[2].partition('<')[0].strip()
                                print(currentUser+" ->> "+ target)
                                removeActiveVote(currentUser, phaseNum, currentLink, currentPostInt, currentTimestamp)
                                addActiveVote(currentUser, target, phaseNum, currentLink, currentPostInt, 2, currentTimestamp)
                            #Handle triple vote command
                            elif(command_triplevote in line):
                                if len(current_phase_info) == 0:
                                    continue
                                target = str(line).lower().partition(command_triplevote)[2].partition('<')[0].strip()
                                print(currentUser+" ->>> "+ target)
                                removeActiveVote(currentUser, phaseNum, currentLink, currentPostInt, currentTimestamp)
                                addActiveVote(currentUser, target, phaseNum, currentLink, currentPostInt, 3, currentTimestamp)
                                
    return formatter.format(votes_df, players_df, phases_df)
