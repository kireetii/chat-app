from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, send
from views import view
from flask import session
from flask_login import LoginManager
import datetime
from database import get_user, check_room, delete_room, update_room, get_room, save_content, delete_history


app = Flask(__name__)
app.config.from_object('config.Config')
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'views.login'

app.register_blueprint(view, url_prefix="/")

@socketio.on('connect')
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    join_room(room)
    update_room(room, add=1)
    time = datetime.datetime.now().strftime('%H : %M')
    send({'name': name, 'message': ' has entered the room', 'time' : time}, to=room)
    print(f"{name} joined the room {room}")

@socketio.on('disconnect')
def disconnect():
    name = session.get('name')
    room = session.get('room')
    leave_room(room)
    room_data = get_room(room)
    print(room_data)
    if room_data != None:
        update_room(room, add=-1)
        if room_data['members'] <= 1:
            delete_room(room)
            delete_history(room)
    time = datetime.datetime.now().strftime('%H : %M')
    send({'name': name, 'message': ' has left the room', 'time' : time}, to=room)
    print(f"{name} left the room {room}")

@socketio.on('new_message')
def new_message(data):
    room = session.get('room')
    if not check_room(room):
        return
    time = datetime.datetime.now().strftime('%H : %M')
    content = {
        'name' : session.get('name'), 
        'message' : data['data'],
        'time' : time
    }
    save_content(room, content)
    send(content, to=room)
    print(f"{session.get('name')} said {data['data']}")

@login_manager.user_loader
def load_user(name):
    return get_user(name)

if __name__ == '__main__':
    socketio.run(app, debug=True)