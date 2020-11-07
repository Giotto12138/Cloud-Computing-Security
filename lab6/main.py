from flask import Flask, render_template, jsonify, request
import os, psycopg2

app = Flask(__name__)
# get helpful environment variables
db = os.getenv('POSTGRES_DATABASE')
host = os.getenv('POSTGRES_HOST')
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')


'''
main page
'''
@app.route('/', defaults={'path': '/'}, methods=['GET'])
#@app.route('/', methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def root(path):
    rows = count_path(path)
    # shows all paths in ascending lexicographical order
    rows.sort()
    
    result = {}
    
    for row in rows:
        result[row[0]] = row[1]
    
    return render_template('index.html', data=result)
    
'''
updates the count i the database for that path, setting it to 1 if it isn't there, and incrementing it
if it is there
'''
def count_path(path):
    
    conn = psycopg2.connect(host=host ,database=db, user=user, password=password, port="5432")
    cur = conn.cursor()
    # update the new path_count into the database
    update = """INSERT INTO pathcount (path, count)
                VALUES (%s, 1)
                ON CONFLICT (path) DO UPDATE
                    SET count = pathcount.count + 1
                RETURNING count;"""
                
    cur.execute(update, (path,))
    conn.commit()
    
    # get the latest path_count from the database
    select = """SELECT path, count FROM pathcount ORDER BY path"""
    
    cur.execute(select)
    rows = cur.fetchall()
    conn.commit()
    
    cur.close()
    
    return rows
    

if __name__ == '__main__':
    # For local testing
    app.run(host='127.0.0.1', port=8080, debug=True)