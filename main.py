import datetime
import functools
import os
import re
import urllib
from werkzeug.routing import BaseConverter

from flask import (Flask, abort, flash, Markup, redirect, render_template, request, Response, session, url_for)
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api



from models import db, Entry

#from personal_site.models import Entry, db

ADMIN_PASSWORD = 'secret'
APP_DIR = os.path.dirname(os.path.realpath(__file__))



SECRET_KEY = 'supersecret'
SITE_WIDTH = 800



#TBH, I have no idea what these next three lines are doing
app = Flask(__name__)

#Configuring the mysql database
DB_PASSWORD = os.getenv('Personal_Site_DB_Password')
DB_HOST = os.getenv('Personal_Site_DB_Host')
SQLALCHEMY_DATABASE_URI = 'mysql://flaskuser:{}@{}:3306/personal_site_db'.format(DB_PASSWORD, DB_HOST)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db.init_app(app)

#import personal_site.models
#from personal_site.models import Entry

#db.create_all()

class RegexConverter(BaseConverter):
	def __init__(self, url_map, *items):
		super(RegexConverter, self).__init__(url_map)
		self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter


@app.route('/')
def index():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
	    return render_template('index.html')

@app.route('/register', methods=["POST"])
def register():
    if request.method = 

@app.route('/storytime')
def storytime_index():
	return render_template('storytime/index.html')

@app.route('/task', methods=["GET", "POST"])
def home():
    if request.form:
        task = Entry(task=request.form.get("task"))
        db.session.add(task)
        db.session.commit()
    tasks = Entry.query.all()
    return render_template("task/index.html", tasks=tasks)

@app.route('/login', methods=['POST'])
def do_login():
	if request.form['password'] == 'password' and request.form['username'] == 'admin':
		session['logged_in'] = True
	else:
		flash('wrong password!')
	return index()


"""
@app.route('/test')
def test_index():
        return render_template('test/index.html')
"""

@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
	querystring = dict((key, value) for key, value in request_args.items())
	for key in keys_to_remove:
		querystring.pop(key, None)
	querystring.update(new_values)
	return urllib.urlencode(querystring)

@app.errorhandler(404)
def not_found(exc):
	return Response('<h3>Not found</h3'), 404




if __name__=='__main__':
	#db.create_tables([Entry], safe=True)
	app.run(host='0.0.0.0', debug=True)
