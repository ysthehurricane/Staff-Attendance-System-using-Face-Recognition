from flask import Flask, render_template, request, url_for
from database import DatabaseOp as db

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c776df@e4h&9dd$q'

@app.route('/', methods=["GET","POST"])
def index():
    d = db()
    records = d.dbfetchall('facultyinfo')
    print(records)
    return render_template('dashboard.html')

@app.route('/register', methods=["GET","POST"])
def register():
    return render_template('register.html')
