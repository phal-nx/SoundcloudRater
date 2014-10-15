import string
import soundcloud
from twython import Twython
from bcolors import BColors

#GLOBAL VARIABLES
queryLength = 100 #How many twitter posts to search each time this is run
query = 'soundcloud.com/'
#Setup soundcloud client
SCClient =  soundcloud.Client(client_id = 'fc2d2bb48658c6612489eed9aaa88dc4')

'''
Input: Takes a soundcloud URL
Output: Returns a track with a bunch of parameters (see https://developers.soundcloud.com/docs/api/reference#tracks) 
'''
def getTrackInfo(trackURL):
	global SCClient
	try:	
		track = SCClient.get('/resolve', url=trackURL)
	except:
		print(BColors.makeError("Track Not Found: " + trackURL))
		return False
	return track 

'''
Input: Takes the expanded Soundcloud URL
Output: Returns whether or not link is valid
Put logic for the checking of whether the link is valid here
TODO: Make a regular expression to ensure link is to a track and not an artist
'''
def checkEntry(entry):
	if "//soundcloud.com/" in entry["expanded_url"]:
		return True
	return False

'''
Input: Takes a twitter post string
Output: Sanitizes the post to only be printable characters removing emojis and other chars 
'''
def sanitizeEntry(entry):
	return str(entry.encode('ascii',errors='ignore'))[1:]

'''
Input: Takes track, twitter username, post, soundcloudLink and post_id
Output: Returns a dictionary to append to the list if it works
'''
def makeEntry(track,username,post,post_id):
	sctitle = track.title
	scuser = track.user['username']
	sctrackduration = track.duration
	sctracktype = track.track_type
	soundcloudLink = track.permalink_url

	##To implement at the web level
	#purchase_url = track.purchase_url
	#download_url = track.download_url
	#artwork_url = track.artwork_url
	
	return{'username':username,'post':post,'id':post_id,'soundcloudLink':soundcloudLink,'user':scuser,'title':sctitle,'duration':sctrackduration,'tracktype':sctracktype}

'''
Creates a list and fills it with the Soundcloud Links contained in the first queryLength
amount of twitter posts returned by the query if they are valid (determined by checkEntry())
'''
def populateList():
	global queryLength
	global query
	songList = []

	#App key and secret found by registering Twitter App
	APPSECRET = "CPMs6yeXwWRqV5Yow7QmOVZzfouC2UOT1AIykCZKYwBzuUrw0b"
	APPKEY = 'ngJbJ1mb6uHR0oZvTO5QjPUtz'
	twitter = Twython(APPKEY, APPSECRET)
	results = twitter.search(q=query, lang='en',count=queryLength) #since_id = current_id_searched

	for entry in results["statuses"]:
		for url in entry["entities"]["urls"]:
			if(checkEntry(url)):
				print(entry)
				postid= 5#entry['id_str'] 
				username = entry["user"]["name"]
				post = sanitizeEntry(entry["text"]) # Remove non ASCII characters
				soundcloudLink = url["expanded_url"].split('?')[0] #Set the soundcloud link to be everything before a question mark
				track = getTrackInfo(soundcloudLink)
				if track:
					try:
						entry = makeEntry(track,username,post,postid)
						print(BColors.makeRed(entry['user']), ":\t", BColors.makeBlue(entry['title']))
						songList.append(entry)
					except:
						print(BColors.makeError('ERROR: SONG NOT FOUND ' +soundcloudLink))	
	return songList

'''
The main function
'''
def main():
	
	searchQuery =  populateList()

	#Print each entry

	for result in searchQuery:
		print(BColors.makeRed(result['username']) + ":")
		print(result['post'])
		print(BColors.makeGreen(result['soundcloudLink']) + '\n')


main()
