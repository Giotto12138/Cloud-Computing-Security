from flask import Flask, render_template, jsonify
from google.cloud import datastore


app = Flask(__name__)

DS = datastore.Client()
EVENT = 'Event' # Name of the event table, can be anything you like.
ROOT = DS.key('Entities', 'root') # Name of root key, can be anything.

# main page
@app.route('/')
def index():
    return render_template("index.html")


"""
    post function
    variables: {name} {date_str}, 
    add new event to google cloud datastore
"""
@app.route("/event", methods = ["POST"])
def post_event(name, date_str):
    entity = datastore.Entity(key=DS.key(EVENT, parent=ROOT))
    entity.update({'name': name, 'date': date_str})
    DS.put(entity)
    

"""
    get function
    get all the existing events from google cloud datastore
"""
@app.route("/events", methods = ["GET"])
def get_events():
    
    for event in DS.query(kind = EVENT, ancestor = ROOT).fetch():
        return jsonify({"events":[{"name": event["name"], "date": event["date"], "id": event.id}], "error": "getError"})


if __name__ == '__main__':
    # For local testing
    app.run(host='127.0.0.1', port=8080, debug=True)