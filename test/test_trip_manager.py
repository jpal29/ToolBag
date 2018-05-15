import os
import sys
import pytest
import tempfile
import TripManager
import json
from dotenv import load_dotenv

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
	mimetype = 'application/json'
	
	headers = {
		'content-type': mimetype,
		'accept': mimetype
	}

	data = {
		"token": os.getenv("VERIFICATION_TOKEN"),
		"event": {
			"channel": os.getenv("TEST_CHANNEL"),
			"type": "message",
			"user": os.getenv("TEST_USER"),
			"text": "add foo",

		},
		"type": "event_callback"
	}

	response = client.post('/listening', data=json.dumps(data), headers=headers)
	assert "Items were added" in response.data
	assert response.status_code == 200




