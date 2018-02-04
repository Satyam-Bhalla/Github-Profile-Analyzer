##Flask day udemy program 1
from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def login():
    return render_template("login.html")

app.run(debug=True)
