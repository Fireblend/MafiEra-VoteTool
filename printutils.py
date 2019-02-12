import math


# The following 2 functions format the results into HTML
def htmlPrintDay(day, players):
    response = ""
    for player in sorted(day, key=lambda k: countActiveVotes(day[k]), reverse=True):
        voteList = day[player]
        activeVotes = countActiveVotes(day[player])
        #If the user has no active votes, we mark it with a special div class so we can filter it out later.
        if(activeVotes == 0):
            response += "<div class=\"not_active\">"
        player_code = getPlayerElement(player, players, None, False)
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
        response+= numElement+" - <b>"

        if(vote['action'] == 'unvote'):
            response+= player_code_sender+"</b> unvoted<br>"
            continue
        elif(vote['action'] == 'replacement'):
            response+= player_code_sender+"</b> was replaced by <b>"+player_code_target +"</b> <br>"
            continue
        elif(vote['action'] == 'death'):
            response+= player_code_target+"</b> was eliminated!<br>"
            continue
        elif(vote['action'] == 'day_start'):
            response+="Day "+vote["day_name"]+" begins!</b><br><br>"
            continue
        elif(vote['action'] == 'day_end'):
            response+="Day "+vote["day_name"]+" ends!</b><br>"
            continue


        #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
        if(vote['active']):
            if (vote['value'] == 2):
                response+= (player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Double)<br>")
            elif (vote['value'] == 3):
                response+=(player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Triple)<br>")
            else:
                response+=(player_code_sender + "</b> voted for <b>"+player_code_target+ "</b><br>")
        else:
            unvoteElement = getNumElement(vote['unvote_num'], vote['unvote_link'], vote['unvote_timestamp'])
            if (vote['value'] == 2):
                response+=("<div class=\"not_active\" style=\"display: inline\"><div id=\"striked\"><strike>"+player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Double)</strike> </div> (Unvote: "+unvoteElement+")<br></div>")
            elif (vote['value'] == 3):
                response+=("<div class=\"not_active\" style=\"display: inline\"><div id=\"striked\"><strike>"+player_code_sender + "</b> voted for <b>"+player_code_target + "</b> (Triple)</strike> </div> (Unvote: "+unvoteElement+")<br></div>")
            else:
                response+=("<div class=\"not_active\" style=\"display: inline\"><div id=\"striked\"><strike>"+player_code_sender + "</b> voted for <b>"+player_code_target + "</b> </strike> </div> (Unvote: "+unvoteElement+")<br></div>")
    response += "</div>"
    return response

def htmlPrintSeq(days, days_info, days_posts, players, thread_url, other_actions=None, countdown=None):
    total_days = len(days)

    response = ""
    alive = 0
    dead = 0
    alive_text = ""
    dead_text = ""

    for key in players:
        if(players[key]["status"] == "alive"):
            alive += 1
            alive_text += players[key]["name"]+"<br>"
        elif(players[key]["status"] == "dead"):
            dead += 1
            dead_text += players[key]["name"]+"<br>"

    if(len(players)>0):
        response+=("<br><br>Current Stats:<br>[ <abbr rel=\"tooltip\" title=\""+alive_text+"\"><b>Alive</b>: " + str(alive) + "</abbr> | <abbr rel=\"tooltip\" title=\""+dead_text+"\"><b>Dead</b>:" + str(dead) + "</abbr> | <b>Majority</b>: " + str(math.floor(alive/2+1))+" ]<br>")

        if(countdown != None):
            response+=("<br><b>Current Countdown:</b><br><img id=\"countdown\" src=\""+countdown+"\"/><br>")

        response+=("<div class=\"day_title\"><br><B> ==== GAME TIMELINE ==== </B><br></div>")
        response+="<div class=\"day_info\">"+htmlPrintDaySeq(days, players, other_actions)
        response+="<br><br></div>"

    return response

def htmlPrint(days, days_info, days_posts, players, thread_url, countdown=None):
    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    total_days = len(days)

    response = ""
    alive = 0
    dead = 0
    alive_text = ""
    dead_text = ""
    for key in players:
        if(players[key]["status"] == "alive"):
            alive += 1
            alive_text += players[key]["name"]+"<br>"
        elif(players[key]["status"] == "dead"):
            dead += 1
            dead_text += players[key]["name"]+"<br>"

    if(len(players)>0):
        response+=("<br><br>Current Stats:<br>[ <abbr rel=\"tooltip\" title=\""+alive_text+"\"><b>Alive</b>: " + str(alive) + "</abbr> | <abbr rel=\"tooltip\" title=\""+dead_text+"\"><b>Dead</b>:" + str(dead) + "</abbr> | <b>Majority</b>: " + str(math.floor(alive/2+1))+" ]<br>")

    if(countdown != None):
        response+=("<br><b>Current Countdown:</b><br><img id=\"countdown\" src=\""+countdown+"\"/><br>")

    for day_no in range(0, len(days)):
        day_info = days_info[day_no]
        if("day_name" in day_info):
            response+=("<div class=\"day_title\"><br><B> ==== DAY "+day_info["day_name"].upper()+" VOTES ==== </B><br></div>")
        else:
            response+=("<div class=\"day_title\"><br><B> ==== DAY "+str(total_days-day_no)+" VOTES ==== </B><br></div>")
        response+=("<a href='"+ day_info['day_start_l']+"' target=\"_blank\">Day Start</a> ")
        if(day_info['day_end_l']!= None):
            response+=("- <a href='"+ day_info['day_end_l']+"' target=\"_blank\">Day End</a>")
        if(len(days[day_no]) == 0):
            response +="<div class=\"day_info\"><br>No votes have been cast!<br>"
        else:
            response+="<div class=\"day_info\">"+htmlPrintDay(days[day_no], players)
        response+="<br><b>Post Counts:</b><br>"
        for player in sorted(days_posts[day_no], key=days_posts[day_no].get, reverse=True):
            player_code = getPlayerElement(player, players, thread_url, True)
            response+="<u>"+ player_code + "</u>: "+str(days_posts[day_no][player])+"  "
        response+="<br><br></div>"

    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    return response

# The following 2 functions format the results into BBCode
def bbCodePrintDay(day, players):
    response = ""
    for player in sorted(day, key=lambda k: countActiveVotes(day[k]), reverse=True):
        voteList = day[player]
        activeVotes = countActiveVotes(day[player])
        #If the user has no active votes, we mark it with a special div class so we can filter it out later.
        if(activeVotes == 0):
            response += "<div class=\"not_active\">"

        name = player
        if len(players) > 0:
            name = players[player]["name"]
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


def getPlayerElement(sender, players, thread_url, addInfo):
    if(sender == None):
        return None

    if(len(players) == 0):
        return sender

    name = players[sender]["name"]

    if(players[sender]["flip_post"] != None):
        name = "<a style=\"text-decoration:none\" href='"+  players[sender]["flip_post"] +"' target=\"_blank\">"+"💀 "+"</a>"+name
    if(addInfo):
        name = "<a style=\"text-decoration:none\" href='"+  thread_url + "p/"+ sender + "' target=\"_blank\">"+"🔍 "+"</a>"+name

    contents = "<b>"+players[sender]["name"]+"</b> "
    contents += "<br><b>Pronouns:</b> "+players[sender]["pronouns"]
    contents += "<br><b>Timezone:</b> "+players[sender]["timezone"]
    contents += "<br><b>Status:</b> "+players[sender]["status"]
    if(players[sender]["replaces"] != None):
        contents += "<br><b>Replacing:</b> "+players[players[sender]["replaces"]]["name"]
    if(players[sender]["replaced_by"] != None):
        contents += "<br><b>Replaced by:</b> "+players[players[sender]["replaced_by"]]["name"]

    player_code = "<abbr rel=\"tooltip\" title=\""+contents+"\">" + name + "</abbr>"

    return player_code

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
        response+="\n[b]Post Counts:[/b]\n"
        for player in sorted(days_posts[day_no], key=days_posts[day_no].get, reverse=True):
            name = player
            if len(players) > 0:
                name = players[player]["name"]
            response+="[u]"+ name + "[/u]: "+str(days_posts[day_no][player])+"  "

        if(countdown != None):
            response+=("\n\n[b]Current Countdown:[/b]\n[img]"+countdown+"[/img]")
        response+="\n\n</div>\n\n"
    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    return response

def totalCountPrint(days_posts, players, thread_url):
    total_posts_count = {}
    for day_no in range(0, len(days_posts)):
        for player in days_posts[day_no]:
            if player in total_posts_count:
                total_posts_count[player] += days_posts[day_no][player]
            else:
                total_posts_count[player] = days_posts[day_no][player]
    response="<br><br><b>Total Accumulated Post Counts:</b><br><div class=\"day_info\">"
    for player in sorted(total_posts_count, key=total_posts_count.get, reverse=True):
        player_code = getPlayerElement(player, players, thread_url, True)
        response+="<br><u>"+ player_code + "</u>: "+str(total_posts_count[player])+"  "
    response+="<br></div>"
    return response

# Counts active votes from a vote list
def countActiveVotes(votes):
    activeVotes = 0
    for vote in votes:
        if(vote['active']):
            activeVotes = activeVotes+vote['value']
    return activeVotes



# The following 2 functions format the results into HTML
def htmlPrintPlayer(days, days_posts, players, player):
    player = player.lower().strip()
    player_data = players[player]

    general = getGeneralInfo(days_posts, player_data, players, player)
    voted_for = getVotedFor(days, players, player)
    voted_by = getVotedBy(days, players, player)

    return general, voted_for, voted_by

def getGeneralInfo(days_posts, player_data, players, player):
    totalPosts = 0
    for day_no in range(0, len(days_posts)):
        if(player in days_posts[day_no]):
            totalPosts += days_posts[day_no][player]

    response = "<h3>"+player_data["name"]+"</h3>"
    response += "<b>Pronouns:</b> "+player_data["pronouns"]
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
        else:
            response += "No one!"


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
        else:
            response += "No one!"


    response += "<h3>Most voted for:</h3>"

    top = [(k, top[k]) for k in sorted(top, key=top.get, reverse=True)]
    for k in top:
        response += "<b>"+k[0]+" </b>" + "("+str(k[1])+")<br>"

    if(len(top) == 0):
        response+="No one!"

    return response

def getNum(vote):
    num = vote['post_num']
    numi = int(num.replace("#", ""))
    return numi
