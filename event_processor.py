class EventProcessor(object):
    """ Instanciates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()

    def handle(self, slack_event)
        self.user_id = slack_event["event"]["user"]
        self.channel_id = slack_event["event"].get("channel")
        self.message_content = slack_event["event"]['text']

        names = ['andrew', 'alex', 'nick', 'brendan', 'bitch']

        if 'add' in message_content:
            pyBot.add_camping_item(channel_id, user_id, message_content)
            global response 
            response = "Items were added"
            print(response)
        elif 'list' in message_content:
            pyBot.list_camping_items(channel_id, user_id)
        elif any(name in message_content for name in names):
            for name in names:
                if name in message_content:
                    pyBot.sass(channel_id, user_id, name)
            global response
            response = "Sass was dispensed"