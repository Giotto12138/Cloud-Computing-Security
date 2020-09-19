from flask import Flask, render_template
from google.cloud import datastore


app = Flask(__name__)

DS = datastore.Client()
EVENT = 'Event' # Name of the event table, can be anything you like.
ROOT = DS.key('Entities', 'root') # Name of root key, can be anything.

# get function
@app.route('/')
def index():
    return render_template("index.html")

"""
    post function
    variables: {name} {date_str}, 
    add to google cloud datastore
"""
@app.route('/')
def put_event(name, date_str):
    entity = datastore.Entity(key=DS.key(EVENT, parent=ROOT))
    entity.update({'name': name, 'date': date_str})
    DS.put(entity)




if __name__ == '__main__':
    # For local testing
    app.run(host='127.0.0.1', port=8080, debug=True)