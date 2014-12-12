import queue
import threading
import logging
import os
import soundcloud
import pdb
from utils import *
from bcolors import BColors
from operator import itemgetter
from twython import Twython

BColors = BColors()
entryQueue = queue.Queue()
repeatedEntries = queue.Queue

class entryManager:
    
    QUERY = "soundcloud.com/"
    QUERYLENGTH = 1000
    # Setup soundcloud client
    SCClient = soundcloud.Client(client_id='fc2d2bb48658c6612489eed9aaa88dc4')

    logging.basicConfig(filename='messages.log',level=logging.DEBUG)
    entries = list()
    idlist = list()
    entriesfilename = 'entries.txt'
    idfilename = 'ids.txt'

    def __init__(self):
        self.entries = self.getAllEntries()
        self.idlist = self.getAllIDs()
        

    def getAllEntries(self):        
        readEntries = self.readInEntries()
        allEntries = [entry for entry in readEntries if entry not in self.entries]  
        return sorted(allEntries + self.entries, key=itemgetter('count'),reverse=True) 


    '''Input: None
    Removes files from Disk
    '''

    def removeFiles(self):
        open(idfilename, 'w').close()
        open(entriesfilename, 'w').close()
        self.entries=list()
        self.idlist=list()

    '''Input: Takes songid
    Gets song at that id
    '''
    def getEntry(self, songid):
        return [item for item in self.getEntries() if str(item['scid']) == songid][0]
   
    '''Input: Takes songid as identifier
    Increments count at that id
    '''
    def incrementCount(self, songid):
        self.getEntry(songid)['count']+=1
    
    
    '''Input: Track, twitter username, post, soundcloudLink and post_id
    Returns a dictionary to append to the list if it works
    TODO: Implement count
    '''

    def makeEntry(self,track, username,userID, post, post_id):
        sctitle = track.title
        scuser = track.user['username']
        sctrackduration = track.duration
        sctracktype = track.track_type
        soundcloudLink = track.permalink_url
        sc_id = track.id
        date = 0  # datetime.now() 
        artwork_url = track.artwork_url
        # purchase_url = track.purchase_url
        # download_url = track.download_url
        return{'username': username, 'userID':userID, 'post': post.strip(),
                'id': post_id,
               'soundcloudLink': soundcloudLink, 'user': scuser,
               'title': sctitle, 'duration': sctrackduration,
               'tracktype': sctracktype, 'scid': sc_id, 'count': 1,
               'date': date,'artwork' : artwork_url}
    '''
    Input: ids (optional)
    Output: Returns all entries in file and RAM
    '''
    def getAllIDs(self):
        readIDs = self.readinIDs()
        allIDs = [ID.strip() for ID in readIDs if ID not in self.getIDList()]
        return allIDs + self.getIDList()

    '''Input: None
    Returns a list with all ids in ids.txt
    '''
    def readinIDs(self):
            idlist = list()
            infile = open(self.idfilename,'r')
            for line in infile:
                    idlist.append(line)
            infile.close()  
            return idlist


    '''
    Input:None
    Runs commands to be executed when updating DB automatically
    '''
    def update(self):
        ents, ids = self.populateEntries()  # First reads in new entries from twitter
        self.rateEntries(ents)  # Rates those entries
        self.entries += ents
        self.idlist += ids
        self.outputIDsToFile()  # Saves idlist to file
        self.outputEntriesToFile()  # Saves entries to file

    '''Input: entries and the filename to output to
    Outputs all the IDs to a file to avoid duplicate results
    '''
    def outputIDsToFile(self):
            infile = open(self.idfilename, "a")
            for entry in self.getEntries():
                    infile.write(str(entry['userID'])+str(entry['soundcloudLink']+'\n'))
            infile.close()
    
    '''Input: None
    Creates a and fills it with the Soundcloud Links
    contained in the first QUERYLENGTH amount of
    twitter posts returned by the QUERY if they are valid
    (determined by checkEntry())
    '''


    def queryTwitter(self):
        # App key and secret found by registering Twitter App
        APPSECRET = "CPMs6yeXwWRqV5Yow7QmOVZzfouC2UOT1AIykCZKYwBzuUrw0b"
        APPKEY = 'ngJbJ1mb6uHR0oZvTO5QjPUtz'
        twitter = Twython(APPKEY, APPSECRET)
        results = twitter.search(q=self.QUERY, lang='en', count=self.QUERYLENGTH)  # since_id =  currentID
        #pdb.set_trace() 
        resultsStatuses = {v['id']:v for v in results['statuses']}.values()
        # Threading is efficient because we're waiting on api requests 
        threads = [threading.Thread(target=self.resolveEntry, args=(entry,)) 
                  for entry in resultsStatuses]  # Thread Pool Generator
        for thread in threads:
            thread.start()

        for thread in threads:
                thread.join()
        
        songList = entryQueue
        return songList

    '''Input: Takes a soundcloud URL
    Returns a track with a bunch of parameters
    (see https://developers.soundcloud.com/docs/api/reference#tracks)
    '''


    def getTrackInfo(self, trackURL):
            try:
                track = self.SCClient.get('/resolve', url=trackURL)
            except:
                logging.info(BColors.makeError("Track Not Found: %s\n" % trackURL))
                return False
            return track

    '''Input: twitter client, results, entry
    Extracts info and makes an entry in the queue
    from the inputted list of twitter posts
    '''
    def resolveEntry(self,entry):
        allEntries = self.getEntries()
        requestcount=0
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
                track = self.getTrackInfo(soundcloudLink)
                if track:
                    if not self.songExists(track.permalink_url):  # If the song is unique in the database
                        try:
                            entry = self.makeEntry(track, username, userID, post, postid)
                            logging.info(BColors.makeRed(entry['user']) + ":\t"
                                        + BColors.makeBlue(entry['title']+'\n'))
                            entryQueue.put(entry)
                        except AttributeError:
                                logging.warning(BColors.makeError('ERROR: SONG NOT FOUND %s' % soundcloudLink))     
                    else:
                        try:
                            incrementCount(track.permalink_url)
                            #repeatedEntries.put(track.permalink_url)
                        except:
                            logging.warning(BColors.makeError('PERMALINK NOT FOUND: %s' % track.title))


    '''
    Input: entries
    Rates all entries
    '''
    def rateEntries(self, entries=[]):
        # If entries passed in, rate those entries
        if entries:
            unratedEntries = [entry for entry in entries if 'rating' not in entry]
            if unratedEntries:
                for entry in unratedEntries:
                    entry['rating'], entry['score'] = self.rate(entry)
                    print (BColors.makeHeader(entry['post']), '\n', " has a rating of:", BColors.makeBlue(str(round(entry['score'],2))) , entry['rating'], "\n")
            else:
                print(BColors.makeRedText('All Entries are already rated'))
        # If no entries inputted, then re-rate existing ones
        else:
            print("Re rating existing entries: ")
            entriesToRate = self.getEntries()
            for entry in entriesToRate:
                entry['rating'], entry['score'] = self.rate(entry)
                print (BColors.makeHeader(entry['post']), '\n', " has a new rating of:", BColors.makeBlue(str(round(entry['score'],2))) , entry['rating'], "\n")
            return
        print(BColors.makeGreen(str(len(list(unratedEntries)))),'entries rated.')

    '''

    '''
    def populateEntries(self): 
        entriesAdded=0
        repeatEntries=0
        searchQuery = self.queryTwitter()
        entriesToAdd = list()
        idlistToAdd = list()
        repeatLinks = list()
        # Print each entry in the queue and populate a list called entries
        while(not searchQuery.empty()):
            result = searchQuery.get()
            #It is a duplicate if a user links to the same song multiple times
            if(str(result['userID'])+str(result['soundcloudLink']) not in self.getIDList()):
                entriesAdded+= 1
                entriesToAdd.append(result)
                idlistToAdd.append(str(result['user'])+str(result['soundcloudLink']))
            else:
                repeatEntries+=1
        #pdb.set_trace()
        print(BColors.makeGreen(str(entriesAdded)), "entries added from Twitter Query. Total entries in RAM + File:", BColors.makeRed(str(entriesAdded+len(self.getIDList()))))
        print(BColors.makeRedText(str(repeatEntries)), "duplicate posts")
        
        return entriesToAdd, idlistToAdd



    def getIDList(self):
        return self.idlist

    def getEntries(self):
        return self.entries
    '''
    Get highest count value
    '''
    def getHighestCount(self):
        return sorted(self.getAllEntries(), key=itemgetter('count'),reverse=True)[:3]

    '''Input: AllEntries
    Return list with top 10 songs
    TODO
    '''
    def getTopTen(self):
        sortedList = sorted(self.getEntries(), key=itemgetter('count'),reverse=True) 
        topten=list()
        for i in range(SONGSTOASSESS):
            topEntries.append(sortedList[i])
        try:
            for entry in topEntries:
                entryDate = entry['date']
                entryScore = entry['score']
                entry['hot'] = hot(entryScore, entryDate)
        except:
            print(BC.makeError("You must rate all tracks first"))
            return list()
        topTen = sorted(topEntries, key=itemgetter('hot'))[:10]
        return topTen

    '''Input: A Track
    The rating of a track
    TODO: Implement All
    '''


    def rate(self, track):
        payload = track['post'].strip('\n')
        
        for word in track['title'].split() + [track['username']]:
            payload.replace(word,"")
            
        review = TextBlob(payload)

        if(review.sentiment.polarity > TOLERANCE):
            return 'pos', review.sentiment.polarity
        elif(review.sentiment.polarity < 0-TOLERANCE):
            return 'neg', review.sentiment.polarity
        return 'neutral', review.sentiment.polarity

    '''Input: entries and the filename to output to
    Outputs all the IDs to a file to avoid duplicate results
    '''


    def outputEntriesToFile(self):
            infile =  open(self.entriesfilename,"r+") 
            currentEntries = self.getEntries()
            #if os.stat(self.entriesfilename)[6] != 0: #  If content in file
            try:
                logging.info("No old files")
                infile.seek(0)
                infile.write(str(currentEntries))  # If empty then create
                logging.info("Outputted entries to  %s succesfully" % self.entriesfilename)
                print("Outputted entries to  %s succesfully" % BC.makeRed(self.entriesfilename))
                infile.close()
                    
            except:
                logging.warning("Unable to output entries to file %s " % self.entriesfilename)
            
    '''Input:None
    Returns dictionary externally stored
    '''


    def readInEntries(self):
        with open(self.entriesfilename,'r') as infile:
            if os.stat(self.entriesfilename)[6] != 0: #  If content in file
                try:
                    currentLine = eval(infile.read())
                    return currentLine
                except TypeError:
                    logging.warning('Cant parse entry at %s' % infile.read())
            return []

    '''Input: Track
    Checks to see if song already exists in database
    TODO: Add logic to find if song already exists
    whether by identical URL or similar Artist / Track
    '''


    def songExists(self, track):
        for currentEntry in self.getEntries():
            if track == currentEntry['soundcloudLink']:
                return True
        return False

def main():
   pass 

if __name__ == "__main__":
    main()
