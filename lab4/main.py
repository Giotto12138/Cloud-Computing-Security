from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World"

if __name__ == '__main__':
    # For local testing
    app.run(host='127.0.0.1', port=7070, debug=True)