import random
import sys


def printInfo(info, roles):
  results = "<b>These are the numbers and codes generated for this setup:</b><br><br>\n"

  for i, j in zip(info[0], info[1]):
      results += str(i)+"("+j+") "

  results += "<br><br><b>Resulting Role Distribution:</b><br><br>\n"

  distro = {}
  distro['Vanilla Townie'] = roles.count('T')
  distro['Doctor'] = roles.count('D')
  distro['1-Shot Doctor'] = roles.count('d')
  distro['Cop'] = roles.count('C')
  distro['1-Shot Cop'] = roles.count('c')
  distro['Vigilante'] = roles.count('V')
  distro['1-Shot Vigilante'] = roles.count('v')
  distro['Innocent Child'] = roles.count('i')
  distro['Mason'] = roles.count('M1')
  distro['Other Mason'] = roles.count('M2')
  distro['Roleblocker'] = roles.count('B')
  distro['1-Shot Roleblocker'] = roles.count('b')
  distro['Mafia Goon'] = roles.count('G')
  distro['Mafia Roleblocker'] = roles.count('R')
  distro['Godfather'] = roles.count('GF')
  distro['Serial Killer'] = roles.count('SK')

  for role in distro:
      rolename = role
      if distro[role] > 1:
          rolename += "s"
      if distro[role] > 0:
          results += str(distro[role])+" "+rolename+"<br>"


  return results

def printRoles(roles):
  htmlresult = "<div id=\"roles\">\n"
  bbcode = ""

  roles = list(set(roles))
  for role in roles:
    if role == 'D':
      title = "Doctor"
      ability = ["Each night phase, you may protect one player in the game from one nightkill."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."
    elif role == 'd':
      title = "1-Shot Doctor"
      ability = ["Once at night, you may protect a player in the game from one nightkill."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."
    elif role == 'C':
      title = "Cop"
      ability = ["Each night phase, you may investigate one player in the game by PM'ing the mod. You will get results back in the form of Town, Antitown or No Result."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."
    elif role == 'c':
      title = "1-Shot Cop"
      ability = ["Once at night, you may investigate a player in the game by PM'ing the mod. You will get results back in the form of Town, Antitown or No Result."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."
    elif role == 'V':
      title = "Vigilante"
      ability = ["Each night, you may select a player in the game to target for a nightkill."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."
    elif role == 'v':
      title = "1-Shot Vigilante"
      ability = ["Once at night, you may select a player in the game to target for a nightkill."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."
    elif role == 'i':
      title = "Innocent Child"
      ability = ["At the start of Day 1, the moderator of the game will announce you as an Innocent Child, confirming you as town."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."
    elif role == 'M1' or role == 'M2':
      title = "Mason"
      ability = ["You are confirmed town to your mason partner(s) and vice versa. You are permitted to talk to your partner(s) during pregame and at nights in this [link]."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."
    elif role == 'B':
      title = "Roleblocker"
      ability = ["Each night, you may select a player in the game to roleblock. They will not be able to perform an action at night if they have one."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."
    elif role == 'b':
      title = "1-Shot Roleblocker"
      ability = ["Once at night, you may select a player in the game to roleblock. They will not be able to perform an action on this night if they have one."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."
    elif role == 'G':
      title = "Mafia Goon"
      ability = ["Factional communication: During the night phase you may talk with your partners here [link].", "Factional kill: Each night phase, one of you or your partners may perform the factional kill."]
      wincon = "You win when the Mafia obtain a majority or nothing can prevent this from occurring."
    elif role == 'R':
      title = "Mafia Roleblocker"
      ability = ["Factional communication: During the night phase you may talk with your partners here [link].", "Factional kill: Each night phase, one of you or your partners may perform the factional kill.","Roleblock: Each night phase, you individually may perform a roleblock on another player in the game. You cannot block and kill in the same night."]
      wincon = "You win when the Mafia obtain a majority or nothing can prevent this from occurring."
    elif role == 'GF':
      title = "Mafia Godfather"
      ability = ["Factional communication: During the night phase you may talk with your partners here [link].", "Factional kill: Each night phase, one of you or your partners may perform the factional kill.", "Investigation Immunity: You appear innocent to Cop investigations."]
      wincon = "You win when the Mafia obtain a majority or nothing can prevent this from occurring."
    elif role == 'SK':
      title = "Serial Killer"
      ability = ["Pregame you must choose to be either Investigation Immune or 1-Shot Bulletproof.\nEach night phase, you may select a player in the game to nightkill."]
      wincon = "You win when you are the last player alive or nothing can prevent this from occurring."
    else:
      title = "Vanilla Townie"
      ability = ["Your weapon is your vote, you have no night actions."]
      wincon = "You win when all threats to the town have been eliminated and there is at least one town player alive."

    htmlrole = "<div class=\"role\">\n <div class=\"role-name\">" + title + "</div>\n"
    bbrole = "<div class=\"role\">\n <div class=\"role-name\">" + title + "</div>\n"

    htmlrole += "<div class=\"welcome\"> Welcome, [Player]! You're a <b>"+ title + "</b>"
    bbrole  += "Welcome, [Player]! You're a [b]"+ title + "[/b]"

    if(role in ['G', 'R', 'GF', 'M1', 'M2']):
      htmlrole += " along with your partner(s) [Player] (and [Player])"
      bbrole += " along with your partner(s) [Player] (and [Player])"
    htmlrole += "!</div><br>\n"
    bbrole += "<br><br>\n\n"

    htmlrole += "<div class=\"abiheader\">Abilities:</div>\n"
    bbrole += "[b]Abilities:[/b]<br>\n"

    htmlrole += "<div class=\"abilist\"><ul>\n"

    for a in ability:
      htmlrole += "    <li>"+ a +"</li>\n"
      bbrole += " - "+ a +"<br><br>\n"

    htmlrole += "</ul></div>\n"
    bbrole += "\n"

    htmlrole += "<div class=\"winheader\">Win Condition:</div>\n"
    bbrole += "[b]Win Condition:[/b]<br>\n"

    htmlrole += "<div class=\"wincon\"><ul><li>"+wincon+"</li></ul></div><br>\n"
    bbrole += wincon+"\n"

    htmlresult += htmlrole+"</div>"
    bbcode += bbrole + "</div>"

  return [htmlresult+"</div>", "<div class=\"bbcode\">"+bbcode+"</div>"]


def generate(seed=0, useSeed=False):
  numbers = []
  values = []
  info = ""

  if(useSeed):
    random.seed(seed)
  else:
    seed = random.randrange(sys.maxsize)
    random.seed(seed)

  print("Seed: "+str(seed))

  #Generate random numbers and add basic codes
  for x in range(7):
    val = random.randint(1,101)
    numbers.append(val)

    if(val <=50):
      values.append('T')
    elif (val <= 65):
      values.append('C')
    elif (val <= 75):
      values.append('D')
    elif (val <= 85):
      values.append('V')
    elif (val <= 95):
      values.append('M')
    else:
      values.append('B')


  #Determine roles
  roles = []

  cops = values.count('C')
  doctors = values.count('D')
  vigs = values.count('V')
  masons = values.count('M')
  blockers = values.count('B')
  scums = values.count('T')

  #Add cops
  if cops % 2 == 0:
    for x in range(cops//2):
      roles.append('C')
  else:
    for x in range(cops//2):
      roles.append('C')
    roles.append('c')

  #Add doctors
  if doctors % 2 == 0:
    for x in range(doctors//2):
      roles.append('D')
    if doctors > 0:
      roles.append('d')
  else:
    for x in range(doctors//2+1):
      roles.append('D')

  #Add vigs
  if vigs % 2 == 0:
    for x in range(vigs//2):
      roles.append('V')
  else:
    for x in range(vigs//2):
      roles.append('V')
    roles.append('v')

  #Add masons
  if masons == 1:
    roles.append('i')
  elif masons == 2:
    roles.append('M1')
    roles.append('M1')
  elif masons == 3:
    roles.append('M1')
    roles.append('M1')
    roles.append('i')
  elif masons == 4:
    roles.append('M1')
    roles.append('M1')
    roles.append('M1')
  elif masons == 5:
    roles.append('M1')
    roles.append('M1')
    roles.append('M2')
    roles.append('M2')

  #Add roleblockers
  if blockers % 2 == 0:
    for x in range(blockers):
      roles.append('B')
    if blockers > 0:
      roles.append('b')
  else:
    for x in range(blockers//2+1):
      roles.append('B')

  #Add scum team
  roles.append('G')
  if scums <= 2:
    roles.append('R')
    roles.append('GF')
  elif scums <= 4:
    roles.append('G')
    roles.append('R')
  elif scums <= 7:
    roles.append('GF')

  #Add serial killer
  if scums % 2 != 0:
    roles.append('SK')

  #Add townies
  while len(roles) < 13:
    roles.append('T')

  print(roles)

  return [roles, seed, [numbers, values]]
