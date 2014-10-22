import logging
import re
import os
idfilename = 'ids.txt'
entriesfilename = 'entries.txt'
logging.basicConfig(level= logging.INFO, filename='messages.log')

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
    for entry in allEntries:
        pass

'''Input: A Track
The rating of a track
TODO: Implement All
'''


def rate(track):
        tweetText = track['post']
        return 5

'''Input: Takes the expanded Soundcloud URL
Returns whether or not link is valid
Put logic for the checking of whether the link is valid here
'''


def checkEntry(entry):
    if type(entry) is str:
        return bool(re.match("((http|https)://soundcloud.com\/\S+\/\S+)", entry)) and 'sets' not in entry
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
        global idfilename
        idlist = list()
        infile = open(idfilename,'r')
        for line in infile:
                idlist.append(line)
        infile.close()  
        return idlist

'''Input: entries and the filename to output to
Outputs all the IDs to a file to avoid duplicate results
'''


def outputIDsToFile(entries):
        global idfilename
        infile = open(idfilename,"a")
        for entry in entries:
                infile.write(str(entry['id'])+'\n')
        infile.close
                                

'''Input: entries and the filename to output to
Outputs all the IDs to a file to avoid duplicate results
'''


def outputEntriesToFile(entries):
        global entriesfilename
        infile =  open(entriesfilename,"r+") 
        oldEntries=list()
        for line in infile:
            oldEntries = oldEntries + eval(line)
        if os.stat(entriesfilename)[6] != 0: #  If content in file
            try:
                if oldEntries:
                    infile.seek(0)  # Seek to the beginning in order to overwrite not append
                    infile.write(str(oldEntries + entries))  # Append if something exists
                    logging.info("Outputted entries to " + entriesfilename + "succesfully")
                    
            except:
                logging.warning("Unable to output entries to file" + entriesfilename)
        else:
            logging.info("Empty File")
            infile.write(str(entries))  # If empty then create
        infile.close()

'''Input:None
Returns dictionary externally stored
'''


def readInEntries():
    global entriesfilename
    with open(entriesfilename,'r') as infile:
        try:
            currentLine = eval(infile.read())
            return currentLine
        except TypeError:
            logging.warning('Cant parse entry at '+ infile.read())
            return []

'''Input: Track
Checks to see if song already exists in database
TODO: Add logic to find if song already exists
whether by identical URL or similar Artist / Track
'''


def songExists():
    return False
    #return (song in database)
        
