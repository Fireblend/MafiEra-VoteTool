from os import listdir
from os.path import isfile, join

mypath = "gamecache"

file_list = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for filename in file_list:
    file_uri = "gamecache/"+filename

    originalFile = open(file_uri, "r")
    text = originalFile.read()
    originalFile.close()

    backup_file = open(file_uri+".bak", "w")
    backup_file.write(text)
    backup_file.close()

    text = text.replace("\"vote_num\"", "\"post_num\"")
    text = text.replace("\"vote_link\"", "\"post_link\"")
    text = text.replace("\"vote_timestamp\"", "\"post_timestamp\"")

    new_file = open(file_uri, "w")
    new_file.write(text)
    new_file.close()
