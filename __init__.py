from flask import Flask, render_template, redirect,url_for, request, session, flash, g, make_response, send_file
from wtforms import Form
import requests
from multiprocessing.pool import ThreadPool
from copy import deepcopy
from os import urandom


app = Flask(__name__)
app.secret_key = urandom(134)

@app.route('/')
def login_form():
    return render_template("login.html")



@app.route('/design/')
def design_check():
	return render_template('design.html')



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
        response_unique_traffic_list = []
        response_total_traffic_list = []
        
        raw_results_1 = ThreadPool(30).map(fetch_url, urls_1)
        for response_clone, error in raw_results_1:
            if error is None:
                response_clone_list.append(response_clone.json()['count'])
        raw_results_2 = ThreadPool(30).map(fetch_url, urls_2)
        for response_clone, error in raw_results_2:
            if error is None:
                response_unique_traffic_list.append(response_clone.json()['uniques'])
                response_total_traffic_list.append(response_clone.json()['count'])

        for i in range(len(repos_json)):
            #repos_list contains name of repo,watchers_count,language used,forks_count,clones_count
            repos_list.append([repos_json[i]['name'],response_clone_list[i],repos_json[i]['forks_count'],response_unique_traffic_list[i],response_total_traffic_list[i],repos_json[i]['watchers_count']])
        keys_for_dict = ['avatar','email','followers','following','name','username','bio','url','public_repos','repos_list']
        values_for_dict = [user_info_json['avatar_url'],user_info_json['email'],user_info_json['followers'],user_info_json['following'],user_info_json['name'],user_info_json['login'],user_info_json['bio'],user_info_json['url'],user_info_json['public_repos'],repos_list]
        result_dict = dict(zip(keys_for_dict,values_for_dict))
#         graph_dict = deepcopy(result_dict)
        for i in result_dict['repos_list']:
            i.append(i[1]+i[2]+i[3]+i[5])
        result_dict['repos_list'].sort(key=lambda x:x[-1],reverse=True)
        for i in range(len(result_dict['repos_list'])):
            result_dict['repos_list'][i].insert(0,i+1)
#         for i in range(len(result_dict['repos_list'])):
#             if i==5:
#                 break
#             else:
#                 graph_x.append(str(result_dict['repos_list'][i][1]))
#                 graph_y.append(result_dict['repos_list'][i][-1])
        return result_dict
    except Exception as e:
        return str(e)





@app.route('/signin/',methods=["GET","POST"])
def login_check():
    error = ''
    if 'data' in session:
        return render_template('index.html',data=session['data'],graph_x=session['graph_x'],graph_y=session['graph_y'])
    elif request.method == "POST":
	    attempted_username = request.form['userid']
	    attempted_password = request.form['password']
	    check_user = requests.get('https://api.github.com/user', auth=(attempted_username, attempted_password))
	    if check_user.status_code == 200:
	    	data=resultant_data(check_user,attempted_username, attempted_password)
	    	if type(data)==dict:
                    graph_x_list = []
                    graph_y_list = []

                    for i in range(len(data['repos_list'][0:5])):
                        graph_x_list.append(str(data['repos_list'][i][1]))
                        graph_y_list.append(data['repos_list'][i][-1])
                    session['data'] = data
                    session['graph_x'] = graph_x_list
                    session['graph_y'] = graph_y_list
                    if 'data' in session:
                        return render_template('index.html',data=session['data'],graph_x=session['graph_x'],graph_y=session['graph_y'])
	    	else:
                    return render_template('login.html',error=data)
	    else:
	    	return render_template("login.html",error=check_user.json()['message'])
    else:
        return redirect("//")

@app.route('/plot/')
def draw_plot():
    error = ''
    if 'data' in session:
        return render_template("plot.html",graph_x = session['graph_x'],graph_y = session['graph_y'],data=session['data'])
    else:
        return render_template("login.html",error=check_user.json()['message'])

@app.route('/logout/')
def logout():
    error = ''
    if 'data' in session:
        session.pop('data',None)
        session.pop('graph_x',None)
        session.pop('graph_y',None)
        return redirect("//")
    else:
        return render_template("login.html",error=check_user.json()['message'])
 
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

app.run(debug=True)

