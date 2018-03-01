from flask import Flask, render_template, redirect,url_for, request, session, flash, g, make_response, send_file
from wtforms import Form
import requests
from multiprocessing.pool import ThreadPool


app = Flask(__name__)


@app.route('/')
def login_form():
    return render_template("login.html")


def resultant_data(user_info,username,password):
    def fetch_url(url):
        try:
            response = requests.get(url,auth=(username,password))
            return response, None
        except Exception as e:
            return  None, e
    try:
        user_info_json = user_info.json()
        repos_request = requests.get('https://api.github.com/users/' +user_info_json['login']+ '/repos', auth=(username,password))
        repos_json = repos_request.json()
        repos_list = []
        
        urls_1 = []
        urls_2 = []
        for i in range(len(repos_json)):
            urls_1.append('https://api.github.com/repos/'+user_info_json['login']+'/'+repos_json[i]['name']+'/traffic/clones')
            urls_2.append('https://api.github.com/repos/'+user_info_json['login']+'/'+repos_json[i]['name']+'/traffic/views')
        
        response_clone_list = []
        response_traffic_list = []
        
        raw_results_1 = ThreadPool(30).map(fetch_url, urls_1)
        for response_clone, error in raw_results_1:
            if error is None:
                response_clone_list.append(response_clone.json()['count'])
        raw_results_2 = ThreadPool(30).map(fetch_url, urls_2)
        for response_clone, error in raw_results_2:
            if error is None:
                response_traffic_list.append(response_clone.json()['count'])

        for i in range(len(repos_json)):
            #repos_list contains name of repo,watchers_count,language used,forks_count,clones_count
            repos_list.append([repos_json[i]['name'],repos_json[i]['watchers_count'],repos_json[i]['forks_count'],
                               response_clone_list[i],
                               response_traffic_list[i]])
        keys_for_dict = ['avatar','email','followers','following','name','bio','url','public_repos','repos_list']
        values_for_dict = [user_info_json['avatar_url'],user_info_json['email'],user_info_json['followers'],user_info_json['following'],user_info_json['name'],user_info_json['bio'],user_info_json['url'],user_info_json['public_repos'],repos_list]
        result_dict = dict(zip(keys_for_dict,values_for_dict))
        return result_dict
    except Exception as e:
    	return str(e)





@app.route('/signin/',methods=["GET","POST"])
def login_check():
	error = ''
	if request.method == "POST":
	    attempted_username = request.form['userid']
	    attempted_password = request.form['password']
	    check_user = requests.get('https://api.github.com/user', auth=(attempted_username, attempted_password))
	    if check_user.status_code == 200:
	    	data=resultant_data(check_user,attempted_username, attempted_password)
	    	if type(data)==dict:
	    		return render_template('index.html',data=data)
	    	else:
	    		return render_template('login.html',error=data)
	    else:
	    	return render_template("login.html",error=check_user.json()['message'])

app.run(debug=True)

