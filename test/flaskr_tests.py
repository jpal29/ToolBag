import os
import sys
import unittest
import tempfile

sys.path.append('/home/josh/development/TripManager')
"""
Need to import the main file that contains the instance of the flask app that I want to test. 
At least until I restructure this whole project to be more standardized.
"""
from main import app
from models import db

class FlaskrTestCase(unittest.TestCase):

	def setUp(self):
		self.db_fd, app.config['SQLALCHEMY_DATABASE_URI'] = tempfile.mkstemp()
		app.testing = True
		self.app = app.test_client()
		with app.app_context():
			db.init_app(app)

	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(app.config['SQLALCHEMY_DATABASE_URI'])

	def test_empty_db(self):
		rv = self.app.get('/')
		assert b'<h1>This is a test page</h1>' in rv.data

	def test_command_get(self):
		rv = self.app.get('/command')
		print(rv.data)

if __name__=='__main__':
	unittest.main()