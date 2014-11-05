import soundcloud
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
entryQueue = queue.Queue()
repeatedEntries = queue.Queue()
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
        try:
            track = SCClient.get('/resolve', url=trackURL)
        except:
            logging.info(BColors.makeError("Track Not Found: %s" % trackURL))
            return False
        return track

'''Input: Track, twitter username, post, soundcloudLink and post_id
Returns a dictionary to append to the list if it works
TODO: Implement count
'''


def makeEntry(track, username, post, post_id):
        sctitle = track.title
        scuser = track.user['username']
        sctrackduration = track.duration
        sctracktype = track.track_type
        soundcloudLink = track.permalink_url
        sc_id = track.id
        # To implement at the web level
        # purchase_url = track.purchase_url
        # download_url = track.download_url
        # artwork_url = track.artwork_url
        # if isinstance(sctracktype,str) and ( sctracktype == "original" or sctracktype == "remix"):
        return{'username': username, 'post': post, 'id': post_id,
               'soundcloudLink': soundcloudLink, 'user': scuser,
               'title': sctitle, 'duration': sctrackduration,
               'tracktype': sctracktype, 'scid': sc_id, 'count': 1}
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
        # App key and secret found by registering Twitter App
        APPSECRET = "CPMs6yeXwWRqV5Yow7QmOVZzfouC2UOT1AIykCZKYwBzuUrw0b"
        APPKEY = 'ngJbJ1mb6uHR0oZvTO5QjPUtz'
        twitter = Twython(APPKEY, APPSECRET)
        results = twitter.search(q=QUERY, lang='en', count=QUERYLENGTH)  # since_id =  currentID
        
        # Threading is efficient because we're waiting on api requests 
        threads = [threading.Thread(target=resolveEntry, args=(results, entry)) 
                  for entry in results["statuses"]]  # Thread Pool Generator
        for thread in threads:
            thread.start()

        for thread in threads:
                thread.join()
        
        songList = entryQueue
        return songList

'''Input: twitter client, results, entry
Extracts info and makes an entry in the queue
from the inputted list of twitter posts
'''
def resolveEntry(results, entry):
        global requestcount
        for url in entry["entities"]["urls"]:
            if(checkEntry(url['expanded_url'])):
                    requestcount += 1
                    postid = entry["id"]
                    try:
                        username = entry["user"]["name"]
                    except KeyError:
                        logging.warning('Couldnt store username at %s' % username)
                    except TypeError:
                        logging.warning(entry['user'])
                    try:
                        post = sanitizeEntry(entry["text"])  # Remove non ASCII characters
                    except KeyError:
                        try:
                            post = sanitizeEntry(entry['post'])
                        except KeyError:
                            logging.warning("Couldnt resolve entry at entry['text'] %s" % str( entry))
                    soundcloudLink = url["expanded_url"].split('?')[0] # Set the soundcloud link to be everything before a question mark
                    track = getTrackInfo(soundcloudLink)
                    if track is not False:
                        if not songExists():  # If the song is unique in the database
                            try:
                                entry = makeEntry(track, username, post, postid)
                                logging.info(BColors.makeRed(entry['user']) + ":\t"
                                            + BColors.makeBlue(entry['title']))
                                entryQueue.put(entry)
                            except AttributeError:
                                    logging.warning(BColors.makeError('ERROR: SONG NOT FOUND %s' % soundcloudLink))     
                        else:
                            repeatedEntries.put(track['user']+'\t'+track['title'])

'''
The main function
'''


def main(): 
        searchQuery = populateList()
        entries = list()
        idlist = readinIDs()
        # Print each entry in the queue and populate a list called entries
        while(not searchQuery.empty()):
            result = searchQuery.get()
            if(result['id'] not in idlist):
                entries.append(result)
                print(BColors.makeRed(result['username']) + ":")
                print(result['post'])
                print(BColors.makeGreen(result['soundcloudLink']) + '\n')
        allEntries = readInEntries()+entries  # Returns list of all current and past entries (list)
        while(not repeatedEntries.empty()):  # Aquire all duplicate songs
            repeatedEntry = repeatedEntries.get()
            #allEntries['repeatedEntry]['count'] += 1
            pass

        logging.info(BColors.makeError(" The total count of entries is: %s" % str(requestcount)))
        outputIDsToFile(entries)  # Makes file to avoid duplicate IDs
        outputEntriesToFile(entries)  # Outputs entries to use in ranking
        #wordValues = getWordValues()
       # (entry['rating'] = rate(entry) for entry in entries)
        
        for entry in entries:
            print (str(entry['post']) + " has a rating of: " + str(rate(entry)) + "\n")
        
        # getTopTen(entriesDict())
main()
