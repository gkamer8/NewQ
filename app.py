import sqlite3
from flask import Flask, render_template, url_for, g

app = Flask(__name__)

DATABASE = 'database.db'

# get_db, close_connection, and query_db come from https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    courses = query_db('select * from courses')
    return render_template("index.html", courses=courses)


if __name__ == '__main__':
    app.run()