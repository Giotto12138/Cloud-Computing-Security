import uuid, time, os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from google.cloud import datastore
from flask_login import LoginManager, login_user, current_user, login_required, UserMixin, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from flask_wtf import FlaskForm

# user class
class User(UserMixin):
    def __init__(self, user):
        self.username = user.get("name")
        self.password_hash = user.get("password")
        self.id = user.get("id")

    def verify_password(self, password):
        
        if self.password_hash is None:
            return False
        
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id

    @staticmethod
    def get(user_id):
        
        if not user_id:
            return None
        for user in USERS:
            if user.get('id') == user_id:
                return User(user)
            
        return None

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

app.secret_key = os.urandom(24) # generate a 24 bits random key as a form exchange secret key, preventing CSRF attack

login_manager = LoginManager()  # initiate login management object
login_manager.init_app(app)  # initiate app
login_manager.login_view = 'login'  # set the page to jump to when validation fails. the login page

USERS = [{
        "id": 1,
        "name": 'giotto',
        "password": generate_password_hash('123')
    }] # stores every registered user, giotto is an intiate user for testing

DS = datastore.Client()
EVENT = 'event' # Name of the event table, can be anything you like.
ROOT = DS.key('Entities', 'root') # Name of root key, can be anything.

# main page
@app.route('/')
@login_required
def index():
    # current_user is a global varabe provided by flask_login package
    return render_template("index.html", username=current_user.username)

"""
    get function
    get all the existing events from google cloud datastore
"""
@app.route('/events',methods = ["GET"])
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

# create a user, will be replaced by register function
def create_user(user_name, password):
    
    user = {
        "name": user_name,
        "password": generate_password_hash(password),
        "id": uuid.uuid4()  # use uuid to generate an unique id as Primary key
    }
    USERS.append(user)
    

# get user information according to the user_name
def get_user(user_name):
    
    for user in USERS:
        if user.get("name") == user_name:
            return user
        
    return None


@login_manager.user_loader  # define a method to get logining user
def load_user(user_id):
    return User.get(user_id)

# login function
@app.route('/login/', methods=('GET', 'POST'))  
def login():
    form = LoginForm()
    emsg = None
    # for post request, judge whether the user submitted the form completely
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_info = get_user(user_name)  # try to find this user from stored users
        
        if user_info is None:
            emsg = "invalid username or password"
        else:
            user = User(user_info)  # initiate a user entity
            if user.verify_password(password):  # check the password
                login_user(user)  # create a session for the user
                # jump to the main page
                return redirect(request.args.get('next') or url_for('index'))
            else:
                emsg = "invalid username or password"
                
    return render_template('login.html', form=form, emsg=emsg)

# registration function
@app.route('/register/', methods=('GET', 'POST')) 
def register():
    form = SignupForm()
    emsg = None
    
    if form.validate_on_submit():
        
        user_name = form.username.data
        password = form.password.data
        # get user information for this user
        user_info = get_user(user_name) 
        # if it is an unused user name, we create a new username
        if user_info is None:
            create_user(user_name, password)  
            # jump to the login page
            return redirect(url_for("login"))  
        else:
            emsg = "this username already exists"  
            
    return render_template('register.html', form=form, emsg=emsg)


# log out and delete the session
@app.route('/logout')  
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    # For local testing
    app.run(host='127.0.0.1', port=7070, debug=True)