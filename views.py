from flask import Blueprint
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
import random
from string import ascii_uppercase
from flask_login import login_user, logout_user, current_user, login_required
from database import get_user, save_user, add_room, check_room, get_history, get_room
import pymongo.errors

view = Blueprint('views', __name__)

def generate_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        return code

@view.route('/', methods=['GET', 'POST'])
@view.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        if not name:
            error = 'Enter username'
            return render_template('login.html', error=error)        
        
        user = get_user(name)

        if user and user.verify_password(password):
            login_user(user)

            session['name'] = name
            return redirect(url_for('views.home'))

        else:
            error = 'Login Failed'
            return render_template('login.html', error=error, name=name)

    return render_template('login.html')

@view.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    name = session.get('name')

    if request.method == 'POST':
        join = request.form.get('join', default=False)
        create = request.form.get('create', default=False)
        code = request.form.get('code')

        if join != False:
            if not code:
                error = 'Enter code'
                return render_template('home.html', error=error, name=name, code=code)
            
            if check_room(code):
                room = code
            else:
                error = 'Room does not exist'
                return render_template('home.html', name=name, error=error)
            
        if create != False:
            room = generate_code(4)
            try:
                add_room(code=room, members=0)
            except pymongo.errors.DuplicateKeyError:
                room += '1'
                add_room(code=room, members=0)
        session['room'] = room

        return redirect(url_for('views.room', code=room))
    return render_template('home.html', name=name)

@view.route('/room/<code>/', methods=['GET', 'POST'])
@login_required
def room(code):
    name = session.get('name')
    code = session.get('room')
    room_info = get_room(code)
    if room_info:
        members = room_info['members']
    if not check_room(code):
        return redirect(url_for('views.home'))
    messages = get_history(code)
    return render_template('room.html', name=name, code=code, members=members, messages=messages)

@view.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('views.login'))

@view.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        new_name = request.form.get('new-name')
        new_password = request.form.get('new-password')
        if new_password == '':
            error = 'Please enter a password'
            return render_template('signup.html', error=error, new_name=new_name)
        try:
            save_user(new_name, new_password)
        except pymongo.errors.DuplicateKeyError:
            error = 'Username already exists'
            return render_template('signup.html', error=error)
        
        return redirect(url_for('views.login'))
    
    return render_template('signup.html')
