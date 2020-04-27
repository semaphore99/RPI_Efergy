import sys
import pymongo


# connect to Mongo
#client = pymongo.MongoClient("mongodb+srv://dbWriter:<password>@cluster0-scaef.mongodb.net/test?retryWrites=true&w=majority")
#db = client.test


for line in sys.stdin:
    sys.stdout.write("process_efergy...hello!")
    sys.stdout.write(line)
