import datetime
import functools
import os
import re
import urllib
#import TripManager.bot
import json
import pprint
from werkzeug.routing import BaseConverter

from flask import (Flask, abort, flash, Markup, redirect, render_template, request, Response, session, url_for, make_response)
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_script import Manager 
from flask_migrate import Migrate, MigrateCommand 
from TripManager.models import db, Entry
from TripManager.bot import Bot
from TripManager.event_processor import EventProcessor

ADMIN_PASSWORD = 'secret'



SECRET_KEY = 'supersecret'
SITE_WIDTH = 800




app = Flask(__name__)
pyBot = Bot()
slack = pyBot.client
#Configuring the mysql database
DB_PASSWORD = os.getenv('Personal_Site_DB_Password')
DB_HOST = os.getenv('Personal_Site_DB_Host')
SQLALCHEMY_DATABASE_URI = 'mysql://flaskuser:{}@{}:3306/slackdb'.format(DB_PASSWORD, DB_HOST)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

import TripManager.views


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

        app.url_map.converters['regex'] = RegexConverter


@app.route("/install", methods=["GET"])
def pre_install():
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    return render_template("install.html", client_id=client_id, scope=scope)

@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    code_arg = request.args.get('code')
    pyBot.auth(code_arg)
    return render_template("thanks.html")

@app.route("/command", methods=["POST"])
def command():
    return make_response("NGROK tunnel is working", 200)

@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    print("Received the slack event")
    slack_event = json.loads(request.data.decode('utf-8'))
    pprint.pprint(slack_event)
    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                             "application/json"
                             })

# ============ Slack Token Verification =========== #
# We can verify the request is coming from Slack by checking that the
# verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        print("You got the wrong one Buzzo")
        message = "Invalid Slack verification token: %s \npyBot has: \
            %s\n\n" % (slack_event["token"], pyBot.verification)
    # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
    # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

# ====== Process Incoming Events from Slack ======= #
# If the incoming request is an Event we've subcribed to
    if "event" in slack_event and 'subtype' not in slack_event['event']:
        event_type = slack_event["event"]["type"]
        NewEvent = EventProcessor(event_type, slack_event)

        if event_type=="message" or event_type=="app_mention":
            return NewEvent.handle_message(pyBot)
        else:   
        # ============= Event Type Not Found! ============= #
            # If the event_type does not have a handler
            message = "You have not added an event handler for the %s" % event_type
            # Return a helpful error message
            return make_response(message, 200, {"X-Slack-No-Retry": 1})

    # If our bot hears things that are not events we've subscribed to
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
    you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route('/')
def index():
    return render_template('test/index.html')


@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
        querystring.update(new_values)
    return urllib.urlencode(querystring)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3'), 404




if __name__=='__main__':
    manager.run()
