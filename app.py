import votecount
import printutils
import mafiagen
import json
from flask import Flask, render_template

#Era Base URLs
era_url = 'https://www.resetera.com/'
base_thread_url = era_url+'threads/'

#Outer Mafia Base URLs
om_url = 'https://outermafia.com/'
om_thread_url = om_url+'index.php?threads/'

#Vote Tool Base URLs
vt_url = 'https://vote.fireblend.com/'

############################################
####     FLASK CALLBACKS
############################################
app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return ''


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/<threadId>/')
def gamePage(threadId):

    res = votecount.scrapeThread(threadId+"/")

    hresponse = printutils.htmlPrint(res["days"], res["days_info"], res["days_posts"])

    bresponse = printutils.bbCodePrint(res["days"], res["days_info"], res["days_posts"])
    totals = printutils.totalCountPrint(res["days_posts"])

    header="<br><b>MafiEra Vote Tool 3000</b>"
    header+="<br><a href=\""+base_thread_url+threadId+"\"><b>Go To Game Thread</b></a><br>"
    header+="<img src=\""+res['banner_url']+"\" />"

    header+="<br><br>"

    if(len(res["days"])) == 0:
        return render_template('template_nogame.html')

    return render_template('template.html', thread_url=base_thread_url+threadId, html=hresponse, bbcode=bresponse, totals=totals, banner=res["banner_url"], header=header, current_day_id="day"+str(len(res["days"])))


@app.route('/om/<threadId>/')
def omGamePage(threadId):

    res = votecount.scrapeThread(threadId+"/", True)

    hresponse = printutils.htmlPrint(res["days"], res["days_info"], res["days_posts"])

    bresponse = printutils.bbCodePrint(res["days"], res["days_info"], res["days_posts"])
    totals = printutils.totalCountPrint(res["days_posts"])

    header="<br><b>MafiEra Vote Tool 3000</b>"
    header+="<br><a href=\""+om_thread_url+threadId+"\"><b>Go To Game Thread</b></a><br>"
    header+="<img src=\""+res['banner_url']+"\" />"

    header+="<br><br>"

    if(len(res["days"])) == 0:
        return render_template('template_nogame.html')

    return render_template('template.html', thread_url=om_thread_url+threadId, html=hresponse, bbcode=bresponse, totals=totals, banner=res["banner_url"], header=header, current_day_id="day"+str(len(res["days"])))

@app.route('/<threadId>/raw/')
def raw(threadId):
    res = votecount.scrapeThread(threadId+"/")
    return json.dumps(res)

@app.route('/om/<threadId>/raw/')
def omRaw(threadId):
    res = votecount.scrapeThread(threadId+"/", True)
    return json.dumps(res)

@app.route('/<threadId>/simple/')
def simple(threadId):
    res = votecount.scrapeThread(threadId+"/")
    last = len(res["days"])-1

    if(last<0):
        return render_template('template_nogame.html')

    hresponse = printutils.htmlPrint([res["days"][last]], [res["days_info"][last]], [res["days_posts"][last]])
    bresponse = printutils.bbCodePrint([res["days"][last]], [res["days_info"][last]], [res["days_posts"][last]])

    hresponse = hresponse.replace("==== DAY 1 VOTES ====", "==== CURRENT VOTES ====")
    bresponse = bresponse.replace("==== DAY 1 VOTES ====", "==== CURRENT VOTES ====")

    return render_template('template_simple.html', thread_url=base_thread_url+threadId, html=hresponse, bbcode=bresponse, votetool=vt_url+threadId)


@app.route('/om/<threadId>/simple/')
def omSimple(threadId):
    res = votecount.scrapeThread(threadId+"/", True)
    last = len(res["days"])-1

    if(last<0):
        return render_template('template_nogame.html')

    hresponse = printutils.htmlPrint([res["days"][last]], [res["days_info"][last]], [res["days_posts"][last]])
    bresponse = printutils.bbCodePrint([res["days"][last]], [res["days_info"][last]], [res["days_posts"][last]])

    hresponse = hresponse.replace("==== DAY 1 VOTES ====", "==== CURRENT VOTES ====")
    bresponse = bresponse.replace("==== DAY 1 VOTES ====", "==== CURRENT VOTES ====")
    return render_template('template_simple.html', thread_url=om_thread_url+threadId, html=hresponse, bbcode=bresponse, votetool=vt_url+"/om/"+threadId)


@app.route('/mafiagen/')
def gen():
    results = mafiagen.generate()

    seed = results[1]
    info = mafiagen.printInfo(results[2], results[0])

    printInfo = mafiagen.printRoles(results[0])

    html = printInfo[0]
    bbcode = printInfo[1]

    return render_template('template_gen.html', info=info, seed=seed, html=html, bbcode=bbcode)

@app.route('/mafiagen/<userseed>/')
def genuserseed(userseed):
    results = mafiagen.generate(userseed, True)

    seed = results[1]
    info = mafiagen.printInfo(results[2], results[0])

    printInfo = mafiagen.printRoles(results[0])

    html = printInfo[0]
    bbcode = printInfo[1]

    return render_template('template_gen.html', info=info, seed=seed, html=html, bbcode=bbcode)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, threaded=True)
