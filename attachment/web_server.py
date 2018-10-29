import argparse
import logging

import requests
from flask import Flask, request, Response
from flask_restful import Resource, Api


PAGE_ACCESS_TOKEN = 'EAAWdYsDjndwBAPS99g8M1yU8FXIyUa2qlqDFCjdgNNzgvxyrvMxHJsIy6EeC1ku2Run1ZAZCAvFEonEghRQUKel0CYwBIgaLlbrCP8bHrT4yaXcOdGZA0YD7MOI9HGjb1AURZByVUIgJESZCJKusJUzH9xQGZC7z3dX40zUloI3BB8n7eOrbWd'
API_URL = 'https://graph.facebook.com/'
API_VERSION = 'v3.2'
VERIFY_TOKEN = '12345678'

app = Flask(__name__)
api = Api(app)
logging.basicConfig(level=logging.INFO)

def call_send_api(sender_psid, response):
    data = {
        "messaging_type": "RESPONSE",
        "recipient": {
            "id": sender_psid
        },
        "message": response
    }
    try:
        resp = requests.post(API_URL + API_VERSION +
                         "/me/messages?access_token=" + PAGE_ACCESS_TOKEN, json=data)
    except Exception as e:
        logging.error('Unable to send message:' + e)

class InitBot(Resource):
    def post(self):
        reset_messenger_profile()
        return {"message": "success"}

def reset_messenger_profile():
    data = {
        "fields": [
            "persistent_menu",
            "get_started",
            "greeting"
        ]
    }
    resp = requests.delete(API_URL + API_VERSION +
                         "/me/messenger_profile?access_token=" + PAGE_ACCESS_TOKEN, json=data)
    
    if resp.status_code > 300:
        logging.error('Unable to set welcome screen :' + resp.text)

def handle_message(sender_psid, received_message):
    if 'text' in received_message:
        response = {
            # 'text': received_message['text'],
            'attachment': {
                "type": "image",
                "payload": {
                    "url":"http://i.imgur.com/7SKqWba.jpg", 
                }
            }
        }
    
    call_send_api(sender_psid, response)

    return "ok"


class Webhook(Resource):
    def get(self):
        mode = request.args['hub.mode']
        token = request.args['hub.verify_token']
        challenge = request.args['hub.challenge']
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return Response(response=challenge, status=200)
        else:
            return Response(response='Verification token mismatch', status=403)

    def post(self):
        data = request.get_json(force=True)
        print(data)
        if data['object'] == 'page':
            for entry in data['entry']:
                webhook_event = entry['messaging'][0]
                sender_psid = webhook_event['sender']['id']
                if 'message' in webhook_event:
                    message = webhook_event['message']
                    handle_message(sender_psid, message)
            return {'message': 'EVENT_RECEIVED'}, 200
        else:
            return {'message': 'event is not from a page subscription'}, 404


api.add_resource(Webhook, '/webhook')
api.add_resource(InitBot, '/init-bot')

def main():
    logging.info('Start Messenger Bot Server')
    parser = argparse.ArgumentParser(description='Messenger Bot Server')
    parser.add_argument(
        '-p', type=int, help='listening port for Messenger Bot Server', default=8000)
    args = parser.parse_args()
    port = args.p
    app.run(port=port, debug=True)


if __name__ == "__main__":
    main()
