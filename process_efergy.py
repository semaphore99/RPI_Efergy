import sys
import pymongo
from datetime import datetime

secret = open("secret", "r")
credentials = secret.read()

client = pymongo.MongoClient("mongodb+srv://" + credentials + "@cluster0-i2cea.mongodb.net/test?retryWrites=true&w=majority")
efergyDB = client.Efergy
testCollection = efergyDB.test

thisHour = 0
readings = []
for line in sys.stdin:
    # example line: 04/26/20,21:57:48,2603.437500
    now = datetime.now()
    print("Processing: " + line)
    tokens = line.split(",")
    docId = str(now.year) + str(now.month) + str(now.day)
    
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    #really only interested in the last number
    reading = {'timestamp':timestamp, 'reading':tokens[-1]}
    readings.append(reading)
    document = {
        '_id': docId,
        'readings': readings
    }
    key = {'_id': docId}
    testCollection.replace_one(key, document, upsert=True)


