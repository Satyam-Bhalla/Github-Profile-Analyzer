from flask import Flask, render_template, redirect,url_for, request, session, flash, g, make_response, send_file
from wtforms import Form
import requests


app = Flask(__name__)


@app.route('/')
def login_form():
    return render_template("login.html")

@app.route('/signin/',methods=["GET","POST"])
def login_check():
	error = ''
	if request.method == "POST":
	    attempted_username = request.form['userid']
	    attempted_password = request.form['password']
	    check_user = requests.get('https://api.github.com/user', auth=(attempted_username, attempted_password))
	    if check_user.status_code == 200:
	    	return render_template('index.html',user='Welcome ' + check_user.json()['name'])
	    else:
	    	return render_template("login.html",error=check_user.json()['message'])

app.run(debug=True)

