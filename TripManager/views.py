from TripManager.main import app
from TripManager.models import db

@app.route('/testing_new_structure')
def testing_new_structure():
	return 'The structure seems to work'