import pdb
import soundcloud
import queue
import threading
import logging
import subprocess
import sys
import os
from datetime import datetime
from operator import itemgetter
from twython import Twython
from bcolors import BColors
from utils import *
from entryManager import entryManager

BColors = BColors()
requestcount = 0
logging.basicConfig(filename='messages.log',level=logging.DEBUG)



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
                entryManager.update()
                '''
                ents,ids = populateEntries(idlist)
                entries += ents
                idlist += ids
                while(not repeatedEntries.empty()):
                    repeat = repeatedEntries.get()
                    for entry in entries:
                        #print(repeat, entry['soundcloudLink'])
                        if repeat == entry['soundcloudLink']:
                            print("Repeat Entry: ", repeat)
                            entry['count']+=1
                '''
            
            # 2 Rate Current Entries
            if command=='2':
                entryManager.rateEntries()

            # 3 Erase idlist and entries from file
            if command=='3':
                entryManager.removeFiles()
            # 4 Get Top 10
            if command == '4':
                for rank,entry in enumerate(entryManager.getTopTen()):
                    print (rank, entry['title'])
            # U Update database (Run Chronologically)
            if command == 'u':
               entryManager.update() 
            #D DEbug
            if command == 'd':
                pdb.set_trace()

            # P. Print List
            if command == 'p':
                printingEntries = entryManager.getEntries()
                if not printingEntries:
                    print( "Entries Not Populated")
                for result in printingEntries:
                        print(BColors.makeRed(result['username']) + ":")
                        print(result['post'])
                        print(BColors.makeBlue(result['soundcloudLink']))
                        print("Entries: " + BColors.makeBlue(str(result['count'])+ '\n'))
                print(BColors.makeGreen(str(len(printingEntries))), "entries printed out.")

            # c Clear
            if command =='c':
                subprocess.call('clear')
                printHelp()

if __name__ == '__main__':
    entryManager = entryManager() 
    main()
else:
    #f = open(os.devnull, 'w')
    #sys.stdout = f
    pass
