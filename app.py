import sqlite3
import re
from flask import Flask, render_template, url_for, g, request

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

@app.route('/', methods=['GET', 'POST'])
def index():
    cs = query_db('select name, number from abbreviations')

    if request.method == "POST":
        query = request.form['bar']

        # Search logic
        """
        The idea is to match to a specific course or a specific department.
        
        If there are no spaces, it's assumed that it's searching a department...
        
        unless it's a series of letters followed by numbers (with optional letters following),
        in which case it's a course.

        If there are two parts, it's assumed to be a course.

        Any other number of separate words trigger a search for all (select * from ___).
        """
        words = query.split()
        match = re.match(r"([a-zA-Z]+)([0-9]+)(a-zA-Z)*", query, re.I)
        if match:
            items = match.groups()
            q = "SELECT name, number FROM abbreviations WHERE name = ? AND number = ?"
            table_courses = query_db(q, (items[0].upper(), items[1]))
        elif len(words) == 1:
            # Gets only for department
            q = "SELECT name, number FROM abbreviations WHERE name = ? ORDER BY number"
            table_courses = query_db(q, (words[0].upper(),))
        elif len(words) == 2:
            q = "SELECT name, number FROM abbreviations WHERE name = ? AND number = ?"
            table_courses = query_db(q, (words[0].upper(), words[1]))
        else:
            table_courses = query_db("SELECT name, number FROM abbreviations")[:50]
    else:
        table_courses = cs[:50]

    return render_template("index.html", courses=cs, table_courses=table_courses)


if __name__ == '__main__':
    app.run()