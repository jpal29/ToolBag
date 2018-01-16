import datetime
import functools
import os
import re
import urllib

from flask import (Flask, abort, flash, Markup, redirect, render_template, request, Response, session, url_for)
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api


from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache

from models import db

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

@app.route('/')
def index():
	return render_template('index.html')

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
