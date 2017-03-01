# -*- coding: utf-8 -*-

from requests import get as GET
import json
import time
import os
import errno


getLinks = False
getComments = True
targetFolder = "C:\\Users\\Aarop\\rips\\reddit\\"
targetSubreddit = "twice"
userAgent = "desktop:us.noxim.ripit:v0.0.0 (by /u/noxime)"



if(getLinks):

    print("Fetching all posts of " + targetSubreddit)

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

        print("Finished reading page: " + str(currentPage) + ", at " + str(totalPosts) + " posts now")

        currentPage += 1
        if "next_page" in page["metadata"]:
            page = json.loads(GET(page["metadata"]["next_page"], headers = { "user-agent": userAgent }).content)
        else:
            stillLinks = False;

    linksFile.close();
    print("Done fetching all links, saved to " + targetFolder + "links")

if(getComments):
    print("Fetching comments")

    entries = [line.rstrip() for line in open(targetFolder + "links")] #Get all lines
    for index, entry in enumerate(entries):
    #entry = entries[8072] #DEBUG
    #if(True):

        print("Fetching " + entry + ", " + str(index) + "/" + str(len(entries)))
        data = GET("https://reddit.com/r/" + targetSubreddit + "/comments/" + entry + "/.json", headers = { "user-agent": userAgent }).text

        postFilename = targetFolder + entry + "\\post.json"
        os.makedirs(os.path.dirname(postFilename), exist_ok = True) #Create folder if necessary
        with open(postFilename, "w") as post:
            post.write(str(data))

    print("All comments fetched")
