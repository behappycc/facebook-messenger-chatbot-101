
import argparse
import logging
import requests
from flask import Flask, request, Response
from flask_restful import Resource, Api


ACCESS_TOKEN = 'EAAFXuikn4ZCoBAAwI4w7KeOLcCjT5W6TVCwbnMOfa95imtCY2R7vQVGCZAQnBEHQhJeCn2X3b0EQRVL6yytWBvrfTX52UgitN0dyYnydUuOlkIfaKsMYV8dZBy3H7qqXRpkqZARYkyfmyzcaqgidIsrlTpcvnL6c696LXZAWWYmSKEXpysRn8'
API_URL = 'https://graph.facebook.com/'
API_VERSION = 'v2.6'
VERIFY_TOKEN = '12345678'

app = Flask(__name__)
api = Api(app)


def call_send_api(sender_psid, response):
    data = {
        "recipient": {"id": sender_psid},
        "message": response
    }
    resp = requests.post(API_URL + API_VERSION +
                         "/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)


def handle_postback(sender_psid, received_postback):
    print(sender_psid, received_postback)

    payload = received_postback['payload']
    payload_action = False
    if (payload == 'yes'):
        response = {"text": "Thanks!"}
    elif (payload == 'no'):
        response = {"text": "Oops, try sending another image."}
    elif (payload == 'HELP_PAYLOAD'):
        response = {"text": "Oops, try sending another image."}
        payload_action = 'HELP_PAYLOAD'

    call_send_api(sender_psid, response)


def handle_message(sender_psid, received_message):
    if 'text' in received_message:
        response = {
            'text': 'you sent the message: ${0}, now send me an image!'.format(received_message['text'])
        }
    elif 'attachments' in received_message:
        attachment_url = received_message['attachments'][0]['payload']['url']
        response = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "Is this the right picture?",
                        "subtitle": "Tap a button to answer.",
                        "image_url": attachment_url,
                        "buttons": [
                            {
                                "type": "postback",
                                "title": "Yes!",
                                "payload": "yes"
                            },
                            {
                                "type": "postback",
                                "title": "No!",
                                "payload": "no"
                            }
                        ]
                    }]
                }
            }
        }

    call_send_api(sender_psid, response)

    return "ok"


class Verify(Resource):
    def get(self):
        args = request.args
        if args['hub.mode'] == 'subscribe' and args['hub.challenge']:
            verify_token = args['hub.verify_token']
            if verify_token == VERIFY_TOKEN:
                return Response(response=args['hub.challenge'], status=200, content_type='text/plain')
            else:
                return Response(response='Verification token mismatch', status=403, content_type='text/plain')
        return Response(response='Fail', status=400, content_type='text/plain')

    def post(self):
        data = request.get_json(force=True)
        if data['object'] == 'page':
            for entry in data['entry']:
                messaging = entry['messaging'][0]
                sender = messaging['sender']['id']
                if 'message' in messaging:
                    message = messaging['message']
                    handle_message(sender, message)
                elif 'postback' in messaging:
                    postback = messaging['postback']
                    handle_postback(sender, postback)
        else:
            raise Exception("NotFoundError")


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

    def post(self):
        json_data = request.get_json(force=True)
        print(json_data)
        return json_data


api.add_resource(HelloWorld, '/')
api.add_resource(Verify, '/webhook')


def main():
    parser = argparse.ArgumentParser(description='Messenger Bot Server')
    parser.add_argument(
        '-p', type=int, help='listening port for Messenger Bot Server', default=8000)
    args = parser.parse_args()
    port = args.p
    app.run(port=port, debug=True)


if __name__ == "__main__":
    main()
