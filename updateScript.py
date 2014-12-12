from entryManager import entryManager
import logging

logging.basicConfig(filename='updater.log',level=logging.DEBUG)
entryManager = entryManager()
entryManager.update()
