import math

search_url = "https://www.resetera.com/search/1/?q=%2A&t=post&c[thread]=***GAMETHREAD***&c[users]=***PLAYER***&o=date"

def getThreadId(url):
    list = url.split("/")
    if(list[-1] == ""):
        return list[-2]
    return list[-1]

# The following 2 functions format the results into HTML
def htmlPrintDay(day, players):
    partners = []
    response = ""
    for player in sorted(day, key=lambda k: countActiveVotes(day[k], k, players, day), reverse=True):
        if("username" in players[player]):
            continue
        if player in partners:
            continue
        if("partner" in players[player]):
            partner = players[player]["partner"]
            partners.append(partner)
            if partner in day:
                voteList = day[player] + day[partner]
                activeVotes = countActiveVotes(day[player]) + countActiveVotes(day[partner])
            else:
                voteList = day[player]
                activeVotes = countActiveVotes(day[player])
            player_code = getPlayerElement(player, players, None, False) + " & " +  getPlayerElement(partner, players, None, False)

        else:
            voteList = day[player]
            activeVotes = countActiveVotes(day[player])
            player_code = getPlayerElement(player, players, None, False)

        #If the user has no active votes, we mark it with a special div class so we can filter it out later.
        if(activeVotes == 0):
            response += "<div class=\"not_active\">"
        response+=("<div class=\"pname\"><br><u><b>"+player_code+ "</b></u></div> ("+str(activeVotes)+" votes)<br>")
        if(activeVotes == 0):
            response += "</div>"
        response += "<div class=\"votes\">"
        for vote in voteList:
            sender = vote['sender']
            player_code = getPlayerElement(sender, players, None, False)

            vote_element = getNumElement(vote["post_num"], vote["post_link"], vote.get("timestamp", None))
            #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
            if(vote['active']):
                if (vote['value'] == 2):
                    response+=(player_code + " - "+vote_element+" (Double)<br>")
                elif (vote['value'] == 3):
                    response+=(player_code + " - "+vote_element+" (Triple)<br>")
                else:
                    response+=(player_code + " - "+vote_element+"<br>")
            else:
                vote_element = getNumElement(vote['post_num'], vote['post_link'], vote.get("timestamp", None), striked=True)
                unvote_element = getNumElement(vote['unvote_num'], vote['unvote_link'], vote.get("timestamp", None))
                if (vote['value'] == 2):
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - "+vote_element+" (Double)</strike> </div> "+unvote_element+"<br></div>")
                elif (vote['value'] == 3):
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - "+vote_element+" (Triple)</strike> </div> "+unvote_element+"<br></div>")
                else:
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code +" - "+vote_element+" </strike> </div> "+unvote_element+"<br></div>")
        response += "</div>"
    return response

# The following 2 functions format the results into HTML
def htmlPrintDaySeq(days, players, other_actions):
    response = "<br>"
    allVotes = []
    for day in days:
        for player in day:
            allVotes+=(day[player])

    if(other_actions != None):
        allVotes += other_actions


    sortedVotes = sorted(allVotes, key=lambda k: getNum(k), reverse=True)

    for vote in sortedVotes:
        sender = vote['sender']
        target = vote['target']
        player_code_sender = getPlayerElement(sender, players, None, False)
        player_code_target = getPlayerElement(target, players, None, False)

        numElement = getNumElement(vote['post_num'], vote['post_link'], vote.get("timestamp", None))


        prefix = numElement+" - <b>"
        if(vote['action'] == 'unvote'):
            response+= prefix+player_code_sender+"</b> unvoted<br>"
            continue
        elif(vote['action'] == 'replacement'):
            response+= prefix+player_code_sender+"</b> was replaced by <b>"+player_code_target +"</b> <br>"
            continue
        elif(vote['action'] == 'death'):
            response+= prefix+player_code_target+"</b> was eliminated!<br>"
            continue
        elif(vote['action'] == 'victory'):
            response+= prefix+player_code_target+"</b> won the game!<br>"
            continue
        elif(vote['action'] == 'day_start'):
            day_namex = vote["day_name"]
            if(day_namex == None):
                day_namex=""
            response+= prefix+"Day "+day_namex+" begins!</b><br><br>"
            continue
        elif(vote['action'] == 'day_end'):            
            day_namex = vote["day_name"]
            if(day_namex == None):
                day_namex=""
            response+= prefix+"Day "+day_namex+" ends!</b><br>"
            continue


        #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
        if(vote['active']):
            if (vote['value'] == 2):
                response+=  prefix+(player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Double)<br>")
            elif (vote['value'] == 3):
                response+=  prefix+(player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Triple)<br>")
            else:
                response+=  prefix+(player_code_sender + "</b> voted for <b>"+player_code_target+ "</b><br>")
        else:
            unvoteElement = getNumElement(vote['unvote_num'], vote['unvote_link'], vote['unvote_timestamp'])
            if (vote['value'] == 2):
                response+=("<div class=\"not_active\" style=\"display: inline\"><div id=\"striked\">"+ prefix+"<strike>"+player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Double)</strike> </div> (Unvote: "+unvoteElement+")<br></div>")
            elif (vote['value'] == 3):
                response+=("<div class=\"not_active\" style=\"display: inline\"><div id=\"striked\">"+ prefix+"<strike>"+player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Triple)</strike> </div> (Unvote: "+unvoteElement+")<br></div>")
            else:
                response+=("<div class=\"not_active\" style=\"display: inline\"><div id=\"striked\">"+ prefix+"<strike>"+player_code_sender + "</b> voted for <b>"+player_code_target + "</b> </strike> </div> (Unvote: "+unvoteElement+")<br></div>")
    response += "</div>"
    return response

def htmlPrintSeq(days, days_info, days_posts, players, thread_url, other_actions=None, countdown=None):
    total_days = len(days)

    response = ""
    alive = 0
    dead = 0
    alive_text = ""
    dead_text = ""


    response = "<div class=\"column1\">"
    response += htmlHeader(days[len(days)-1], days_info, days_posts, players, thread_url, countdown)
    response+=("<br><div class=\"day_title\"><B>GAME TIMELINE</B></div><br><br>")
    response+="<div class=\"day_info\">"+htmlPrintDaySeq(days, players, other_actions)
    response+="<br><br></div>"

    return response

def htmlHeader(day, days_info, days_posts, players, thread_url, countdown=None):
    if(len(players) == 0):
        return ""
    alive = 0
    dead = 0
    voting = 0
    notvoting = 0
    victory = 0
    voting_text = ""
    not_voting_text = ""
    alive_text = ""
    dead_text = ""
    victory_text = ""
    response = ""

    for key in players:
        if("username" in players[key] or "nokill" in players[key]):
            continue
        players[key]["voting"] = False
        if(players[key]["status"] == "alive"):
            alive += 1
            alive_text += players[key]["name"]+"<br>"
        elif(players[key]["status"] == "dead"):
            dead += 1
            dead_text += players[key]["name"]+"<br>"
        elif(players[key]["status"] == "victory"):
            victory += 1
            victory_text += players[key]["name"]+"<br>"

    for player in day:
        for vote in day[player]:
            if(vote["active"] and players[vote["sender"]]["status"]!="replaced"):
                players[vote["sender"]]["voting"] = True

    for key in players:
        if("username" in players[key] or "nokill" in players[key]):
            continue
        if(players[key]["voting"]):
            voting += 1
            voting_text += players[key]["name"]+"<br>"
        elif(players[key]["status"]!="replaced" and players[key]["status"]!="dead" and players[key]["status"] !="victory"):
            notvoting += 1
            not_voting_text += players[key]["name"]+"<br>"

    response+=("<br><br><b><div class='day_title'>GAME STATS</div><br></b><br>[ <abbr rel=\"tooltip\" title=\""+alive_text+"\"><b>Alive</b>: " + str(alive) + "</abbr> | <abbr rel=\"tooltip\" title=\""+dead_text+"\"><b>Dead</b>: " + str(dead) + "</abbr> | <b>Majority</b>: " + str(math.floor(alive/2+1))+" ]")
    response+=("<br>[ <abbr rel=\"tooltip\" title=\""+voting_text+"\"><b>Voting</b>: " + str(voting) + "</abbr> | <abbr rel=\"tooltip\" title=\""+not_voting_text+"\"><b>Not Voting</b>: " + str(notvoting) + "</abbr> ]")
    if(victory > 0):
        response+=("<br>[ <abbr rel=\"tooltip\" title=\""+victory_text+"\"><b>Winners</b>: " + str(victory) + "</abbr> ]")
    if(countdown != None):
        response+=("<br><br><b>Current Countdown:</b><br><img id=\"countdown\" src=\""+countdown+"\"/><br>")

    return response+"<br>"

def htmlPrint(days, days_info, days_posts, players, thread_url, countdown=None):
    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    total_days = len(days)

    response = "<div class=\"column1\">"
    response += htmlHeader(days[0], days_info, days_posts, players, thread_url, countdown)

    for day_no in range(0, len(days)):
        day_info = days_info[day_no]

        if("day_name" in day_info):
            response+=("<br><div class=\"day_title\"><B>DAY "+day_info["day_name"].upper()+" VOTES</B></div><br><br>")
        else:
            response+=("<br><div class=\"day_title\"><B>DAY "+str(total_days-day_no)+" VOTES</B></div><br><br>")
        contents = ""

        for player in sorted(days_posts[day_no], key=days_posts[day_no].get, reverse=True):
            name = player
            if(len(players) > 0):
                name = players[player]["name"]
            contents+=  name + ": "+str(days_posts[day_no][player])+"<br>"

        response+=("<a href='"+ day_info['day_start_l']+"' target=\"_blank\">Day Start</a> ")
        if(day_info['day_end_l']!= None):
            response+=("- <a href='"+ day_info['day_end_l']+"' target=\"_blank\">Day End</a>")
        response+=(" - <abbr rel=\"tooltip\" title=\""+contents+"\"><b>Post Counts</b></abbr><br>")
        if(len(days[day_no]) == 0):
            response +="<div class=\"day_info\"><br>No votes have been cast!<br>"
        else:
            response+="<div class=\"day_info\">"+htmlPrintDay(days[day_no], players)
        response+="<br></div>"
        if(day_no == 0 and len(days)>1):
            response+= "<a class=\"toggle\" onclick=\"toggleDays()\" href=\"#a\">👀 See/hide previous days</a><br>"
            response+= "<br><span class=\"old_days\">"

    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    response += "</span></div>"
    return response

# The following 2 functions format the results into BBCode
def bbCodePrintDay(day, players):
    response = ""
    partners = []
    for player in sorted(day, key=lambda k: countActiveVotes(day[k], k, players, day), reverse=True):
        if("username" in players[player]):
            continue
        if player in partners:
            continue

        print(players[player])
        if("partner" in players[player]):
            partner = players[player]["partner"]
            partners.append(partner)
            if partner in day:
                voteList = day[player] + day[partner]
                activeVotes = countActiveVotes(day[player]) + countActiveVotes(day[partner])
            else:
                voteList = day[player]
                activeVotes = countActiveVotes(day[player])
            name  = player + " & " + partner

            if len(players) > 0:
                name = players[player]["name"]+ " & " +  players[partner]["name"]

        else:
            voteList = day[player]
            activeVotes = countActiveVotes(day[player])
            player_code = getPlayerElement(player, players, None, False)
            name = player

            if len(players) > 0:
                name = players[player]["name"]

        #If the user has no active votes, we mark it with a special div class so we can filter it out later.
        if(activeVotes == 0):
            response += "<div class=\"not_active\">"


        response+=("\n[b][u]"+name+ "[/u][/b] ("+str(activeVotes)+" votes)\n")
        if(activeVotes == 0):
            response += "</div>"
        for vote in voteList:
            sender = vote['sender']
            name = sender
            if len(players) > 0:
                name = players[sender]["name"]
            #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.

            vote_string = ""
            if vote['active']:
                if vote['value']==2:
                    vote_string=(name + " - [u][url='"+ vote['post_link']+"']"+vote['post_num']+"[/url][/u] (Double)\n")
                elif vote['value']==3:
                    vote_string=(name + " - [u][url='"+ vote['post_link']+"']"+vote['post_num']+"[/url][/u] (Triple)\n")
                else:
                    vote_string=(name + " - [u][url='"+ vote['post_link']+"']"+vote['post_num']+"[/url][/u]\n")
            else:
                if vote['value']==2:
                    vote_string=("<div class=\"not_active\">[s]"+name + " - [u][url='"+  vote['post_link'] +"']"+vote['post_num']+"[/url][/u] (Double)[/s]  [u][url='"+ vote['unvote_link']+"']"+vote['unvote_num']+"[/url][/u]\n</div>")
                elif vote['value']==3:
                    vote_string=("<div class=\"not_active\">[s]"+name + " - [u][url='"+  vote['post_link'] +"']"+vote['post_num']+"[/url][/u] (Triple)[/s]  [u][url='"+ vote['unvote_link']+"']"+vote['unvote_num']+"[/url][/u]\n</div>")
                else:
                    vote_string=("<div class=\"not_active\">[s]"+name + " - [u][url='"+  vote['post_link'] +"']"+vote['post_num']+"[/url][/u][/s]  [u][url='"+ vote['unvote_link']+"']"+vote['unvote_num']+"[/url][/u]\n</div>")
            response+=vote_string

    return response

def getNumElement(number, link, timestamp, striked=False):
    if(striked):
        number = "<div id=\"striked\">"+number+"</div>"
    title = "<a href='"+ link +"' target=\"_blank\">"+ number +"</a>"
    if(timestamp != None):
        return "<abbr rel=\"tooltip\" title=\""+timestamp+"\">" + title + "</abbr>"
    return title


def getPlayerElement(sender, players, thread_url, addInfo=False, addIsoThread=None):
    if(sender == None):
        return None

    if(len(players) == 0):
        return sender

    if("nokill" in players[sender]):
        return "No kill"

    name = players[sender]["name"]
    if(players[sender]["nickname"] != None):
        name = name+" / "+players[sender]["nickname"]
    dead_icon = ""
    iso_icon = ""
    info_icon = ""
    victory_icon = ""

    if(players[sender]["status"] == "victory"):
        victory_icon = "<abbr rel=\"tooltip\" title=\"Go to victory post\">"
        victory_icon = victory_icon+"<a style=\"text-decoration:none\" href='"+  players[sender]["flip_post"] +"' target=\"_blank\">"+"🏆 "+"</a></abbr>"
    elif(players[sender]["flip_post"] != None):
        dead_icon = "<abbr rel=\"tooltip\" title=\"Go to elimination post\">"
        dead_icon = dead_icon+"<a style=\"text-decoration:none\" href='"+  players[sender]["flip_post"] +"' target=\"_blank\">"+"💀 "+"</a></abbr>"
    if(addIsoThread):
        iso_url = search_url.replace("***GAMETHREAD***", addIsoThread).replace("***PLAYER***",sender)
        iso_icon = "<abbr rel=\"tooltip\" title=\"Searchs posts in thread\">"
        iso_icon = iso_icon+"<a style=\"text-decoration:none\" href='"+  iso_url +"' target=\"_blank\">"+"🗒️"+"</a></abbr>"

    contents = "<b>"+players[sender]["name"]+"</b> "
    contents += "<br><b>Pronouns:</b> "+players[sender]["pronouns"]
    if(players[sender]["nickname"] != None):
        contents += "<br><b>Nickname:</b> "+players[sender]["nickname"]
    contents += "<br><b>Timezone:</b> "+players[sender]["timezone"]
    contents += "<br><b>Status:</b> "+players[sender]["status"]

    if(players[sender]["replaces"] != None):
        contents += "<br><b>Replacing:</b> "+players[players[sender]["replaces"]]["name"]
    if(players[sender]["replaced_by"] != None):
        contents += "<br><b>Replaced by:</b> "+players[players[sender]["replaced_by"]]["name"]
    if(addInfo):
        contents += "<br>Click for More!"
        name = "<a class=\"name\" style=\"text-decoration:none\" href='"+  thread_url + "p/"+ sender + "' target=\"_blank\">"+name+"</a>"

    player_code = "<abbr rel=\"tooltip\" title=\""+contents+"\">"+name+"</abbr>"

    return victory_icon+dead_icon+iso_icon+player_code

def bbCodePrint(days, days_info, days_posts, players, countdown=None):
    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    total_days = len(days)
    response = ""
    for day_no in range(0, len(days)):
        day_info = days_info[day_no]
        if("day_name" in day_info):
            response+=("<div class='day' id=\'day"+str(total_days-day_no)+"\'>\n[b] ==== DAY "+day_info["day_name"].upper()+" VOTES ==== [/b]\n")
        else:
            response+=("<div class='day' id=\'day"+str(total_days-day_no)+"\'>\n[b] ==== DAY "+str(total_days-day_no)+" VOTES ==== [/b]\n")
        response+=("[u][url='"+ day_info['day_start_l']+"']Day Start[/url][/u] ")
        if(day_info['day_end_l']!= None):
            response+=("- [u][url='"+ day_info['day_end_l']+"']Day End[/url][/u]")
        if(len(days[day_no]) == 0):
            response += "\n\nNo votes have been cast!\n"
        else:
            response+="\n"+bbCodePrintDay(days[day_no], players)

        if(day_no == 0 and len(players) > 0):
            not_voting_no = 0
            not_voting = "\n[b]Not voting:[/b] "
            for player in days[0]:
                for vote in days[0][player]:
                    if(vote["active"] and players[vote["sender"]]["status"]!="replaced"):
                        players[vote["sender"]]["voting"] = True

            for key in players:
                if("username" in players[key] or "nokill" in players[key]):
                    continue
                if((not players[key]["voting"] )and players[key]["status"]!="replaced" and players[key]["status"]!="dead" and players[key]["status"]!="victory"):
                    not_voting += players[key]["name"]+", "
                    not_voting_no += 1
            if(not_voting_no > 0):
                response += not_voting[:-2]+"\n"

        response+="\n[b]Post Counts:[/b]\n"
        for player in sorted(days_posts[day_no], key=days_posts[day_no].get, reverse=True):
            name = player
            if len(players) > 0:
                name = players[player]["name"]
            response+="[u]"+ name + "[/u]: "+str(days_posts[day_no][player])+"  "

        if(day_no == 0 and countdown != None):
            response+=("\n\n[b]Current Countdown:[/b]\n[img]"+countdown+"[/img]")

        response+="\n\n</div>\n\n"
    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    return response

def totalCountPrint(days_posts, players, thread_url, om=False):
    print(days_posts)
    total_posts_count = {}
    for day_no in range(0, len(days_posts)):
        for player in days_posts[day_no]:
            if player in total_posts_count:
                total_posts_count[player] += days_posts[day_no][player]
            else:
                total_posts_count[player] = days_posts[day_no][player]
    response="<br><br><b><div class=\"day_title\">PLAYERS & POST COUNTS</div></b><div class=\"day_info\">"
    for player in sorted(total_posts_count, key=total_posts_count.get, reverse=True):
        player_code = getPlayerElement(player, players, thread_url, True)

        threadId = getThreadId(thread_url)
        iso_url = search_url.replace("***GAMETHREAD***", threadId).replace("***PLAYER***",player)
        iso_icon = "<abbr rel=\"tooltip\" title=\"See posts in thread\">"
        iso_icon = iso_icon+"<a style=\"text-decoration:none\" href='"+  iso_url +"' target=\"_blank\">"+str(total_posts_count[player])+"</a></abbr>"

        response+="<br><u>"+ player_code + "</u>: "+ (iso_icon if not om else str(total_posts_count[player]))
    response+="<br></div>"
    return response

# Counts active votes from a vote list
def countActiveVotes(votes, player=None, players=None, day=None):
    activeVotes = 0
    if (player != None):
        if ("partner" in players[player]):
            partner = players[player]["partner"]
            if(partner in day):
                activeVotes = activeVotes+countActiveVotes(day[partner])

    for vote in votes:
        if(vote['active']):
            activeVotes = activeVotes+vote['value']
    return activeVotes



# The following 2 functions format the results into HTML
def htmlPrintPlayer(days, days_posts, players, player, other_actions):
    player = player.lower().strip()
    player_data = players[player]

    general = getGeneralInfo(days_posts, player_data, players, player)
    voted_for = getVotedFor(days, players, player)
    voted_by = getVotedBy(days, players, player)
    timeline = htmlTimelinePlayer(player, days, players, other_actions)

    return general, voted_for, voted_by, timeline

def getGeneralInfo(days_posts, player_data, players, player):
    totalPosts = 0
    for day_no in range(0, len(days_posts)):
        if(player in days_posts[day_no]):
            totalPosts += days_posts[day_no][player]

    response = "<h3>"+player_data["name"]+"</h3>"
    response += "<b>Pronouns:</b> "+player_data["pronouns"]
    if(player_data["nickname"] != None):
        response += "<br><b>Nickname:</b> "+player_data["nickname"]
    response += "<br><b>Timezone:</b> "+player_data["timezone"]
    response += "<br><b>Status:</b> "+player_data["status"]
    if(player_data["replaces"] != None):
        response += "<br><b>Replacing:</b> "+players[player_data["replaces"]]["name"]
    if(player_data["replaced_by"] != None):
        response += "<br><b>Replaced by:</b> "+players[player_data["replaced_by"]]["name"]
    response += "<br><b>Total posts:</b> "+str(totalPosts)
    return response

def getVotedBy(days, players, player):
    votes = []
    response = "<h3>Voted by:</h3>"
    phase = 0
    top = {}
    for day in days:
        phase+=1
        if(player in day):
            for vote in sorted(day[player], key=lambda k: getNum(k)) :
                sender = vote['sender']

                if sender in top:
                    top[sender] += 1
                else:
                    top[sender] = 1

                player_code = getPlayerElement(sender, players, None, False)
                #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
                if(vote['active']):
                    if (vote['value'] == 2):
                        response+=(player_code + " - <a href='"+ vote['post_link']+"' target=\"_blank\">"+vote['post_num']+"</a> (Double) (Day "+str(phase)+")<br>" )
                    elif (vote['value'] == 3):
                        response+=(player_code + " - <a href='"+ vote['post_link']+"' target=\"_blank\">"+vote['post_num']+"</a> (Triple) (Day "+str(phase)+")<br>")
                    else:
                        response+=(player_code + " - <a href='"+ vote['post_link']+"' target=\"_blank\">"+vote['post_num']+"</a> (Day "+str(phase)+")<br>")
                elif (vote['value'] == 2):
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['post_link'] +"' target=\"_blank\">"+vote['post_num']+"</a> (Double)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")
                elif (vote['value'] == 3):
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['post_link'] +"' target=\"_blank\">"+vote['post_num']+"</a> (Triple)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")
                else:
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['post_link'] +"' target=\"_blank\">"+vote['post_num']+"</a></strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")


    response += "<h3>Most voted by:</h3>"

    top = [(k, top[k]) for k in sorted(top, key=top.get, reverse=True)]
    for k in top:
        response += "<b>"+k[0]+" </b>" + "("+str(k[1])+")<br>"

    if(len(top) == 0):
        response+="No one!"

    return response

def getVotedFor(days, players, player):
    votes = []
    response = "<h3>Voted For:</h3>"
    phase = 0
    top = {}
    for day in days:
        phase+=1
        for sender in day:
            for vote in sorted(day[sender], key=lambda k: getNum(k)) :
                if(vote["sender"] != player):
                    continue
                target = vote['target']

                if target in top:
                    top[target] += 1
                else:
                    top[target] = 1

                player_code = getPlayerElement(target, players, None, False)
                #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
                if(vote['active']):
                    if (vote['value'] == 2):
                        response+=(player_code + " - <a href='"+ vote['post_link']+"' target=\"_blank\">"+vote['post_num']+"</a> (Double) (Day "+str(phase)+")<br>" )
                    elif (vote['value'] == 3):
                        response+=(player_code + " - <a href='"+ vote['post_link']+"' target=\"_blank\">"+vote['post_num']+"</a> (Triple) (Day "+str(phase)+")<br>")
                    else:
                        response+=(player_code + " - <a href='"+ vote['post_link']+"' target=\"_blank\">"+vote['post_num']+"</a> (Day "+str(phase)+")<br>")
                elif (vote['value'] == 2):
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['post_link'] +"' target=\"_blank\">"+vote['post_num']+"</a> (Double)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")
                elif (vote['value'] == 3):
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['post_link'] +"' target=\"_blank\">"+vote['post_num']+"</a> (Triple)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")
                else:
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['post_link'] +"' target=\"_blank\">"+vote['post_num']+"</a></strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")


    response += "<h3>Most voted for:</h3>"

    top = [(k, top[k]) for k in sorted(top, key=top.get, reverse=True)]
    for k in top:
        response += "<b>"+k[0]+" </b>" + "("+str(k[1])+")<br>"

    if(len(top) == 0):
        response+="No one!"

    return response


# The following 2 functions format the results into HTML
def htmlTimelinePlayer(playerX, days, players, other_actions):
    allVotes = []
    for day in days:
        for player in day:
            allVotes+=(day[player])

    if(other_actions != None):
        allVotes += other_actions

    sortedVotes = sorted(allVotes, key=lambda k: getNum(k), reverse=True)
    response = "<h3>Player Activity</h3>"

    for vote in sortedVotes:
        sender = vote['sender']
        target = vote['target']
        player_code_sender = getPlayerElement(sender, players, None, False)
        player_code_target = getPlayerElement(target, players, None, False)

        if(vote['action'] != 'day_start' and vote['action'] != 'day_end' and vote['sender'] != playerX and vote['target'] != playerX):
            continue

        numElement = getNumElement(vote['post_num'], vote['post_link'], vote.get("timestamp", None))
        prefix = numElement+" - <b>"
        if(vote['action'] == 'unvote'):
            response+= prefix+player_code_sender+"</b> unvoted "
            if(vote['target'] != None):
                response+=player_code_target
            response+="<br>"
            continue
        elif(vote['action'] == 'replacement'):
            response+= prefix+player_code_sender+"</b> was replaced by <b>"+player_code_target +"</b> <br>"
            continue
        elif(vote['action'] == 'death'):
            response+= prefix+player_code_target+"</b> was eliminated!<br>"
            continue
        elif(vote['action'] == 'victory'):
            response+= prefix+player_code_target+"</b> won the game!<br>"
            continue
        elif(vote['action'] == 'day_start'):
            response+= prefix+"Day "+vote["day_name"]+" begins!</b><br><br>"
            continue
        elif(vote['action'] == 'day_end'):
            response+= prefix+"Day "+vote["day_name"]+" ends!</b><br>"
            continue


        #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
        if(vote['active']):
            if (vote['value'] == 2):
                response+=  prefix+(player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Double)<br>")
            elif (vote['value'] == 3):
                response+=  prefix+(player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Triple)<br>")
            else:
                response+=  prefix+(player_code_sender + "</b> voted for <b>"+player_code_target+ "</b><br>")
        else:
            unvoteElement = getNumElement(vote['unvote_num'], vote['unvote_link'], vote['unvote_timestamp'])
            if (vote['value'] == 2):
                response+=("<div class=\"not_active\" style=\"display: inline\"><div id=\"striked\">"+ prefix+"<strike>"+player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Double)</strike> </div> (Unvote: "+unvoteElement+")<br></div>")
            elif (vote['value'] == 3):
                response+=("<div class=\"not_active\" style=\"display: inline\"><div id=\"striked\">"+ prefix+"<strike>"+player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Triple)</strike> </div> (Unvote: "+unvoteElement+")<br></div>")
            else:
                response+=("<div class=\"not_active\" style=\"display: inline\"><div id=\"striked\">"+ prefix+"<strike>"+player_code_sender + "</b> voted for <b>"+player_code_target + "</b> </strike> </div> (Unvote: "+unvoteElement+")<br></div>")
    response += "</div>"
    return response

def getNum(vote):
    num = vote['post_num']
    numi = int(num.replace("#", "").replace(",",""))
    return numi
