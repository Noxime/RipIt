# -*- coding: utf-8 -*-
#RipIt.py
#Aaro Perämaa, 2017
#
#
#See below for configuration options. Should be able to build index at ~75 entries / sec
#And get post json's at 8500 / hour. Media is up to your connection


from requests import get as GET
import json
import time
import os
import errno
import subprocess

#Configuration, should make these passable to program
getLinks = False #Build index of posts
getComments = False #Download posts

getPostMedia = True #Download media, like jpgs
getCommentMedia = False
getMedia = getPostMedia or getCommentMedia

extensions = set([ "jpg", "jpeg", "png", "gif", "webm", "mp3", "mp4" ])
#extensions = set([ ]) #DEBUG
useYoutubeDl = False
YDLSites = [ "youtu", "streamable", "gfycat" ]

targetFolder = "C:\\Users\\Aarop\\rips\\reddit\\"
targetSubreddit = "twice"
youtubeDlLocation = "C:\\Users\\Aarop\\youtube-dl.exe"

retries = 3
userAgent = "desktop:us.noxim.ripit:v0.0.0 (by /u/noxime)"
#End of configuration

startTime = time.time()
def timestamp():
    return "{0:.2f}".format(time.time() - startTime) #Format to 2 decimals

if(getLinks):

    print(timestamp() + "s | Fetching all posts of " + targetSubreddit)

    #http://apiv2.pushshift.io/reddit/submission/fetch/?subreddit=twice&sort=asc
    page = json.loads(GET("https://apiv2.pushshift.io/reddit/submission/fetch/?sort=asc&subreddit=" + targetSubreddit, headers = { "user-agent": userAgent }).content)

    totalPosts = 0
    currentPage = 0

    stillLinks = True;
    linksFile = open(targetFolder + "links", "w")

    while (stillLinks):

        for entry in page["data"]:
            linksFile.write(entry["id"] + "\n")
            totalPosts += 1
                #print(str(entry["data"]["permalink"]).encode("ascii", "ignore")

        print(timestamp() + "s | Finished reading page: " + str(currentPage) + ", at " + str(totalPosts) + " posts now")

        currentPage += 1
        if "next_page" in page["metadata"]:
            page = json.loads(GET(page["metadata"]["next_page"], headers = { "user-agent": userAgent }).content)
        else:
            stillLinks = False;

    linksFile.close();
    print(timestamp() + "s | Done fetching all links, saved to " + targetFolder + "links")

if(getComments):
    print(timestamp() + "s | Fetching comments")

    entries = [line.rstrip() for line in open(targetFolder + "links")] #Get all lines
    for index, entry in enumerate(entries):
    #entry = entries[8072] #DEBUG
    #if(True):

        print(timestamp() + "s | Fetching " + entry + ", " + str(index) + "/" + str(len(entries)))
        try:
            req = GET("https://reddit.com/r/" + targetSubreddit + "/comments/" + entry + "/.json", headers = { "user-agent": userAgent })
        except:
            continue
        if(req.status_code != 200): #Failed
            tryI = 0
            while(req.status_code != 200 and tryI < retries):
                print(timestamp() + "s | Failed to get " + entry + ", retrying")
                req = GET("https://reddit.com/r/" + targetSubreddit + "/comments/" + entry + "/.json", headers = { "user-agent": userAgent })
                tryI += 1
                time.sleep(0.5) #Wait half a second to be safe

            if(req.status_code != 200):
                continue


        data = req.text

        postFilename = targetFolder + entry + "\\post.json"
        os.makedirs(os.path.dirname(postFilename), exist_ok = True) #Create folder if necessary
        with open(postFilename, "w") as post:
            post.write(str(data))

    print(timestamp() + "s | All comments fetched")



if(getMedia):
    print(timestamp() + "s | Fetching media")

    folderIndex = 0
    folderCount = len(next(os.walk(targetFolder))[1])
    for folder in next(os.walk(targetFolder))[1]: #Get all post folders
        print(timestamp() + "s | Reading post " + folder + ", " + str(folderIndex) + "/" + str(folderCount))
        folderIndex += 1

        with open(targetFolder + folder + "\\post.json", "r") as raw:
            try:
                data = json.loads(raw.read())
            except:
                print(timestamp() + "s | ERROR: " + folder + " has malformed json")
                continue #Something is wrong with the input data

            mediaURL = data[0]["data"]["children"][0]["data"]["url"] #Get the post media
            extension = mediaURL.rsplit(".", 1)[-1]

            if(getPostMedia):
                if(extension in extensions):
                    postFilename = targetFolder + folder + "\\media\\" + mediaURL.rsplit("/", 1)[-1] #After last / in url
                    os.makedirs(os.path.dirname(postFilename), exist_ok = True) #Create folder if necessary
                    with open(postFilename, "wb") as mediaFile:
                        try:
                            req = GET(mediaURL, headers = { "user-agent": userAgent }) #Request data and save to file
                            for chunk in req:
                                mediaFile.write(chunk)
                        except:
                            print(timestamp() + "s | Failed to retreive " + mediaURL + ", skipping")
                            continue

                    print(timestamp() + "s | Downloaded " + mediaURL) #Logger
                elif(useYoutubeDl):
                    print(timestamp() + "s | NOTE: YoutubeDL support is experimental! Make sure you don't have config set")

                    for domain in YDLSites:
                        if(domain in mediaURL):
                            print(timestamp() + "s | Trying Youtube-DL for " + mediaURL)

                            #This is an ass
                            #proc = subprocess.Popen([ youtubeDlLocation, "-f bestvideo+bestaudio", "-i", "-o", targetFolder + folder + "\\media\\%(title)s.%(ext)s", mediaURL ], stdout = subprocess.PIPE)
                            proc = subprocess.Popen([ youtubeDlLocation, "-o", targetFolder + folder + "\\media\\abc.%(ext)s", mediaURL ], stdout = subprocess.PIPE)
                            output = proc.stdout.read()
                            print(output) #Comment if you dont want your log getting spammed



print(timestamp() + "s | Finished")
