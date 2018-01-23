import os


from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import string
import random

db = SQLAlchemy()

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.String(255))

    def __repr__(self):
        return '<Entry %r>' % self.task
