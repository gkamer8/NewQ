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

        # Turns department synonym into proper department
        # i.e. cs -> COMPSCI or econ -> ECON
        def synonym(dept):
            # Alters query to add synonyms
            # If statements kept in alphabetical order by nickname
            dept = dept.upper()
            if dept == "ANTH":
                return "ANTHRO"
            elif dept == "ASTRO":
                return "ASTRON"
            elif dept == "BIO":
                return "BIOLOGY"
            elif dept == "CS":
                return "COMPSCI"
            elif dept == "EC":
                return "ECON"
            elif dept == "ENGSCI":
                return "ENG-SCI"
            elif dept == "GENED":
                return "GEN-ED"
            elif dept == "GER":
                return "GERMAN"
            elif dept == "HISTLIT":
                return "HIST-LIT"
            elif dept == "KOR":
                return "KOREAN"
            elif dept == "PHYS":
                return "PHYSICS"
            elif dept == "PS":
                return "PHYSCI"
            else:
                return dept
            
        words = query.split()
        match = re.match(r"([a-zA-Z]+)([0-9]+)([a-zA-Z]*)", query, re.I)

        if match:
            items = match.groups()
            q = "SELECT name, number FROM abbreviations WHERE name LIKE ? AND number = ?"
            print(items)
            table_courses = query_db(q, (synonym(items[0]), items[1] + items[2].upper()))
        elif len(words) == 1:
            # Gets only for department
            q = "SELECT name, number FROM abbreviations WHERE name LIKE ? ORDER BY number"
            table_courses = query_db(q, (synonym(words[0]),))
        elif len(words) == 2:
            q = "SELECT name, number FROM abbreviations WHERE name LIKE ? AND number = ?"
            table_courses = query_db(q, (synonym(words[0]), words[1].upper()))
        else:
            table_courses = query_db("SELECT name, number FROM abbreviations")[:50]
    else:
        table_courses = cs[:50]

    return render_template("index.html", courses=cs, table_courses=table_courses)


if __name__ == '__main__':
    app.run()