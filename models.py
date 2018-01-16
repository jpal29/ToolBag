import os


from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import string
import random

db = SQLAlchemy()

class Entry(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	title  = db.Column(db.String(255))
	slug = db.Column(db.String(255), unique=True)
	content = db.Column(db.Text)
	published = db.Column(db.Boolean)
	timestamp = db.Column(db.DateTime)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = re.sub('[^\w]+', '-', self.title.lower())
		ret = super(Entry, self).save(*args, **kwargs)

		return ret

	

	


