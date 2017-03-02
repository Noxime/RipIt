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

startTime = time.time()
def timestamp():
    return "{0:.2f}".format(time.time() - startTime) #Format to 2 decimals

#Configuration, should make these passable to program
getLinks = False #Build index of posts
getComments = True #Download posts

getPostMedia = True #Download media, like jpgs
getCommentMedia = False
getMedia = getPostMedia or getCommentMedia

extensions = set([ "jpg", "jpeg", "png", "gif", "webm", "mp3", "mp4" ])

retries = 3
targetFolder = "C:\\Users\\Aarop\\rips\\reddit\\"
targetSubreddit = "twice"
userAgent = "desktop:us.noxim.ripit:v0.0.0 (by /u/noxime)"
#End of configuration


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
        req = GET("https://reddit.com/r/" + targetSubreddit + "/comments/" + entry + "/.json", headers = { "user-agent": userAgent })
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

    for folder in next(os.walk(targetFolder))[1]: #Get all post folders
        print(timestamp() + "s | Reading post " + folder)

        with open(targetFolder + folder + "\\post.json", "r") as raw:
            data = json.loads(raw.read())
            mediaURL = data[0]["data"]["children"][0]["data"]["url"] #Get the post media
            extension = mediaURL.rsplit(".", 1)[-1]

            if(getPostMedia):
                if(extension in extensions):
                    postFilename = targetFolder + folder + "\\media\\" + mediaURL.rsplit("/", 1)[-1] #After last / in url
                    os.makedirs(os.path.dirname(postFilename), exist_ok = True) #Create folder if necessary
                    with open(postFilename, "wb") as mediaFile:
                        req = GET(mediaURL, headers = { "user-agent": userAgent }) #Request data and save to file
                        for chunk in req:
                            mediaFile.write(chunk)

                    print(timestamp() + "s | Downloaded " + mediaURL) #Logger


print(timestamp() + "s | Finished")
