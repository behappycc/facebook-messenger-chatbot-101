import argparse
import logging

import requests
from flask import Flask, request, Response
from flask_restful import Resource, Api

PAGE_ACCESS_TOKEN = '<PAGE_ACCESS_TOKEN>'
API_URL = 'https://graph.facebook.com/'
API_VERSION = 'v3.2'
VERIFY_TOKEN = '<VERIFY_TOKEN>'

def main():
    app = Flask(__name__)
    api = Api(app)
    logging.basicConfig(level=logging.DEBUG)

    api.add_resource(Webhook, '/webhook')
    api.add_resource(InitBot, '/init-bot')

    logging.info('Start Messenger Bot Server')
    parser = argparse.ArgumentParser(description='Messenger Bot Server')
    parser.add_argument(
        '-p', type=int, help='listening port for Messenger Bot Server', default=8000)
    args = parser.parse_args()
    port = args.p
    app.run(port=port, debug=True)

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
        logging.info(data)
        if data['object'] == 'page':
            for entry in data['entry']:
                webhook_event = entry['messaging'][0]
                sender_psid = webhook_event['sender']['id']
                if 'message' in webhook_event:
                    if 'quick_reply' in webhook_event['message']:
                        if 'payload' in webhook_event['message']['quick_reply']:
                            postback = webhook_event['message']['quick_reply']
                            handle_postback(sender_psid, postback)
                    else:
                        message = webhook_event['message']
                        handle_message(sender_psid, message)
                elif 'postback' in webhook_event:
                    postback = webhook_event['postback']
                    handle_postback(sender_psid, postback)
            return {'message': 'EVENT_RECEIVED'}, 200
        else:
            return {'message': 'event is not from a page subscription'}, 404

class InitBot(Resource):
    def post(self):
        reset_messenger_profile()
        set_messenger_profile()
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

def set_messenger_profile():
    data = {
        "get_started": {"payload": "menu"},
        "greeting": [
            {
                "locale": "default",
                "text": "Hello" 
            }
        ]
    }
    resp = requests.post(API_URL + API_VERSION +
                         "/me/messenger_profile?access_token=" + PAGE_ACCESS_TOKEN, json=data)
    
    if resp.status_code > 300:
        logging.error('Unable to set welcome screen :' + resp.text)

def handle_message(sender_psid, received_message):
    text = received_message.get('text')
    
    test_case = ["url", "菜單", "菜单", "menu", "help", "幫助", "帮帮我"]
    
    if text in test_case: 
        response = {
            'text': "Hello, Welcome to our page"
        }
    
        call_send_api(sender_psid, response)

    return "ok"

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

if __name__ == "__main__":
    main()