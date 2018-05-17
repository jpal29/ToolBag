import os

class request_wrapper:
	def __init__(self, message_text):
		self.headers = {
			'content-type': 'application/json',
			'accept': 'application/json'
		}

		self.data = {
			"token": os.getenv("VERIFICATION_TOKEN"),
			"event": {
				"channel": os.getenv("TEST_CHANNEL"),
				"type": "message",
				"user": os.getenv("TEST_USER"),
				"text": message_text,
			},
			"type": "event_callback"
		}