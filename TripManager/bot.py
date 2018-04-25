# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
import os
import TripManager.message
import MySQLdb
import pprint

from slackclient import SlackClient

from TripManager.models import db, CampItemNeed, CampItemHave, SassEntry

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}

class Bot(object):
    """ Instanciates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "tripmanager"
        self.emoji = ":robot_face:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient(os.environ.get("TRIPMANAGER_OAUTH_TOKEN"))
        # We'll use this dictionary to store the state of each message object.
        # In a production envrionment you'll likely want to store this more
        # persistantly in  a database.
        self.messages = {}

        #Adding the database configuration for diesem bot
        self.db_host = os.environ.get("Personal_Site_DB_Host")
        self.db_user = os.environ.get("Personal_Site_DB_User")
        self.db_password = os.environ.get("Personal_Site_DB_Password")
        self.db_name = os.environ.get("Slack_DB_Name")

    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}
        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def open_dm(self, user_id):
        """
        Open a DM to send a welcome message when a 'team_join' event is
        recieved from Slack.

        Parameters
        ----------
        user_id : str
            id of the Slack user associated with the 'team_join' event

        Returns
        ----------
        dm_id : str
            id of the DM channel opened by this method
        """
        new_dm = self.client.api_call("im.open",
                                      user=user_id)

        print("This is the dm")
        print(new_dm)
        dm_id = new_dm["channel"]["id"]
        return dm_id

    """def open_cm(self, channel_id):
        new_cm = self.client.api_call("im.open",)"""

    def add_camping_item(self, channel_id, user_id, item_request):
        parsed_item_request = ""
        #Need to handle both direct requests and app mention.
        #So if there is an app mention then the request starts with <@APPID>
        #Hence the parsing with ">"
        if ">" in item_request:
            parsed_item_request = item_request.split("> add ")
        else:
            parsed_item_request = item_request.split("add ")
        camping_item = parsed_item_request[1]
        user_info = self.client.api_call("users.info", user=user_id)
        print(user_info)
        user_name = user_info["user"]["profile"]["real_name"]
        new_item = CampItemNeed(camping_item, user_name)
        db.session.add(new_item)
        db.session.commit()

        self.client.api_call("chat.postMessage",
                                channel=channel_id,
                                text="Item added.")

    def remove_camping_item(self, channel_id, user_id, item):
        print("removing item")
        parsed_item = ""

        #Need this if-else in case a user has requested this removal
        if ">" in item:
            parsed_item = item.split("> remove ")
        else:
            parsed_item = item.split("remove ")
        camping_item = parsed_item[1]
        user_info = self.client.api_call("users.info", user=user_id)
        user_name = user_info["user"]["profile"]["real_name"]

        item_remove = CampItemNeed.query.filter_by(item_name=camping_item).all()
        if item_remove:

            CampItemNeed.query.filter_by(item_name=camping_item).delete()

            #Adding the removed item to the list of items we have
            have_item = CampItemHave(camping_item, user_name)
            db.session.add(have_item)
            db.session.commit()

            self.client.api_call("chat.postMessage",
                                    channel=channel_id,
                                    text="Item removed and added to purchased items")
            return
        else:
            self.client.api_call("chat.postMessage",
                                    channel=channel_id,
                                    text="This item isn't needed")
            return


    def list_camping_items_needed(self, channel_id, user_id):
        
        items = CampItemNeed.query.filter().all()

        
        item_string = "" #Just initializing an empty string
        name_string = ""


        for item in items:
            item_string = item_string + item.item_name + "\n"
            name_string = name_string + item.requested_by + "\n"


        attachment = [{
            "fields": [
                {
                    "title": "Item",
                    "value": item_string,
                    "short": True
                },
                {
                    "title": "Requested by",
                    "value": name_string,
                    "short": True
                }
            ]
        }]

        self.client.api_call("chat.postMessage",
                                channel=channel_id,
                                text="Here are the camping items need",
                                attachments=attachment)

    
    def list_camping_items_purchased(self, channel_id, user_id):

        items = CampItemHave.query.filter().all()

        item_string = ""
        name_string = ""
    
        for item in items:
            item_string = item_string + item.item_name + "\n"
            name_string = name_string + item.purchased_by + "\n"


        attachment = [{
            "fields": [
                {
                    "title": "Item",
                    "value": item_string,
                    "short": True
                },
                {
                    "title": "Purchased by",
                    "value": name_string,
                    "short": True
                }
            ]
        }]

        self.client.api_call("chat.postMessage",
                                channel=channel_id,
                                text="Here are the camping items purchased",
                                attachments=attachment)

    def set_sass(self, channel_id, user_id, message):
        #We need to parse the message to get the user(sass victim) and the message.
        #The format of the message should be @TripManager set sass for @Josh Is he even relevant?
        if ('> set sass for ') in message:
            parsed_message = message.split('> set sass for ')
        else:
            parsed_message = message.split('set sass for ')
        re_parsed_message = parsed_message[1].split('> ')
        sass_victim = re_parsed_message[0] + ">"
        sass_content = re_parsed_message[1]

        table_row = SassEntry.query.filter_by(receiver=sass_victim).first()
        #Need to see if the sass victim already has some sass associated with them
        if (table_row is None):
            new_sass = SassEntry(sass_content, sass_victim)
            db.session.add(new_sass)
            db.session.commit()
            self.client.api_call("chat.postMessage",
                                channel=channel_id,
                                text="Sass has been set")
        #If no sass is associated with victim, associate
        else:
            table_row.blurb = sass_content
            db.session.commit()
            self.client.api_call("chat.postMessage",
                                channel=channel_id,
                                text="Sass has been set")

    def sass(self, channel_id, user_id, message):
        if ('> sass ') in message:
            parsed_message = message.split('> sass ')
        else:
            parsed_message = message.split('sass ')
        print(parsed_message)
        sass_victim = parsed_message[1]
        print(sass_victim)
        table_row = SassEntry.query.filter_by(receiver=sass_victim).first()

        if (table_row is None):
            self.client.api_call("chat.postMessage",
                                    channel=channel_id,
                                    text="That user doesn't have any sass set. Try setting sass first.")
        else:
            self.client.api_call("chat.postMessage",
                            channel=channel_id,
                            text=table_row.blurb)

        
        

   


