from pymongo import MongoClient

username = 'Enter Username'
password = 'Enter Password'

client = MongoClient(f'mongodb+srv://{username}:{password}@tutorialmongodb.2hatyig.mongodb.net/?retryWrites=true&w=majority')

db = client.mytvlist


