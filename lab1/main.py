from flask import Flask, render_template, jsonify, request
from google.cloud import datastore
import time

app = Flask(__name__)

DS = datastore.Client()
EVENT = 'Event' # Name of the event table, can be anything you like.
ROOT = DS.key('Entities', 'root') # Name of root key, can be anything.

# main page
@app.route('/')
def index():
    return render_template("index.html")

"""
    get function
    get all the existing events from google cloud datastore
"""
@app.route('/events',methods = ["GET"])
def getEvents():
    events = DS.query(kind='event', ancestor=ROOT).fetch()
    
    return jsonify({
        'events':sorted([{'name': event['name'], 'date': event['date'], 'id': event.id} for event in events], key=lambda x:(x['name'])), 
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
    delete events based on the key of the event
"""
@app.route('/delete', methods=['DELETE'])
def delEvent():
    event_id = request.json
    print("here----------------------------------", event_id["key"])
    DS.delete(DS.key(EVENT, event_id["key"], parent=ROOT))
    print("here***************************")
    return getEvents()


if __name__ == '__main__':
    # For local testing
    app.run(host='127.0.0.1', port=7070, debug=True)