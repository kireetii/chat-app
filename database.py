import os
import certifi
from pymongo.mongo_client import MongoClient
from werkzeug.security import generate_password_hash
import User

ca = certifi.where()

MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
uri = f"mongodb+srv://kireeti:{MONGO_PASSWORD}@chat-app.hs8ogra.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, tlsCAFile=ca)

db = client.get_database('chat-db')
users = db.get_collection('users')
rooms = db.get_collection('rooms')
history = db.get_collection('history')

def save_user(name, password):
    password_hash = generate_password_hash(password)
    users.insert_one({'_id' : name, 'password' : password_hash})

def get_user(name):
    user_data = users.find_one({'_id' : name})
    return User.User(user_data['_id'], user_data['password']) if user_data else None

def add_room(code, members):
    rooms.insert_one({'_id' : code, 'members' : members})

def check_room(code):
    room_data = rooms.find_one({'_id' : code})
    return True if room_data else False

def update_room(code, add):
    room_data = rooms.find_one({'_id' : code})
    if not room_data: return
    members = room_data['members']
    new_values = {"$set": {'members': members+add}}
    rooms.update_one({'_id' : code}, new_values)

def delete_room(room):
    rooms.delete_one({'_id' : room})

def get_room(code):
    room_data = rooms.find_one({'_id' : code})
    return room_data

def save_content(code, content):
    history.insert_one({'room' : code, 'content' : content})

def delete_history(code):
    history.delete_many({'room' : code})

def get_history(code):
    return list(history.find({'room' : code}))