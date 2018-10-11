# The following 2 functions format the results into HTML
def htmlPrintDay(day):
    response = ""
    for player in sorted(day, key=lambda k: countActiveVotes(day[k]), reverse=True):
        voteList = day[player]
        activeVotes = countActiveVotes(day[player])
        #If the user has no active votes, we mark it with a special div class so we can filter it out later.
        if(activeVotes == 0):
            response += "<div class=\"not_active\">"
        response+=("<div class=\"pname\"><br><u><b>"+player+ "</b></u></div> (Players at this location: "+str(activeVotes)+")<br>")
        if(activeVotes == 0):
            response += "</div>"
        response += "<div class=\"votes\">"
        for vote in voteList:
            #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
            if(vote['active']):
                if (vote['value'] == 2):
                    response+=(vote['sender'] + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Double)<br>")
                elif (vote['value'] == 3):
                    response+=(vote['sender'] + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a> (Triple)<br>")
                else:
                    response+=(vote['sender'] + " - <a href='"+ vote['vote_link']+"' target=\"_blank\">"+vote['vote_num']+"</a><br>")
            elif (vote['value'] == 2):
                response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+vote['sender'] + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a> (Double)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a><br></div>")
            elif (vote['value'] == 3):
                response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+vote['sender'] + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a> (Triple)</strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a><br></div>")
            else:
                response+=("<div class=\"not_active\"><div id=\"striked\"><strike>"+vote['sender'] + " - <a id=\"striked\" href='"+  vote['vote_link'] +"' target=\"_blank\">"+vote['vote_num']+"</a></strike> </div> <a href='"+ vote['unvote_link']+"' target=\"_blank\">"+vote['unvote_num']+"</a><br></div>")
        response += "</div>"
    return response

def htmlPrint(days, days_info, days_posts):
    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    total_days = len(days)

    response = ""
    for day_no in range(0, len(days)):
        day_info = days_info[day_no]
        if("day_name" in day_info):
            response+=("<div class=\"day_title\"><br><B> ==== DAY "+day_info["day_name"].upper()+" MOVES ==== </B><br></div>")
        else:
            response+=("<div class=\"day_title\"><br><B> ==== DAY "+str(total_days-day_no)+" MOVES ==== </B><br></div>")
        response+=("<a href='"+ day_info['day_start_l']+"' target=\"_blank\">Day Start</a> ")
        if(day_info['day_end_l']!= None):
            response+=("- <a href='"+ day_info['day_end_l']+"' target=\"_blank\">Day End</a>")
        if(len(days[day_no]) == 0):
            response +="<div class=\"day_info\"><br>No one has moved!<br>"
        else:
            response+="<div class=\"day_info\">"+htmlPrintDay(days[day_no])
        response+="<br><b>Any player not listed here is at the quarters!</b><br>"
        response+="<br><br></div>"

    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    return response

# The following 2 functions format the results into BBCode
def bbCodePrintDay(day):
    response = ""
    for player in sorted(day, key=lambda k: countActiveVotes(day[k]), reverse=True):
        voteList = day[player]
        activeVotes = countActiveVotes(day[player])
        #If the user has no active votes, we mark it with a special div class so we can filter it out later.
        if(activeVotes == 0):
            response += "<div class=\"not_active\">"
        response+=("\n[b][u]"+player+ "[/u][/b] (Players at this location: "+str(activeVotes)+")\n")
        if(activeVotes == 0):
            response += "</div>"
        for vote in voteList:
            #For each vote on the user, we need to check whether it's active or not, and whether it's a regular, double or triple vote.
            if vote['active']:
                if vote['value']==2:
                    response+=(vote['sender'] + " - [u][url='"+ vote['vote_link']+"']"+vote['vote_num']+"[/url][/u] (Double)\n")
                elif vote['value']==3:
                    response+=(vote['sender'] + " - [u][url='"+ vote['vote_link']+"']"+vote['vote_num']+"[/url][/u] (Triple)\n")
                else:
                    response+=(vote['sender'] + " - [u][url='"+ vote['vote_link']+"']"+vote['vote_num']+"[/url][/u]\n")
            elif vote['value']==2:
                response+=("<div class=\"not_active\">[s]"+vote['sender'] + " - [u][url='"+  vote['vote_link'] +"']"+vote['vote_num']+"[/url][/u] (Double)[/s]  [u][url='"+ vote['unvote_link']+"']"+vote['unvote_num']+"[/url][/u]\n</div>")
            elif vote['value']==3:
                response+=("<div class=\"not_active\">[s]"+vote['sender'] + " - [u][url='"+  vote['vote_link'] +"']"+vote['vote_num']+"[/url][/u] (Triple)[/s]  [u][url='"+ vote['unvote_link']+"']"+vote['unvote_num']+"[/url][/u]\n</div>")
            else:
                response+=("<div class=\"not_active\">[s]"+vote['sender'] + " - [u][url='"+  vote['vote_link'] +"']"+vote['vote_num']+"[/url][/u][/s]  [u][url='"+ vote['unvote_link']+"']"+vote['unvote_num']+"[/url][/u]\n</div>")
    return response

def bbCodePrint(days, days_info, days_posts):
    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    total_days = len(days)
    response = ""
    for day_no in range(0, len(days)):
        day_info = days_info[day_no]
        if("day_name" in day_info):
            response+=("<div class='day' id=\'day"+str(total_days-day_no)+"\'>\n[b] ==== DAY "+day_info["day_name"].upper()+" MOVES ==== [/b]\n")
        else:
            response+=("<div class='day' id=\'day"+str(total_days-day_no)+"\'>\n[b] ==== DAY "+str(total_days-day_no)+" MOVES ==== [/b]\n")
        response+=("[u][url='"+ day_info['day_start_l']+"']Day Start[/url][/u] ")
        if(day_info['day_end_l']!= None):
            response+=("- [u][url='"+ day_info['day_end_l']+"']Day End[/url][/u]")
        if(len(days[day_no]) == 0):
            response += "\n\nNo one has moved!\n"
        else:
            response+="\n"+bbCodePrintDay(days[day_no])
        response+="\n[b]Any player not listed here is at the quarters![/b]"
        response+="\n</div>\n"

    days.reverse()
    days_info.reverse()
    days_posts.reverse()

    return response

# Counts active votes from a vote list
def countActiveVotes(votes):
    activeVotes = 0
    for vote in votes:
        if(vote['active']):
            activeVotes = activeVotes+vote['value']
    return activeVotes
