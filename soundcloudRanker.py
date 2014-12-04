import pdb
import soundcloud
import queue
import threading
import logging
import subprocess
from datetime import datetime
from operator import itemgetter
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
logging.basicConfig(filename='messages.log',level=logging.DEBUG)


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
'''Input: Takes songid
Gets song at that id
'''
def getEntry(songid):
    return [item for item in getAllEntries() if str(item['scid']) == songid][0]

'''Input: Track, twitter username, post, soundcloudLink and post_id
Returns a dictionary to append to the list if it works
TODO: Implement count
'''


def makeEntry(track, username,userID, post, post_id):
        sctitle = track.title
        scuser = track.user['username']
        sctrackduration = track.duration
        sctracktype = track.track_type
        soundcloudLink = track.permalink_url
        sc_id = track.id
        date = 0  # datetime.now() 
        artwork_url = track.artwork_url
        # To implement at the web level
        # purchase_url = track.purchase_url
        # download_url = track.download_url
        # if isinstance(sctracktype,str) and ( sctracktype == "original" or sctracktype == "remix"):
        return{'username': username, 'userID':userID, 'post': post, 'id': post_id,
               'soundcloudLink': soundcloudLink, 'user': scuser,
               'title': sctitle, 'duration': sctrackduration,
               'tracktype': sctracktype, 'scid': sc_id, 'count': 1,
               'date': date,'artwork' : artwork_url}

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
                    userID = entry["user"]["id_str"]
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
                            entry = makeEntry(track, username, userID, post, postid)
                            logging.info(BColors.makeRed(entry['user']) + ":\t"
                                        + BColors.makeBlue(entry['title']))
                            entryQueue.put(entry)
                        except AttributeError:
                                logging.warning(BColors.makeError('ERROR: SONG NOT FOUND %s' % soundcloudLink))     
                    else:
                        repeatedEntries.put(track['soundcloudLink'])
    

'''
Input:None
Runs commands to be executed when updating DB automatically
'''
def update():
    ents,ids = populateEntries(getAllIDs())  # First reads in new entries from twitter
    rateEntries(ents)  # Rates those entries

    outputIDsToFile(ents)  # Saves idlist to file
    outputEntriesToFile(ents)  # Saves entries to file
'''
Input: entries
Rates all entries
'''
def rateEntries(entries):
    if not entries :
        print("You must populate entries first")
    unratedEntries = [entry for entry in entries if 'rating' not in entry]
    if unratedEntries:
        for entry in unratedEntries:
            entry['rating'], entry['score'] = rate(entry)
            print (BColors.makeHeader(entry['post']), '\n', " has a rating of:", BColors.makeBlue(str(round(entry['score'],2))) , entry['rating'], "\n")
    else:
        print(BColors.makeRedText('All Entries are already rated'))
    print(BColors.makeGreen(str(len(list(unratedEntries)))),'entries rated.')

'''

'''
def populateEntries(existingIDs): 
    entriesAdded=0
    repeatEntries=0
    searchQuery = populateList()
    entriesToAdd = list()
    idlistToAdd = list()
    repeatLinks = list()
    # Print each entry in the queue and populate a list called entries
    while(not searchQuery.empty()):
        result = searchQuery.get()
        #It is a duplicate if a user links to the same song multiple times
        if(str(result['userID'])+str(result['soundcloudLink']) not in existingIDs):
            entriesAdded+= 1
            entriesToAdd.append(result)
            idlistToAdd.append(str(result['user'])+str(result['soundcloudLink']))
        else:
            repeatEntries+=1
    #pdb.set_trace()
    print(BColors.makeGreen(str(entriesAdded)), "entries added from Twitter Query. Total entries in RAM + File:", BColors.makeRed(str(entriesAdded+len(existingIDs))))
    print(BColors.makeRedText(str(repeatEntries)), "duplicate entries")
    
    return entriesToAdd, idlistToAdd


'''
The main function
'''


def main(): 
        # Init stuff
        entries = list()
        idlist = getAllIDs() # list()

        command = ''

        printHelp()
        while(command != 'q'):
            command = input("Enter a command:")

            # h. Help
            if(command == 'h'):
                printHelp()
         
         # 1. Populate List
            if(command == '1'):
                ents,ids = populateEntries(idlist)
                entries += ents
                idlist += ids
                while(not repeatedEntries.empty()):
                    repeat = repeatedEntries.get()
                    for entry in entries:
                        if repeat == entry['soundcloudLink']:
                            entry['count']+=1
                
                '''
                entriesAdded=0
                repeatEntries=0
                searchQuery = populateList()
                # Print each entry in the queue and populate a list called entries
                while(not searchQuery.empty()):
                    result = searchQuery.get()
                    if(result['id'] not in idlist):
                        entriesAdded+= 1
                        entries.append(result)
                        idlist.append(result['id'])
                    else:
                        repeatEntries+=1
                print(BColors.makeGreen(str(entriesAdded)), "entries added from Twitter Query. Total entries:", BColors.makeRed(str(len(entries))))
                print(BColors.makeRedText(str(repeatEntries)), "duplicate entries")
                '''

            # 2 Read in Entries from file (Overwrites RAM)
            if command == '2' :
                entries = getAllEntries(entries)
                idlist = getAllIDs()

            # 3 Output Entries to File
            logging.info(BColors.makeError(" The total count of entries is: %s" % str(requestcount)))
            if command == '3': 
                if(entries):
                    outputIDsToFile(entries)  # Makes file to avoid duplicate IDs
                    outputEntriesToFile(entries)  # Outputs entries to use in ranking
                    # wordValues = getWordValues()
                else:
                    print( BColors.makeError("Entries Not Populated"))
            
            # 4 Rate Current Entries
            if command=='4':
                rateEntries(entries)

            # 5 Erase idlist and entries from file
            if command=='5':
                removeFiles()
            # 6 Erase idlist and entries from RAM
            if command == '6':
                entries=list()
                idlist=list()
            # 7 Get Top 10
            if command == '8':
                for rank,entry in enumerate(getTopTen(entries)):
                    print (rank, entry['title'])
            # U Update database (Run Chronologically)
            if command == 'u':
               update() 

            # P. Print List
            if command == 'p':
                if not entries:
                    print( "Entries Not Populated")
                for result in entries:
                        print(BColors.makeRed(result['username']) + ":")
                        print(result['post'])
                        print(BColors.makeBlue(result['soundcloudLink']) + '\n')
                print(BColors.makeGreen(str(len(entries))), "entries printed out.")

            # c Clear
            if command =='c':
                subprocess.call('clear')
                printHelp()


if __name__ == '__main__':
    main()
