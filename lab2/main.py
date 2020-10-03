import uuid, time, os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for
from google.cloud import datastore
from flask_login import LoginManager, login_user, current_user, login_required, UserMixin, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from flask_wtf import FlaskForm


# user class
# class User(UserMixin):
#     def __init__(self, user):
#         self.username = user.get("name")
#         self.password_hash = user.get("password")
#         self.id = user.get("id")

#     def verify_password(self, password):
        
#         if self.password_hash is None:
#             return False
        
#         return check_password_hash(self.password_hash, password)

#     def get_id(self):
#         return self.id

#     @staticmethod
#     def get(user_id):
        
#         if not user_id:
#             return None
#         for user in USERS:
#             if user.get('id') == user_id:
#                 return User(user)
            
#         return None

# the class for user login  
class LoginForm(FlaskForm):
    
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

# the class for user registration
class SignupForm(FlaskForm):
    
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', [
        DataRequired(),
        EqualTo('confirm', message='The two passwords are not the same')
    ])
    confirm = PasswordField('confirm the password')


app = Flask(__name__)
# generate a 24 bits random key as a form exchange secret key, preventing CSRF attack
app.secret_key = os.urandom(24) 
# set the duration of session of 1 hour
# app.config['PERMANENT_SESSION_LIFETIME'] = 3600

login_manager = LoginManager()  # initiate login management object
login_manager.init_app(app)  # initiate app
login_manager.login_view = 'login'  # set the page to jump to the login page, when validation fails. 

DS = datastore.Client()
EVENT = 'event' # Name of the event table, can be anything you like.
SESSION = 'session'
USER = 'user'
ROOT = DS.key('Entities', 'root') # Name of root key, can be anything.
EXPIRES_FMT = "%Y%m%d-%H%M%S"   

# main page
@app.route('/')
@login_required
def index():
    
    # current_user is a global varabe provided by flask_login package
    return render_template("index.html")
    #return render_template("index.html", username=current_user.username)

"""
    get function
    get all the existing events from google cloud datastore
"""
@app.route('/events',methods = ["GET"])
@login_required
def getEvents():
    events = DS.query(kind='event', ancestor=ROOT).fetch()
    #TODO: calculate the remaining time on the server side, and return the sorted data based on the remaining time to the browser, so that we could sort events correctly and display them. The browser will also calculate the remaining time every second
    return jsonify({
        'events':sorted([{'name': event['name'], 'date': event['date'], 'id': event.id} for event in events], key=lambda element:(element['date'])), 
        'error': None
    })
    
"""
    post function
    variables: {name} {date}, 
    add new event to google cloud datastore
"""  
@app.route('/event', methods=['POST'])
@login_required
def addEvents():
    event = request.json
    entity = datastore.Entity(key=DS.key('event', parent=ROOT))
    entity.update({
        'name': event['name'],
        'date': event['date']
    })
    DS.put(entity)
    
    return getEvents()

"""
    delete events based on the id of the event in the datastore
"""
# @app.route('/delete', methods=['DELETE'])
# def delEvent():
#     event_id = request.json
#     DS.delete(DS.key(EVENT, event_id["key"], parent=ROOT))
#     return getEvents()
@app.route('/delete/<int:event_id>', methods=['DELETE'])
def delEvent(event_id):
    DS.delete(DS.key(EVENT, event_id, parent=ROOT))
    return getEvents()


'''
The following is the manage user registration and login section.
''' 

# create a user
def create_user(username, password):
    if not username:
        return
    
    user = datastore.Entity(user_key(username))
    user.update({
        'username': username,
        'password': generate_password_hash(password),
        # 'id': uuid.uuid4()  # use uuid to generate an unique id as Primary key
    })
    DS.put(user)


def user_key(user_or_username):
    username = user_or_username
    
    if isinstance(user_or_username, datastore.Entity):
        username = user_or_username.key.name
        
    return DS.key(USER, username, parent=ROOT)


@login_manager.user_loader  # define a method to get logining user
def load_user(user_id):
    return User.get(user_id)


def check_user(username, password):
    user = DS.get(user_key(username))
    
    if user and check_password_hash(user['password'], password):
        return True

    return False


def new_session(username, ttl=None):
    # set the duration of session of 1 hour
    if not ttl:
        ttl = timedelta(hours=1)
    # use uuid to generate an unique id for session
    token = str(uuid.uuid4())
    exp = (datetime.now() + ttl).strftime(EXPIRES_FMT)

    session = datastore.Entity(key=DS.key(SESSION, token, parent=ROOT))
    session.update({
        'username': username,
        'exp': exp,
    })
    # use google datastore to store session for every user
    DS.put(session)

    return token


# login function
@app.route('/login/', methods=('GET', 'POST'))  
def login():
    form = LoginForm()
    emsg = None
    # for post request, judge whether the user submitted the form completely
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        
        if not check_user(user_name, password):
            emsg = "invalid username or password"
        else:
            print("mark***********************")
            # user = User(user_info)  # initiate a user entity
            #login_user(user)  # create a session for the user
            # jump to the main page
            session_token = new_session(user_name)
            resp1 = redirect(url_for('index'))
            resp1.set_cookie('sess', session_token)
            resp2 = redirect(request.args.get('next'))
            resp2.set_cookie('sess', session_token)
            return resp1 or resp2
        
            #return redirect(request.args.get('next') or url_for('index'))
                
    return render_template('login.html', form=form, emsg=emsg)

def migrate(username):
    data = list(DS.query(kind = "event", ancestor=ROOT).fetch())
    user = list(DS.query(kind='user', ancestor=ROOT).fetch())
    userkey = user[0].key
    entity = datastore.Entity(key=DS.key("event"))
    
    for i in range(len(data)):
        data[i]['userkey'] = userkey
        entity.update({'name': data[i]['name'], 'date': data[i]['date'],'id': data[i]['id'], 'userkey': data[i]['userkey']})
        
    DS.put(entity)


# registration function
@app.route('/register/', methods=('GET', 'POST')) 
def register():
    form = SignupForm()
    emsg = None
    # when we click the submit button on the register page, meaning post something
    if form.validate_on_submit():
        
        user_name = form.username.data
        password = form.password.data
        
        # if it is an unused user name, we create a new username
        if not DS.get(user_key(user_name)):
            create_user(user_name, password)  
            session_token = new_session(user_name)
            # jump to the login page
            resp = redirect(url_for('index'))
            resp.set_cookie('sess', session_token)
            # migrate data
            if len(DS.query(kind = USER, ancestor=ROOT).fetch()) <= 1:
                migrate(user_name)
            
            return resp
            #return redirect(url_for("login"))  
        else:
            emsg = "this username already exists"  
    
    return render_template('register.html', form=form, emsg=emsg)


# log out and delete the session
@app.route('/logout')  
@login_required
def logout():
    #logout_user()
    token = request.cookies.get('sess')
    DS.delete(DS.key(SESSION, token, parent=ROOT))
    resp = redirect(url_for("login"))
    resp.delete_cookie('sess')
    return resp
    # return redirect(url_for('login'))


if __name__ == '__main__':
    # For local testing
    app.run(host='127.0.0.1', port=7070, debug=True)