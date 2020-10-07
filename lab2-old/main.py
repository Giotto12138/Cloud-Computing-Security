from flask import Flask, request, render_template, make_response, flash, redirect, url_for
from google.cloud import datastore
import json, bcrypt
import os
from datetime import datetime, timezone, timedelta
import random
import string

app = Flask(__name__, template_folder='static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' #for flash
# domain = "chen-lab1.ue.r.appspot.com/"

# #old event
DS = datastore.Client()
entity = datastore.Entity(key=DS.key("event"))
entity.update({'name': 'baichen', 'date': '2020-10-09'})
DS.put(entity)
entity.update({'name':'baichen', 'date':'2020-10-09', 'id': entity.id})
DS.put(entity)

def putEvent(name, dates, userkey):
    entity = datastore.Entity(key = DS.key("event"))
    entity.update({'name':name, 'date':dates, 'userkey': userkey})
    DS.put(entity)
    entity.update({'name':name, 'date':dates, 'userkey': userkey, 'id': entity.id})
    DS.put(entity)
    return True
    # return entity.id

def deleteEvent(id, userkey):
    query = DS.query(kind = 'event')
    query.add_filter('id', '=', int(id))
    query.add_filter('userkey', '=', userkey)
    # query.add_filter('date', '=', dates)
    events = list(query.fetch())
    # print(events)
    if len(events) < 1: return 0
    # print(events[0])
    # print(type(events[0].key))
    # print(events[0]['name'])
    DS.delete(events[0].key)
    return 1

#Just a random string
def generate_token(num):
    res = ''.join(random.sample(string.ascii_letters + string.digits, num))
    return res

def userKey(token):
    query = DS.query(kind = "session")
    query.add_filter('token', '=', token)
    result = list(query.fetch())
    if len(result) != 0:
        return result[0]['userkey']

def migrate(username):
    query_old = DS.query(kind = "event")
    result_old = list(query_old.fetch())

    query_user = DS.query(kind='user')
    query_user.add_filter('username', '=', username)
    result_user = list(query_user.fetch())
    userkey = result_user[0].key

    entity = datastore.Entity(key=DS.key("event"))
    for i in range(len(result_old)):
        result_old[i]['userkey'] = userkey
        entity.update({'name': result_old[i]['name'], 'date': result_old[i]['date'],'id': result_old[i]['id'], 'userkey': result_old[i]['userkey']})
    DS.put(entity)
    return True


@app.route('/events')
def sendEvents():
    query = DS.query(kind = 'event')
    # print("cookie send event")
    # print(request.cookies.get('cookie_t'))
    userkey = userKey(request.cookies.get('cookie_t'))
    #print(userkey)
    query.add_filter('userkey', '=', userkey)
    events = list(query.fetch())
    for i in range(len(events)):
        del events[i]['userkey']
    # print("event")
    # print(events)
    t = json.dumps(events)
    t = '{"events":' + t + '}'
    return t

@app.route('/event', methods = ['POST'])
def PEvent():
    t = json.loads(request.json)
    userkey = userKey(request.cookies.get('cookie_t'))
    #print(userkey)
    putEvent(t['name'].strip(), t['date'].strip(), userkey)
    return 'OK'

@app.route('/event/<id>', methods = ['POST'])
def dEvent(id):
    userkey = userKey(request.cookies.get('cookie_t'))
    deleteEvent(id, userkey)
    return 'Successfully Deleted'

@app.route('/index')
def root():
    return render_template('index.html')

@app.route('/')
def load():
    token = request.cookies.get('cookie_t')
    if token == None: # No cookies
        return render_template('login.html')
    else: # cookies are there
        token = request.cookies.get('cookie_t')
        userkey = userKey(token)
        query = DS.query(kind = "session")
        query.add_filter('token', '=', token)
        query.add_filter('userkey', '=', userkey)
        results = list(query.fetch())
        #print(results)
        if len(results) == 0: # No required cookies
            return render_template('login.html')
        else: # have required cookies
            if results[0]['expire'] > datetime.now(timezone.utc): # cookies not expire
                return render_template('index.html')
            else: # cookies expire
                new_query = DS.query(kind = "session")
                new_query.add_filter('userkey', '=', userkey)
                new_results = list(query.fetch())
                for nr in new_results:
                    DS.delete(nr.key)
                res = make_response(render_template("login.html"))
                res.set_cookie("cookie_t", value=" ")
                # res.set_cookie("cookie_t", value=" ", domain = domain, secure = True)# the cookie will only be avaliable via HTTPS
                return res


@app.route('/reg')
def reg():
    return render_template('register.html')

@app.route('/register', methods = ['POST'])
def register():
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    query = DS.query(kind='user')
    query.add_filter('username', '=', username)
    account = list(query.fetch())
    if len(account) == 1: #need add an alert
        flash("Duplicate username. Please input a new one.")
        return redirect(url_for('reg'))
    entity = datastore.Entity(key = DS.key('user'))
    passwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    entity.update({'username': username, 'password': passwd})
    DS.put(entity)
    query_new = DS.query(kind = 'user')
    #for migrate
    judge_one = list(query_new.fetch())
    if len(judge_one) == 1:
        migrate(username)
    return redirect(url_for('login'))

@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    query = DS.query(kind = 'user')

    query.add_filter('username', '=', username)
    result = list(query.fetch())
    if len(result) == 0:
        flash("No such user. Please input again")
        return render_template('login.html')
    user_username = result[0]['username']
    user_password = result[0]['password']
    user_key = result[0].key
    if isinstance(password, str):
        password = password.encode()
    if isinstance(user_password, str):
        user_password = user_password.encode()
    if username == user_username and bcrypt.hashpw(password, user_password) == user_password:
        token = generate_token(10)
        # print("token")
        # print(token)
        expire = datetime.utcnow() + timedelta(hours = 1)
        entity = datastore.Entity(key = DS.key("session"))
        entity.update({'token':token, 'expire':expire, 'userkey':user_key})
        DS.put(entity)
        # res = make_response(render_template('index.html'))
        res = make_response(redirect('/index'))
        res.set_cookie("cookie_t", value = token, max_age = 3600) #the cookie will only be avaliable via HTTPS by using secure = True
        return res
    else:
        flash("Wrong password")
        return render_template("login.html", error ="invalid information")#need add an alert

@app.route('/logout')
def logout():
    query = DS.query(kind = "session")
    token = request.cookies.get('cookie_t')
    userkey = userKey(token)
    query.add_filter('userkey', '=', userkey)
    #one user can log in the website multiple times in one hour,
    #it can create different result with different token and same userkey.
    results = list(query.fetch())
    for result in results:
        DS.delete(result.key)
    # return render_template('login.html')
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6060, debug=True)
