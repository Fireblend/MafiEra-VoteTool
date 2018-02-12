from flask import Flask
from datetime import datetime
import urllib.request
from requests_futures.sessions import FuturesSession

from bs4 import BeautifulSoup, SoupStrainer

############################################
####            GLOBAL VARIABLES
############################################

#Era Thread Base URL
era_url = 'https://www.resetera.com/'
base_thread_url = era_url+'threads/'

#Commands
command_vote= "vote:"
command_doublevote= "double:" # <-- this isn't implemented yet
command_unvote= "unvote"
command_day= "day"
command_begins= "begins"
command_ends= "ends"

# No active day atm
current_day = None
current_day_no = -1

# Main Day List
days = []

############################################
####     SOME USEFUL FUNCTIONS
############################################

message_list_strainer = SoupStrainer("div", {"class" : ["messageContent", "messageUserInfo", "postCount"]})

# Returns a soup object from a URL
def getSoup(url, isMessage=False):
    print("REQUESTING: "+url)
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    f = urllib.request.urlopen(req)

    # Store page in variable
    if isMessage:
        result = BeautifulSoup(f, 'lxml', parse_only=message_list_strainer)
    else:
        result = BeautifulSoup(f, 'lxml')
    f.close()
    return result

# Returns a soup object from text
def getSoupFromText(f, isMessage=False):
    if isMessage:
        result = BeautifulSoup(f, 'lxml', parse_only=message_list_strainer)
    else:
        result = BeautifulSoup(f, 'lxml')
    return result

# Marks a vote as innactive
def removeActiveVote(user, day, link, post_num):
    for player in day:
        for vote in day[player]:
            if vote['sender'] == user and vote['active']:
                vote['active'] = False
                vote['unvote_link'] = link
                vote['unvote_num'] = post_num

# Adds a new vote
def addActiveVote(user, target, day, link, post_num):
    toAppend = {'sender': user, 'active': True, 'vote_link': link, 'unvote_link':None, 'vote_num': post_num, 'unvote_num':None }
    if target in day:
        day[target].append(toAppend)
    else:
        day[target] = [toAppend]

# Counts active votes from a vote list
def countActiveVotes(votes):
    activeVotes = 0
    for vote in votes:
        if(vote['active']):
            activeVotes = activeVotes+1
    return activeVotes

# The following 2 functions format the results into HTML
def htmlPrintDay(day):
    response = ""
    for player in day:
        voteList = day[player]
        response+=("<br><u>"+player+ "</u>("+str(countActiveVotes(day[player]))+" votes)<br>")
        for vote in voteList:
            if(vote['active']):
                response+=(vote['sender'] + " - <a href='"+ vote['vote_link']+"'>"+vote['vote_num']+"</a><br>")
            else:
                response+=("<strike>"+vote['sender'] + " - <a href='"+  vote['vote_link'] +"'>"+vote['vote_num']+"</a></strike>  <a href='"+ vote['unvote_link']+"'>"+vote['unvote_num']+"</a><br>")
    return response

def htmlPrint(days, current_day):
    response = ""
    for day_no in range(0, len(days)):
        response+=("<br><B> ==== DAY "+str(day_no+1)+" VOTES ==== </B><br>")
        response+=htmlPrintDay(days[day_no])
    if current_day != None:
        response+=("<br><B> ==== DAY "+str(len(days)+1)+" VOTES ==== </B><br>")
        response+=htmlPrintDay(current_day)
    return response

# The following 2 functions format the results into BBCode
def bbCodePrintDay(day):
    response = ""
    for player in day:
        voteList = day[player]
        response+=("<br>[b][u]"+player+ "[/u][/b] ("+str(countActiveVotes(day[player]))+" votes)<br>")
        for vote in voteList:
            if(vote['active']):
                response+=(vote['sender'] + " - [u][url='"+ vote['vote_link']+"']"+vote['vote_num']+"[/url][/u]<br>")
            else:
                response+=("[s]"+vote['sender'] + " - [u][url='"+  vote['vote_link'] +"']"+vote['vote_num']+"[/url][/u][/s]  [u][url='"+ vote['unvote_link']+"']"+vote['unvote_num']+"[/url][/u]<br>")
    return response

def bbCodePrint(days, current_day):
    response = ""
    for day_no in range(0, len(days)):
        response+=("<br>[b] ==== DAY "+str(day_no+1)+" VOTES ==== [/b]<br>")
        response+=bbCodePrintDay(days[day_no])
    if current_day != None:
        response+=("<br>[b] ==== DAY "+str(len(days)+1)+" VOTES ==== [/b]<br>")
        response+=bbCodePrintDay(current_day)
    return response

# This function runs on the background for each page that is loaded asynchronically.
def getSoupInBackground(sess, resp):
    # Loads the page into soup
    era_page = getSoupFromText(resp.text, True)

    #These are the posts
    posts = era_page.find_all("div", {"class" : "messageContent"})
    #These are the users
    users = era_page.find_all("div", {"class" : "messageUserBlock"})
    #These are the links
    links = era_page.find_all("div", {"class" : "postCount"})

    #Readies the data for this page in the background
    resp.data = {"posts":posts, "users":users, "links":links}

############################################
####     MAIN SCRAPING FUNCTION
############################################

def scrapeThread(thread_id):
    # Store page in variable
    thread_url = base_thread_url+thread_id
    era_page = getSoup(thread_url, False)

    # Find out how many pages there are
    pages = era_page.find("span", {"class" : "pageNavHeader"})
    nav = pages.contents[0].split(" ")
    numPages = int(nav[3])

    current_day = None
    current_day_no = -1
    days = []

    # Load pages asynchronically, I'm a mad scientist
    session = FuturesSession()
    requests = []

    for p in range(1, numPages + 1):
        # Each page request gets added to the session, as well as the getSoupInBackground
        # function which lets us do some additional stuff on the background
        page_url = thread_url + "page-" + str(p)
        requests.append(session.get(page_url, background_callback=getSoupInBackground))

    # For each page:
    for p in range(0, numPages):
        #Load the page into BeautifulSoup
        print("Loading Page "+str(p))

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
        if p == 1:
            startPost = 3

        #For each post in this page:
        for i in range(startPost, len(posts)):

            #Get the current post's content, the user, the link and the post number
            currentPost = posts[i]
            currentUser = users[i].find("a", {"class": "username"}).get_text(strip=True).lower();
            currentLink = era_url+links[i].find("a")['data-href'].partition("/permalink")[0];
            currentPostNum = links[i].find("a").string;

            #Extract quotes so we don't accidentally count stuff in quotes
            hasQuote = currentPost.findAll("div", {"class": "bbCodeBlock bbCodeQuote"})
            for quote in hasQuote: # Skips quoted posts
                quote.extract()

            #Find all potential "actions"
            action_list = currentPost.find_all("span")
            if len(action_list) > 0:
                for action in action_list:
                    #Check for color tags
                    if action.has_attr('style') and 'color' in action['style']:
                        #I'm removing bold tags here to simplify the command matching procedure
                        for match in action.findAll('b'):
                            match.replaceWithChildren()
                        #Check for valid commands
                        for line in str(action).lower().splitlines():
                            #If the day is starting, set the current day variable to a new day
                            if(command_day in line and command_begins in line):
                                day_number = str(line).lower().partition(command_day)[2].partition(command_begins)[0].strip()
                                current_day = {}
                                current_day_no = day_number
                                #print("DAY"+current_day_no+" BEGINS")
                            #If the day has ended, append the current day to the days variable and then clear it
                            elif(command_day in line and command_ends in line):
                                #print("DAY"+current_day_no+" ENDS")
                                days.append(current_day)
                                current_day = None
                                current_day_no = -1
                            #Handle unvote command
                            elif(command_unvote in line):
                                if current_day == None:
                                    continue
                                #print(currentUser+" UNVOTED"+ " ("+currentLink+")")
                                removeActiveVote(currentUser, current_day, currentLink, currentPostNum)
                            #Handle vote command
                            elif(command_vote in line):
                                if current_day == None:
                                    continue
                                target = str(line).lower().partition(command_vote)[2].partition('<')[0].strip()
                                #print(currentUser+" VOTED FOR: "+ target + " ("+currentLink+")")
                                removeActiveVote(currentUser, current_day, currentLink, currentPostNum)
                                addActiveVote(currentUser, target, current_day, currentLink, currentPostNum)

    return [days, current_day]


############################################
####     FLASK CALLBACKS
############################################
app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return ''


@app.route('/')
def home():

    response = "<br><b>MafiEra Vote Tool 3000</b><br>"
    response+= "<br><b>Usage</b>: Append the thread ID of the mafia game that needs to be scraped to the end of this page's URL.<br>"
    response+= "Note that this tool scrapes the entire thread, and it may take a while to finish loading.<br>"

    response+= "<br><b>Examples</b>:<br>"
    response+= "<a href=https://frozen-refuge-64585.herokuapp.com/berserk-mafia-ot-ceremony-of-the-eclipse.3712>https://frozen-refuge-64585.herokuapp.com/berserk-mafia-ot-ceremony-of-the-eclipse.3712</a><br>"
    response+= "<a href=https://frozen-refuge-64585.herokuapp.com/buck-bumble-mafia-lets-rock.22251>https://frozen-refuge-64585.herokuapp.com/buck-bumble-mafia-lets-rock.22251</a><br>"

    response+= "<br>This tool brought to you by <b>Fireblend</b> :)<br>"

    return response

@app.route('/<threadId>')
def homepage(threadId):
    current_day = None
    current_day_no = -1
    days = []

    res = scrapeThread(threadId+"/")

    response = "<br><b>MafiEra Vote Tool 3000</b>"
    response+= "<br><b>Game Thread</b>: <a href="+ base_thread_url+threadId+">"+base_thread_url+threadId+"</a><br><br>"
    response+= (htmlPrint(res[0], res[1]) + "<br><br><b>BBCode:</b><br>" + bbCodePrint(res[0], res[1]))

    return response

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, threaded=True)
