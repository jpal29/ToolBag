import os
import sys
import pytest
import tempfile
import TripManager


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


def test_empty_db(client):
	"""Start with a blank database."""

	rv = client.get('/')
	assert b'This is a test page' in rv.data


