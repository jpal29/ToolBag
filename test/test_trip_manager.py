import os
import sys
import pytest
import tempfile
import TripManager
import json
from dotenv import load_dotenv
from test.util import request_wrapper

"""
Need to import the main file that contains the instance of the flask app that I want to test. 
At least until I restructure this whole project to be more standardized.
"""

from TripManager.main import app
from TripManager.models import db

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

@pytest.fixture
def client():
	db_fd, app.config['DATABASE'] = tempfile.mkstemp()
	app.config['TESTING'] = True
	#Need this otherwise you get an error when running more than one unit test. See https://github.com/ga4gh/ga4gh-server/issues/791 for reference
	app.config['DEBUG'] = False
	client = app.test_client()

	
	db.init_app(app)

	yield client

	os.close(db_fd)
	os.unlink(app.config['DATABASE'])


def test_home_page(client):
	"""Start with a blank database."""

	rv = client.get('/')
	assert b'This is a test page' in rv.data


#Test to make sure that the challenge event on /listening route works

def test_challenge(client):

	mimetype = 'application/json'
	
	headers = {
		'content-type': mimetype,
		'accept': mimetype
	}

	data = {
		"token": os.getenv("VERIFICATION_TOKEN"),
    	"challenge": os.getenv("CHALLENGE_PARAMETER"),
    	"type": "url_verification"
	}

	response = client.post('/listening', data=json.dumps(data), headers=headers)
	assert response.content_type == mimetype
	assert response.status_code == 200




#Test for adding an item to the slackbot via dm
def test_add_item(client):
	add_request = request_wrapper("add foo")

	response = client.post('/listening', data=json.dumps(add_request.data), headers=add_request.headers)
	assert "Items were added" in response.data
	assert response.status_code == 200

def test_remove_item(client):
	remove_request = request_wrapper("remove foo")
	response = client.post('/listening', data=json.dumps(remove_request.data), headers=remove_request.headers)
	assert "Items were removed from list of needed items and added to purchased item list"

def test_list_needed_items(client):
	list_request = request_wrapper("list needed items")

	response = client.post('/listening', data=json.dumps(list_request.data), headers=list_request.headers)
	assert "Listed camping items needed" in response.data
	assert response.status_code == 200

def test_list_purchased_items(client):
	list_request = request_wrapper("list purchased items")

	response = client.post('/listening', data=json.dumps(list_request.data), headers=list_request.headers)
	assert "Listed camping items purchased" in response.data
	assert response.status_code == 200









