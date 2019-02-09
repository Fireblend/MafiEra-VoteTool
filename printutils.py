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
            #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
            if(vote['active']):
                if (vote['value'] == 2):
                    response+=(player_code + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Double)<br>")
                elif (vote['value'] == 3):
                    response+=(player_code + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Triple)<br>")
                else:
                    response+=(player_code + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a><br>")
            elif (vote['value'] == 2):
                response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a> (Double)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a><br></div>")
            elif (vote['value'] == 3):
                response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a> (Triple)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a><br></div>")
            else:
                response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a></strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a><br></div>")
        response += "</div>"
    return response

# The following 2 functions format the results into HTML
def htmlPrintDaySeq(day, players):
    response = "<br>"
    allVotes = []
    for player in day:
        allVotes+=(day[player])

    sortedVotes = sorted(allVotes, key=lambda k: getNum(k['vote_num']))

    for vote in sortedVotes:
        sender = vote['sender']
        target = vote['target']
        player_code_sender = getPlayerElement(sender, players, None, False)
        player_code_target = getPlayerElement(target, players, None, False)
        #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
        if(vote['active']):
            if (vote['value'] == 2):
                response+=(player_code_sender + " -> "+player_code_target + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Double)<br>")
            elif (vote['value'] == 3):
                response+=(player_code_sender + " -> "+player_code_target + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Triple)<br>")
            else:
                response+=(player_code_sender + " -> "+player_code_target+ " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a><br>")
        elif (vote['value'] == 2):
            response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code_sender + " -> "+player_code_target + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a> (Double)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a><br></div>")
        elif (vote['value'] == 3):
            response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code_sender + " -> "+player_code_target + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a> (Triple)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a><br></div>")
        else:
            response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code_sender + " -> "+player_code_target + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a></strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a><br></div>")
    response += "</div>"
    return response

def htmlPrint(days, days_info, days_posts, players, thread_url, seq):
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
        elif not seq:
            response+="<div class=\"day_info\">"+htmlPrintDay(days[day_no], players)
        else:
            response+="<div class=\"day_info\">"+htmlPrintDaySeq(days[day_no], players)
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
                    vote_string=(name + " - [u][url='"+ vote['vote_link']+"']"+vote['vote_num']+"[/url][/u] (Double)\n")
                elif vote['value']==3:
                    vote_string=(name + " - [u][url='"+ vote['vote_link']+"']"+vote['vote_num']+"[/url][/u] (Triple)\n")
                else:
                    vote_string=(name + " - [u][url='"+ vote['vote_link']+"']"+vote['vote_num']+"[/url][/u]\n")
            elif vote['value']==2:
                vote_string=("<div class=\"not_active\">[s]"+name + " - [u][url='"+  vote['vote_link'] +"']"+vote['vote_num']+"[/url][/u] (Double)[/s]  [u][url='"+ vote['unvote_link']+"']"+vote['unvote_num']+"[/url][/u]\n</div>")
            elif vote['value']==3:
                vote_string=("<div class=\"not_active\">[s]"+name + " - [u][url='"+  vote['vote_link'] +"']"+vote['vote_num']+"[/url][/u] (Triple)[/s]  [u][url='"+ vote['unvote_link']+"']"+vote['unvote_num']+"[/url][/u]\n</div>")
            else:
                vote_string=("<div class=\"not_active\">[s]"+name + " - [u][url='"+  vote['vote_link'] +"']"+vote['vote_num']+"[/url][/u][/s]  [u][url='"+ vote['unvote_link']+"']"+vote['unvote_num']+"[/url][/u]\n</div>")
            response+=vote_string
    return response

def getPlayerElement(sender, players, thread_url, addInfo):
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

    player_code = "<div class=\"tooltip\">" + name + "<span class=\"tooltiptext\">"
    player_code = "<abbr rel=\"tooltip\" title=\""+contents+"\">" + name + "</abbr>"

    return player_code

def bbCodePrint(days, days_info, days_posts, players):
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
        response+="\n</div>\n"

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
            for vote in sorted(day[player], key=lambda k: getNum(k['vote_num'])) :
                sender = vote['sender']

                if sender in top:
                    top[sender] += 1
                else:
                    top[sender] = 1

                player_code = getPlayerElement(sender, players, None, False)
                #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
                if(vote['active']):
                    if (vote['value'] == 2):
                        response+=(player_code + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Double) (Day "+str(phase)+")<br>" )
                    elif (vote['value'] == 3):
                        response+=(player_code + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Triple) (Day "+str(phase)+")<br>")
                    else:
                        response+=(player_code + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Day "+str(phase)+")<br>")
                elif (vote['value'] == 2):
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a> (Double)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")
                elif (vote['value'] == 3):
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a> (Triple)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")
                else:
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a></strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")
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
        if(player in day):
            for vote in sorted(day[player], key=lambda k: getNum(k['vote_num'])) :
                target = vote['target']

                if target in top:
                    top[target] += 1
                else:
                    top[target] = 1

                player_code = getPlayerElement(target, players, None, False)
                #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
                if(vote['active']):
                    if (vote['value'] == 2):
                        response+=(player_code + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Double) (Day "+str(phase)+")<br>" )
                    elif (vote['value'] == 3):
                        response+=(player_code + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Triple) (Day "+str(phase)+")<br>")
                    else:
                        response+=(player_code + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Day "+str(phase)+")<br>")
                elif (vote['value'] == 2):
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a> (Double)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")
                elif (vote['value'] == 3):
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a> (Triple)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")
                else:
                    response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+player_code + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a></strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a> (Day "+str(phase)+")<br></div>")
        else:
            response += "No one!"


        response += "<h3>Most voted for:</h3>"

    top = [(k, top[k]) for k in sorted(top, key=top.get, reverse=True)]
    for k in top:
        response += "<b>"+k[0]+" </b>" + "("+str(k[1])+")<br>"

    if(len(top) == 0):
        response+="No one!"

    return response

def getNum(num):
    numi = int(num.replace("#", ""))
    return numi
