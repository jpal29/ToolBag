import os, bcrypt


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

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slack_id = db.Column(db.String(255), unique=True, nullable=False)
    real_name = db.Column(db.String(255), nullable=False)

    def __init__(self, slack_id, real_name):
        self.slack_id = slack_id
        self.real_name = real_name

# class User(db.Model):
#     __tablename__ = 'user'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     username = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     first_name = db.Column(db.String(255), nullable=False)
#     last_name = db.Column(db.String(255), nullable=False)
#     time_created = db.Column(db.Time, nullable=False)
#     date_created = db.Column(db.Date, nullable=False)

#     def __init__(self, username, password, first_name, last_name, id=None, time=datetime.datetime.now().time(), date=datetime.datetime.now().date()):
#         self.username = username
#         self.password = bcrypt.generate_password_hash(password)
#         self.first_name = first_name
#         self.last_name = last_name
#         self.id = id
#         self.time_created = time
#         self.date_created = date

#     @staticmethod
#     def validate(username, password):
#         try:
#             authuser = User.query.filter_by(username=username).first()
#             pwauth = bcrypt.check_password_hash(authuser.password, password)
#             if authuser and pwauth:
#                 return {'status': True, 'credentials': authuser.id, 'user': authuser}
#             else:
#                 return {'status': False, 'failed': 'Invalid password.'}
#         except:
#             return {'status': False, 'failed': 'Invalid username.'}

class CampItemNeed(db.Model):
    __tablename__ = 'campitemneed'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_name = db.Column(db.String(255), nullable=False)
    requested_by = db.Column(db.String(255), nullable=False)

    def __init__(self, item_name, requested_by):
        self.item_name = item_name
        self.requested_by = requested_by

class CampItemHave(db.Model):
    __tablename__ = 'campitemhave'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_name = db.Column(db.String(255), nullable=False)
    purchased_by = db.Column(db.String(255), nullable=False)

    def __init__(self, item_name, purchased_by):
        self.item_name = item_name
        self.purchased_by = purchased_by

class SassEntry(db.Model):
    __tablename__ = 'SassEntry'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blurb = db.Column(db.String(255), nullable=False)
    receiver = db.Column(db.String(255), nullable=False)

    def __init__(self, blurb, receiver):
        self.blurb = blurb 
        self.receiver = receiver



