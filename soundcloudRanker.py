import soundcloud
# import urllib2
import re
import queue
import threading
import logging
from twython import Twython
from bcolors import BColors
from utils import *

BColors = BColors()
# GLOBAL VARIABLES
QUERYLENGTH = 1000  # How many twitter posts to search each time this is run
QUERY = "soundcloud.com/"
# Queue to store results
requestcount = 0
q = queue.Queue()
# Setup soundcloud client
SCClient = soundcloud.Client(client_id='fc2d2bb48658c6612489eed9aaa88dc4')
logging.basicConfig(filename='messages.log')

class NotATrack(Exception):
    pass

'''Input: Takes a soundcloud URL
Returns a track with a bunch of parameters
(see https://developers.soundcloud.com/docs/api/reference#tracks)
'''


def getTrackInfo(trackURL):
        global SCClient
        try:
            track = SCClient.get('/resolve', url=trackURL)
        except:
            logging.info(BColors.makeError("Track Not Found: " + trackURL))
            return False
        return track

'''Input: Track, twitter username, post, soundcloudLink and post_id
Returns a dictionary to append to the list if it works
'''


def makeEntry(track, username, post, post_id):
        sctitle = track.title
        scuser = track.user['username']
        sctrackduration = track.duration
        sctracktype = track.track_type
        soundcloudLink = track.permalink_url

        # To implement at the web level
        # purchase_url = track.purchase_url
        # download_url = track.download_url
        # artwork_url = track.artwork_url
        # if isinstance(sctracktype,str) and ( sctracktype == "original" or sctracktype == "remix"):
        return{'username': username, 'post': post, 'id': post_id,
               'soundcloudLink': soundcloudLink, 'user': scuser,
               'title': sctitle, 'duration': sctrackduration,
               'tracktype': sctracktype}
        #else:
        #       print("#####"+str(sctracktype)+"###")
        #       raise Exception("NotATrack")
'''Input: None
Creates a and fills it with the Soundcloud Links
contained in the first QUERYLENGTH amount of
twitter posts returned by the QUERY if they are valid
(determined by checkEntry())
'''


def populateList():
        global QUERYLENGTH
        global QUERY
        global q
        #global requestcount
    
        # App key and secret found by registering Twitter App
        APPSECRET = "CPMs6yeXwWRqV5Yow7QmOVZzfouC2UOT1AIykCZKYwBzuUrw0b"
        APPKEY = 'ngJbJ1mb6uHR0oZvTO5QjPUtz'
        twitter = Twython(APPKEY, APPSECRET)
        results = twitter.search(q=QUERY, lang='en',count=QUERYLENGTH)  #since_id =  currentID
        
        # Threading is efficient because we're waiting on api requests 
        threads = [threading.Thread(target=resolveEntry, args=(twitter, results, entry)) 
                  for entry in results["statuses"]]  # Thread Pool Generator
        for thread in threads:
            thread.start()

        for thread in threads:
                thread.join()
        
        songList = q
        return songList


def resolveEntry(twitter, results, entry):
        global q
        for url in entry["entities"]["urls"]:
                if(checkEntry(url)):
                        postid = entry["id"] 
                        username = entry["user"]["name"]
                        post = sanitizeEntry(entry["text"])  # Remove non ASCII characters
                        soundcloudLink = url["expanded_url"].split('?')[0] # Set the soundcloud link to be everything before a question mark
                        track = getTrackInfo(soundcloudLink)
                        if track is not False:
                                try:
                                        entry = makeEntry(track, username, post, postid)
                                        logging.info(BColors.makeRed(entry['user']) + ":\t"
                                                + BColors.makeBlue(entry['title']))
                                        q.put(entry)
                                #except NotATrack:
                                #       print(BColors.makeError('ERROR: NOT A SONG ' + soundcloudLink))
                                except:
                                        logging.warning(BColors.makeError('ERROR: SONG NOT FOUND ' + soundcloudLink))     
'''
The main function
'''


def main(): 
        # global requestcount
        searchQuery = populateList()
        entries = list()
        idlist = readinIDs()
        # Print each entry
        while(not searchQuery.empty()):
                result = searchQuery.get()
                if(result['id'] not in idlist):
                        entries.append(result)
                        print(BColors.makeRed(result['username']) + ":")
                        print(result['post'])
                        print(BColors.makeGreen(result['soundcloudLink']) + '\n')
                #print(BColors.makeError("\n The total count of entries is:"+ str(requestcount)))
        outputIDsToFile(entries, "ids.txt")
        

main()
