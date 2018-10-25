import argparse
import logging

import requests
from flask import Flask, request, Response
from flask_restful import Resource, Api


PAGE_ACCESS_TOKEN = '<PAGE_ACCESS_TOKEN>'
API_URL = 'https://graph.facebook.com/'
API_VERSION = 'v3.2'
VERIFY_TOKEN = '<VERIFY_TOKEN>'

app = Flask(__name__)
api = Api(app)
logging.basicConfig(level=logging.INFO)

def call_send_api(sender_psid, response):
    data = {
        "recipient": {"id": sender_psid},
        "message": response
    }
    try:
        resp = requests.post(API_URL + API_VERSION +
                         "/me/messages?access_token=" + PAGE_ACCESS_TOKEN, json=data)
    except Exception as e:
        logging.error('Unable to send message:' + e)


def handle_message(sender_psid, received_message):
    if 'text' in received_message:
        response = {
            'text': received_message['text']
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
