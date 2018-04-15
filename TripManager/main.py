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

ADMIN_PASSWORD = 'secret'
#APP_DIR = os.path.dirname(os.path.realpath(__file__))



SECRET_KEY = 'supersecret'
SITE_WIDTH = 800




app = Flask(__name__)
pyBot = Bot()
slack = pyBot.client
#Configuring the mysql database
DB_PASSWORD = os.getenv('Personal_Site_DB_Password')
DB_HOST = os.getenv('Personal_Site_DB_Host')
SQLALCHEMY_DATABASE_URI = 'mysql://flaskuser:{}@{}:3306/personal_site_db'.format(DB_PASSWORD, DB_HOST)
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

def _event_router(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.

    Parameters
    ----------
    event_type : str
    type of event recieved from Slack
    slack_event : dict
    JSON response from a Slack reaction event

    Returns
    ----------
    obj
    Response object with 200 - ok or 500 - No Event Handler error

    """
    team_id = slack_event["team_id"]
    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    if event_type == "team_join":
        user_id = slack_event["event"]["user"]
    # Send the onboarding message
        pyBot.onboarding_message(team_id, user_id)
        return make_response("Welcome Message Sent", 200,)

    # ============== Share Message Events ============= #
    # If the user has shared the onboarding message, the event type will be
    # message. We'll also need to check that this is a message that has been
    # shared by looking into the attachments for "is_shared".
    # Need to make sure that type of message is not a bot_message which is handled by the 'subtype'
    # boolean. Not handling this leads to an infinite post of messages until the bot is killed.
    elif event_type == "message" and 'subtype' not in slack_event['event']: 
        response = "Message received, but nothing was done"
        user_id = slack_event["event"]["user"]
        channel_id = slack_event["event"].get("channel")
        message_content = slack_event["event"]['text'].lower()

        names = ['andrew', 'alex', 'nick', 'brendan', 'millian']

        if 'add' in message_content:
            pyBot.add_camping_item(channel_id, user_id, message_content)
            response = "Items were added"
            print(response)
            return make_response(response, 200)
        elif 'remove' in message_content:
            print('received remove request')
            pyBot.remove_camping_item(channel_id, user_id, message_content)
            response = "Items were removed from list of needed items and added to purchased item list"
            return make_response(response, 200)
        elif 'list needed items' in message_content:
            pyBot.list_camping_items_needed(channel_id, user_id)
            return make_response("Listed camping items needed", 200)
        elif 'list purchased items' in message_content:
            pyBot.list_camping_items_purchased(channel_id, user_id)
            return make_response("Listed camping items purchased", 200)

        elif any(name in message_content for name in names):
            """
            Unfortunately since the any statement returns a bool, we then have to reiterate through the name list,
            see if the name is one that we can sass, and then sass them. 
            """
            for name in names:
                if name in message_content:
                    pyBot.sass(channel_id, user_id, name)
                    response = "Sass was dispensed"
                    return make_response(response, 200)
        else:
            return make_response(response,
            200,)

    elif event_type == "app_mention" and 'subtype' not in slack_event['event']:
        response = "Message received, but nothing was done"
        user_id = slack_event["event"]["user"]
        channel_id = slack_event["event"].get("channel")
        message_content = slack_event["event"]['text']

        names = ['andrew', 'alex', 'nick', 'brendan', 'bitch']

        if 'add' in message_content:
            pyBot.add_camping_item(channel_id, user_id, message_content)
            response = "Items were added"
            print(response)
            return make_response(response, 200)
        elif 'remove' in message_content:
            print('received remove request')
            pyBot.remove_camping_item(channel_id, user_id, message_content)
            response = "Items were removed from list of needed items and added to purchased item list"
            return make_response(response, 200)
        elif 'list needed items' in message_content:
            pyBot.list_camping_items_needed(channel_id, user_id)
            return make_response("Listed camping items needed", 200)
        elif 'list purchased items' in message_content:
            pyBot.list_camping_items_purchased(channel_id, user_id)
            return make_response("Listed camping items purchased", 200)
        elif any(name in message_content for name in names):
            for name in names:
                if name in message_content:
                    pyBot.sass(channel_id, user_id, name)
                    response = "Sass was dispensed"
                    return make_response(response, 200)
        else:
            return make_response(response,
        200,)

    else:   
    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
        message = "You have not added an event handler for the %s" % event_type
        # Return a helpful error message
        return make_response(message, 200, {"X-Slack-No-Retry": 1})

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
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        print(event_type)
        # Then handle the event by event_type and have your bot respond
        return _event_router(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
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
