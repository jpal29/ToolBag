from flask import (make_response)
from ToolBag.models import db, Entry, User


class EventProcessor:
    
    def __init__(self, event_type, slack_event):
        users = User.query.filter().all()
        self.names = []
        for user in users:
            self.names.append(user.real_name)
        self.response = "Message received, but nothing was done"
        self.user_id = slack_event["event"]["user"]
        self.channel_id = slack_event["event"].get("channel")

        if event_type == "message":
            self.message_content = slack_event["event"]["text"]
        elif event_type == "app_mention":
            self.message_content = slack_event["event"]['text']

    def handle_message(self, pyBot):
        if 'add' in self.message_content:
            pyBot.add_camping_item(self.channel_id, self.user_id, self.message_content)
            self.response = "Items were added"
            return make_response(self.response, 200)

        elif 'remove' in self.message_content:
            pyBot.remove_camping_item(self.channel_id, self.user_id, self.message_content)
            self.response = "Items were removed from list of needed items and added to purchased item list"
            return make_response(self.response, 200)

        elif 'list needed items' in self.message_content:
            pyBot.list_camping_items_needed(self.channel_id, self.user_id)
            self.response = "Listed camping items needed"
            return make_response(self.response, 200)

        elif 'list purchased items' in self.message_content:
            pyBot.list_camping_items_purchased(self.channel_id, self.user_id)
            self.response = "Listed camping items purchased"
            return make_response(self.response, 200)

        elif 'set sass' in self.message_content:
            pyBot.prepare_sass(self.channel_id, self.user_id, self.message_content)
            self.response = "Sass is being set"
            return make_response(self.response, 200)
            
        elif any(name in self.message_content for name in self.names):
            """
            Unfortunately since the any statement returns a bool, we then have to reiterate through the name list,
            see if the name is one that we can sass, and then sass them. 
            """
            for name in self.names:
                if name in self.message_content:
                    user = User.query.filter_by(real_name=name).first()
                    pyBot.sass(self.channel_id, user.slack_id)
                    self.response = "Sass was dispensed"
                    return make_response(self.response, 200)
        else:
            return make_response(self.response,
            200,)