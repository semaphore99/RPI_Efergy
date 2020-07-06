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
hourlyCollection = efergyDB.HourlyReadings
dailyCollection = efergyDB.DailyReadings
monthlyCollection = efergyDB.MonthlyReadings
currentReadingCollection = efergyDB.CurrentReadings

# See if there's already a document for today. This is in case the script restarts for whatever reason
searchId = datetime.now().strftime("%Y%m%d")
existingDoc = dailyCollection.find_one({'_id':searchId})

if not (existingDoc is None):
    readings = existingDoc['Readings']
else:
    readings = []


thisHour = 0
lastUpdate = datetime.now()
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
        print(str(len(readings)) + " entries in readings array")
        document = {
            '_id': docId,
            'Readings': [reading]
        }
        key = {'_id': docId}
        searchId = datetime.now().strftime("%Y%m%d")
        existingDoc = dailyCollection.find_one({'_id':searchId}, {'_id': 1})
        if (existingDoc is None):
            print("Adding new daily record")
            dailyCollection.replace_one(key, document, upsert=True)
            lastUpdate = now
        else:
            #to avoid having too many entries in the daily records, only add a reading
            # every minute.
            print("seconds elapsed since last update: " + str((now - lastUpdate).total_seconds()))
            if lastUpdate != None and (now - lastUpdate).total_seconds() > 60:
                print("Adding new entry to daily readings")
                dailyCollection.update_one(key, {'$push': {'Readings': reading}})
                lastUpdate = now

        
        #the current reading
        key = {'_id': "Now"}
        document = {
            '_id': "Now",
            'Timestamp': timestamp,
            'Reading': wattage
        }
        currentReadingCollection.replace_one(key, document, upsert=True)

        #last hour's readings - 
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
                hourlyCollection.replace_one(key, document, upsert=True)
                break
            index += 1
        

        #update monthly numbers
        total = 0
        for thing in readings:
            total = total + thing['Reading']
        print(str(len(readings)) + " readings for a total of " + str(total) + " Wh")
        print("Averge wattage so far today: " + str(total / len(readings)) + " Wh")
        wattageSoFar = (now.hour + now.minute / 60) * total / len(readings) / 1000
        wattageForDay = total * 24 / len(readings) /  1000
        print("Total wattage so far today: " + str(wattageSoFar) + "kWh")
        print("Forecast total usage today: " + str(wattageForDay) + "kWh")
        if (lastUpdate != None):
            print("lastUpdate.day = " + str(lastUpdate.day) + ", now.day = " + str(now.day))
            docId = now.strftime("%Y%m%d")

            # find average energy usage for the day. 
            # I'm sure there's a better way in python to do this
            
            wattage = total / len(readings) * 24
            key = {'_id': docId}
            document = {
                '_id': docId,
                'Reading': wattageSoFar
            }
            monthlyCollection.replace_one(key, document, upsert=True)

            if lastUpdate.day != now.day:
                #a different day, so clear yesterday's readings
                readings = readings[-1:]

        

    except ValueError:
        print(tokens[-1] + " is not a number")


