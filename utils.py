import logging
import os
idfilename = 'ids.txt'
entriesfilename = 'entries.txt'
logging.basicConfig(filename='messages.log')

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


def trackRating(track):
        tweetText = track['post']
        return 5

'''Input: Takes the expanded Soundcloud URL
Returns whether or not link is valid
Put logic for the checking of whether the link is valid here
TODO: Make a regular expression to ensure link is to a track and not an artist
'''


def checkEntry(entry):
        #Simpler Check w/o regex
        if "//soundcloud.com/" in entry["expanded_url"] and '/sets' not in entry['expanded_url']:
                return True
        return False
'''
        soundcloudRegex = re.compile("(soundcloud.com\/\S+\/\S+)")
        print (str(entry["expanded_url"]) + str( re.match(soundcloudRegex,str(entry["expanded_url"]))))
        return  re.match(soundcloudRegex,str(entry["expanded_url"])):
'''


'''Input: Takes a twitter post string
Sanitizes the post to only be printable characters removing emojis and other chars 
'''


def sanitizeEntry(entry):
        return str(entry.encode('ascii',errors='ignore'))[1:]

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
        with open(entriesfilename,"a") as infile:
            if os.stat(entriesfilename)[6] != 0:
                infile.write(',')                   # If file isn't empty, adds a comma so it can add to the list
            infile.write(str(entries))

    
'''Input:None
Returns dictionary externally stored
'''


def readInEntries():
    global entriesfilename
    with open(entriesfilename,'r') as infile:
        try:
            return eval(infile.read())
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
