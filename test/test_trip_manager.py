import os
import sys
import pytest
import tempfile
import TripManager
import json


"""
Need to import the main file that contains the instance of the flask app that I want to test. 
At least until I restructure this whole project to be more standardized.
"""

from TripManager.main import app
from TripManager.models import db

@pytest.fixture
def client():
	db_fd, app.config['DATABASE'] = tempfile.mkstemp()
	app.config['TESTING'] = True
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
		"token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
    	"challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P",
    	"type": "url_verification"
	}

	response = client.post('/listening', data=json.dumps(data), headers=headers)
	assert response.content_type == mimetype
	assert response.status_code == 200


