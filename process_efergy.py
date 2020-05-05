import sys
import pymongo
from datetime import datetime
import time

def GetLastHourReadings():

    return []


secret = open("secret", "r")
credentials = secret.read()

client = pymongo.MongoClient("mongodb+srv://" + credentials.strip() + "@cluster0-i2cea.mongodb.net/test?retryWrites=true&w=majority")
#client = pymongo.MongoClient("mongodb+srv://" + credentials.strip() + "@cluster0-scaef.mongodb.net/test?retryWrites=true&w=majority")
efergyDB = client.Efergy
testCollection = efergyDB.RawSamples
currentReadingCollection = efergyDB.CurrentReadings

# See if there's already a document for today. This is in case the script restarts for whatever reason
searchId = datetime.now().strftime("%Y%m%d")
existingDoc = testCollection.find_one({'_id':searchId})

if not (existingDoc is None):
    readings = existingDoc['Readings']
else:
    readings = []


thisHour = 0
lastTimestamp = ""
for line in sys.stdin:
    # example line: 04/26/20,21:57:48,2603.437500
    now = datetime.now()
    print("Processing: " + line)
    tokens = line.strip().split(",")
    docId = now.strftime("%Y%m%d")
    try:
        wattage = float(tokens[-1].strip())
    
        timestamp = now.strftime("%Y%m%d-%H%M-%S")
        #really only interested in the last number
        reading = {'Timestamp':timestamp, 'Reading':wattage}
        readings.append(reading) #readings is a leftover when i was uploading all readings for a day repeatedly.
        document = {
            '_id': docId,
            'Readings': [reading]
        }
        key = {'_id': docId}
        searchId = datetime.now().strftime("%Y%m%d")
        existingDoc = testCollection.find_one({'_id':searchId}, {'_id': 1})
        if (existingDoc is None):
            testCollection.replace_one(key, document, upsert=True)
        else:
            testCollection.update_one(key, {'$push': {'Readings': reading}})
        
        #the current reading
        key = {'_id': "Now"}
        document = {
            '_id': "Now",
            'Timestamp': timestamp,
            'Reading': wattage
        }
        currentReadingCollection.replace_one(key, document, upsert=True)

        #last hour's readings
        index = 0
        while (index < len(readings)):
            ts = time.mktime(time.strptime(readings[index]['Timestamp'], '%Y%m%d-%H%M-%S'))
            readingTime = datetime.fromtimestamp(ts)
            if (now - readingTime).total_seconds() < 3600:
                lastHourReadings = readings[index:]
                document = {
                    '_id': "LastHour",
                    'Timestamp': timestamp,
                    'Readings': lastHourReadings
                }
                key = {'_id': "LastHour"}
                testCollection.replace_one(key, document, upsert=True)
                break
            index += 1

    except ValueError:
        print(tokens[-1] + " is not a number")


