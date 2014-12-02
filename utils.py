from operator import itemgetter
from textblob import TextBlob
from bcolors import BColors
from math import log
from datetime import datetime, timedelta
import logging
import re
import requests
import os


BC = BColors()
idfilename = 'ids.txt'
entriesfilename = 'entries.txt'
logging.basicConfig(level= logging.INFO, filename='messages.log')
TOLERANCE = 0.1
SONGSTOASSESS = 50
#epoch = datetime(1970, 1, 1)


'''
Input: A Date
Returns the number of seconds from the epoch to date.
'''
def epoch_seconds(date):
    td = date - epoch
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)


'''The hot formula. Should match the equivalent function in postgres.
Input: Score of entry, date of entry
Output: Hot score
'''
def hot(score, date):
    order = log(max(abs(score), 1), 10)
    sign = 1 if score > 0 else -1 if score < 0 else 0
    seconds = epoch_seconds(date) - 1134028003
    return round(order + sign * seconds / 45000, 7)


'''
Input: None
Output: Return a dictionary of words and their values from the textfile
''' 


def getWordValues():
        infile = open("wordValues.txt", "r")
        wordValues = {} 
        for line in infile:
                splitline = line.split()
                wordValues[splitline[0]] = splitline[1]
        infile.close()
        return wordValues


'''Input: AllEntries
Return list with top 10 songs
TODO
'''
def getTopTen(allEntries):
    sortedList = sorted(allEntries, key=itemgetter('count')) 
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


def rate(track):
    payload = track['post'].strip('\n')
    
    for word in track['title'].split() + [track['username']]:
        payload.replace(word,"")
        
    review = TextBlob(payload)

    if(review.sentiment.polarity > TOLERANCE):
        return 'pos', review.sentiment.polarity
    elif(review.sentiment.polarity < 0-TOLERANCE):
        return 'neg', review.sentiment.polarity
    return 'neutral', review.sentiment.polarity


def rate2(track):
    payload = track['post'].strip('\n')
#    (payload.replace(word,"") for word in track['title'].split())  # Removes all song title from post
    for word in track['title'].split():
        payload.replace(word,"")
    url = 'http://text-processing.com/api/sentiment/'
    request = eval(requests.post("http://text-processing.com/api/sentiment/", {"text":payload}).text)  # Turn JSON object into Dictionary
    if(abs(float(request['probability']['pos']) - float(request['probability']['neg']) ) > 0.05):
        return request['label']  # If the difference is greater than a tolerance return result
    return 'neutral'  # Otherwise return neutral



'''Input: None
Removes files from Disk
'''

def removeFiles():
    open(idfilename, 'w').close()
    open(entriesfilename, 'w').close()


'''Input: Takes the expanded Soundcloud URL
Returns whether or not link is valid
Put logic for the checking of whether the link is valid here
'''

regex = re.compile("((http|https)://soundcloud.com\/\S+\/\S+)")
def checkEntry(entry):
    if type(entry) is str:
        return bool(regex.match(entry)) and 'sets' not in entry
    return False


'''Input: Takes a twitter post string
Sanitizes the post to only be printable characters removing emojis and other chars 
'''


def sanitizeEntry(entry):
        return str(entry.encode('ascii',errors='ignore'))[1:].replace('/m.s','/s') #Accounts for mobile links

'''Input: None
Returns a list with all ids in ids.txt
'''
def readinIDs():
        idlist = list()
        infile = open(idfilename,'r')
        for line in infile:
                idlist.append(line)
        infile.close()  
        return idlist

'''
Input: ids (optional)
Output: Returns all entries in file and RAM
'''
def getAllIDs(ids=[]):
    readIDs = readinIDs()
    allIDs = [ID.strip() for ID in readIDs if ID not in ids]
    return allIDs + ids

'''
Input: entries (optional)
Output: Returns all entries in file and RAM
'''
def getAllEntries(entries=[]):        
    if not entries:
        print(BC.makeBlue("No entries are currently in RAM. All will be from File"))
    
    readEntries = readInEntries()
    allEntries = [entry for entry in readInEntries() if entry not in entries]  # Returns list of all current and past entries (list)
    
    if not readEntries:
        print(BC.makeGreen("No entries in file"))
    print(BC.makeError(str(len(allEntries))), "entries added")
    return sorted(allEntries+entries, key=itemgetter('count'),reverse=True) 
    #while(not repeatedEntries.empty()):  # Aquire all duplicate songs
    #    repeatedEntry = repeatedEntries.get()
    #allEntries['repeatedEntry]['count'] += 1

'''Input: entries and the filename to output to
Outputs all the IDs to a file to avoid duplicate results
'''
def outputIDsToFile(entries):
        infile = open(idfilename,"a")
        for entry in entries:
                infile.write(str(entry['userID'])+str(entry['soundcloudLink']+'\n'))
        infile.close()
                                

'''Input: entries and the filename to output to
Outputs all the IDs to a file to avoid duplicate results
'''


def outputEntriesToFile(entries):
        infile =  open(entriesfilename,"r+") 
        oldEntries= readInEntries()
        #if os.stat(entriesfilename)[6] != 0: #  If content in file
        try:
            if oldEntries:
                infile.seek(0)  # Seek to the beginning in order to overwrite not append
                infile.write(str(oldEntries + entries))  # Append if something exists
            else:
                logging.info("No old files")
                infile.seek(0)
                infile.write(str(entries))  # If empty then create
            logging.info("Outputted entries to  %s succesfully" % entriesfilename)
            print("Outputted entries to  %s succesfully" % BC.makeRed(entriesfilename))
            infile.close()
                
        except:
            logging.warning("Unable to output entries to file %s " % entriesfilename)
        
'''Input:None
Returns dictionary externally stored
'''


def readInEntries():
    with open(entriesfilename,'r') as infile:
        if os.stat(entriesfilename)[6] != 0: #  If content in file
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


def songExists():
    return False
    #return (song in database)
       
'''Input: None
Outputs Help info
'''

def printHelp(): 
        print(BC.makeRed("\nSoundcloud Ranker v 0.1. Phil Leonowens\n"))
        print(BC.makeRedText("1.)")," query twitter for entries")
        print(BC.makeRedText('2.)')," Read in entries from File")
        print(BC.makeRedText('3.)'),' output entries to file')
        print(BC.makeRedText('4.)'),' rate current entries')
        print(BC.makeRedText('5.)'),' remove entries file and idlist file')
        print(BC.makeRedText('6.)'),' clear entries and idlist from RAM')
        print(BC.makeRedText('7.)'),' print top 10')
       
        print(BC.makeGreen('p)'),' print list of entries')
        print(BC.makeGreen('c)'),' clear')
        print(BC.makeGreen('h)'),' help')
        print(BC.makeGreen('q)'),' quit')
