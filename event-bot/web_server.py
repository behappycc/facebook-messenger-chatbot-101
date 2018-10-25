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
                elif 'postback' in webhook_event:
                    postback = webhook_event['postback']
                    handle_postback(sender_psid, postback)
            return {'message': 'EVENT_RECEIVED'}, 200
        else:
            return {'message': 'event is not from a page subscription'}, 404


class InitBot(Resource):
    def post(self):
        set_welcome_screen()
        set_persistent_menu()


def call_send_api(sender_psid, response):
    data = {
        "recipient": {"id": sender_psid},
        "message": response
    }

    resp = requests.post(API_URL + API_VERSION +
                         "/me/messages?access_token=" + PAGE_ACCESS_TOKEN, json=data)


def set_welcome_screen():
    data = {
        "get_started": {"payload": "greeting"},
        "greeting": [
            {
            "locale":"default",
            "text":"Hello!" 
            }
        ]
    }
    resp = requests.post(API_URL + API_VERSION +
                         "/me/messenger_profile?access_token=" + PAGE_ACCESS_TOKEN, json=data)
    if resp.status_code > 300:
        logging.error('Unable to set welcome screen :' + resp.text)



def set_persistent_menu():
    data = {
        'persistent_menu': [
            {
                'locale':'default',
                'call_to_actions': [
                    {
                        "title":"Menu",
                        'type': 'postback',
                        'payload': 'menu'
                    },
                    {
                        'title': 'website',
                        'type': 'web_url',
                        'url': 'https://tenlong.kktix.cc/events/facebook-messenger-chatbot-101'
                    }
                ]
            }
        ]
    }
    resp = requests.post(API_URL + API_VERSION +
                         "/me/messenger_profile?access_token=" + PAGE_ACCESS_TOKEN, json=data)
    if resp.status_code > 300:
        logging.error('Unable to set welcome screen :' + resp.text)

def handle_message(sender_psid, received_message):
    if 'text' in received_message:
        response = {
            'text': received_message['text']
        }
    
    call_send_api(sender_psid, response)

    return "ok"

def handle_postback(sender_psid, received_postback):
    payload = received_postback['payload']
    payload_action = False
    if (payload == 'greeting'):
        response = {"text": "Hello!"}
    elif (payload == 'introduction'):
        response = reply_postback_introduction()
    elif (payload == 'agenda'):
        response = reply_postback_agenda()
    elif (payload == 'traffic_information'):
        response = reply_postback_traffic_information()
    elif (payload == 'ticket'):
        response = reply_postback_ticket()
    elif (payload == 'sponsor'):
        response = reply_postback_sponsor()
    elif (payload == 'contact_us'):
        response = reply_postback_contact_us()
    elif (payload == 'menu'):
        response = reply_postback_menu()

    call_send_api(sender_psid, response)

def reply_postback_menu():
    data = {
        "text": "Facebook Messenger 聊天機器人實作班 － 手把手教你用 Python 建立自己的第一個聊天機器人",
        "quick_replies":[
            {
                "content_type":"text",
                "title":"課程介紹",
                "payload":"introduction",
            },
            {
                "content_type":"text",
                "title":"議程",
                "payload":"agenda",
            },
            {
                "content_type":"text",
                "title":"交通資訊",
                "payload":"traffic_information",
            },
            {
                "content_type":"text",
                "title":"購票",
                "payload":"ticket",
            },
            {
                "content_type":"text",
                "title":"贊助商",
                "payload":"sponsor",
            },
            {
                "content_type":"text",
                "title":"聯絡我們",
                "payload":"contact_us",
            },
            {
                "content_type":"text",
                "title":"主選單",
                "payload":"menu",
            }
        ]
    }
    return data

def reply_postback_introduction():
    data = {"text": "Hello!"}
    return data

def reply_postback_agenda():
    data = {"text": "Hello!"}
    return data

def reply_postback_traffic_information():
    data = {}
    return data

def reply_postback_traffic_ticket():
    data = {}
    return data

def reply_postback_traffic_sponsor():
    data = {}
    return data

def reply_postback_traffic_contact_us():
    data = {}
    return data



api.add_resource(Webhook, '/webhook')
api.add_resource(InitBot, '/init-bot')



def main():
    logging.info('Start Event Bot Server')
    parser = argparse.ArgumentParser(description='Event Bot Server')
    parser.add_argument(
        '-p', type=int, help='listening port for Event Bot Server', default=8000)
    args = parser.parse_args()
    port = args.p
    app.run(port=port, debug=True)


if __name__ == "__main__":
    main()
