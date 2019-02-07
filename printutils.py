# The following 2 functions format the results into HTML
def htmlPrintDay(day, players):
    response = ""
    for player in sorted(day, key=lambda k: countActiveVotes(day[k]), reverse=True):
        voteList = day[player]
        activeVotes = countActiveVotes(day[player])
        #If the user has no active votes, we mark it with a special div class so we can filter it out later.
        if(activeVotes == 0):
            response += "<div class=\"not_active\">"
        player_code = getPlayerElement(player, players)
        response+=("<div class=\"pname\"><br><u><b>"+player_code+ "</b></u></div> ("+str(activeVotes)+" votes)<br>")
        if(activeVotes == 0):
            response += "</div>"
        response += "<div class=\"votes\">"
        for vote in voteList:
            sender = vote['sender']
            player_code = getPlayerElement(sender, players)
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

def htmlPrint(days, days_info, days_posts, players):
    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    total_days = len(days)

    response = ""
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
            player_code = getPlayerElement(player, players)
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

def getPlayerElement(sender, players):
    if(len(players) == 0):
        return sender


    name = players[sender]["name"]
    if(players[sender]["flip_post"] != None):
        name = "<a style=\"text-decoration:none\" href='"+  players[sender]["flip_post"] +"' target=\"_blank\">"+"💀 "+"</a>"+name

    player_code = "<div class=\"tooltip\">" + name + "<span class=\"tooltiptext\">"
    player_code += "<b>"+players[sender]["name"]+"</b> "
    player_code += "<br><b>Pronouns:</b> "+players[sender]["pronouns"]
    player_code += "<br><b>Timezone:</b> "+players[sender]["timezone"]
    player_code += "<br><b>Status:</b> "+players[sender]["status"]
    if(players[sender]["replaces"] != None):
        player_code += "<br><b>Replacing:</b> "+players[sender]["replaces"]
    player_code += "</span></div>"

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

def totalCountPrint(days_posts, players):
    total_posts_count = {}
    for day_no in range(0, len(days_posts)):
        for player in days_posts[day_no]:
            if player in total_posts_count:
                total_posts_count[player] += days_posts[day_no][player]
            else:
                total_posts_count[player] = days_posts[day_no][player]
    response="<br><br><b>Total Accumulated Post Counts:</b><br><div class=\"day_info\">"
    for player in sorted(total_posts_count, key=total_posts_count.get, reverse=True):
        player_code = getPlayerElement(player, players)
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
