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
        set_welcome_screen()
        set_persistent_menu()
        return {"message": "success"}


def call_send_api(sender_psid, response):
    data = {
        "recipient": {"id": sender_psid},
        "message": response
    }

    resp = requests.post(API_URL + API_VERSION +
                         "/me/messages?access_token=" + PAGE_ACCESS_TOKEN, json=data)
    print(resp.text)


def set_welcome_screen():
    data = {
        "whitelisted_domains": [
            "https://behappycc.github.io/"
        ],
        "get_started": {"payload": "greeting"},
        "greeting": [
            {
                "locale": "default",
                "text": "Facebook Messenger Chatbot Workshop" 
            },
            {
                "locale": "zh_TW",
                "text": "Facebook Messenger 聊天機器人實作班" 
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
                        "title":"主選單",
                        'type': 'postback',
                        'payload': 'menu'
                    },
                    {
                        'title': '購票',
                        'type': 'web_url',
                        'url': 'https://tenlong.kktix.cc/events/facebook-messenger-chatbot-101'
                    },
                    {
                        'title': '松果城市',
                        'type': 'web_url',
                        'url': 'https://www.pycone.com/'
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
    if (payload == 'greeting'):
        response = reply_postback_greeting()
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

def reply_postback_greeting():
    data = {
        "text": "Facebook Messenger 聊天機器人實作班 － 手把手教你用 Python 建立自己的第一個聊天機器人"
    }
    return data

def reply_postback_menu():
    data = {
        "text": "主選單",
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
    data = {"text": "Facebook Messenger 聊天機器人實作班－手把手教你用 Python 建立自己的第一個聊天機器人\n 上完課後你可以學到從規劃到實作，建置專屬的聊天機器人"}
    return data

def reply_postback_agenda():
    data = {
        "attachment": {
            "payload": {
                "elements": [
                {
                    "image_url": "https://images.unsplash.com/photo-1527430253228-e93688616381",
                    "subtitle": "講解實作聊天機器的底層概念－Webhook、還有底層技術－Web Server、Facebook 應用程式設定和開發者工具等等，讓你打穩Messenger聊天機器人的基礎。\n 時間: 9:30-12:30",
                    "title": "聊天機器人基石"
                },
                {
                    "image_url": "https://images.unsplash.com/photo-1533915828531-55b274d98dc5",
                    "subtitle": "告訴你如何發送精美的範本訊息，以及像是群體推播、貼文留言回覆等進階功能，各種聊天機器人的運用實例，透過豐富範例教你打造聊天機器人。\n 時間: 13:30-16:30",
                    "title": "聊天機器人技法"
                }
                ],
                "template_type": "generic"
            },
            "type": "template"
        }
    }
    return data

def reply_postback_traffic_information():
    data = {
        "attachment": {
            "payload": {
                "buttons": [
                {
                    "messenger_extensions": "true",
                    "title": "Maps",
                    "type": "web_url",
                    "url": "https://behappycc.github.io/pugbot/tenlong-map.html",
                    "webview_height_ratio": "tall"
                }
                ],
                "template_type": "button",
                "text": "天瓏資訊圖書 Coding Space 台北市重慶南路一段105號2F \n 捷運台大醫院2號出口，步行五分鐘"
            },
            "type": "template"
        }
    }
    return data

def reply_postback_ticket():
    data = {
        "attachment": {
            "payload": {
                "elements": [
                {
                    "buttons": [
                    {
                        "title": "前往",
                        "type": "web_url",
                        "url": "https://tenlong.kktix.cc/events/facebook-messenger-chatbot-101"
                    }
                    ],
                    "image_url": "https://t.kfs.io/upload_images/87747/20181009-_________big_large.jpg",
                    "subtitle": "早鳥優惠價 1,800元",
                    "title": "Facebook Messenger 聊天機器人實作班"
                }
                ],
                "template_type": "generic"
            },
            "type": "template"
        }
    }
    return data

def reply_postback_sponsor():
    data = {
        "attachment": {
            "payload": {
                "elements": [
                {
                    "buttons": [
                    {
                        "title": "前往",
                        "type": "web_url",
                        "url": "https://www.tenlong.com.tw/"
                    }
                    ],
                    "image_url": "https://modernweb.tw/img/logo-ten.jpg",
                    "title": "特別感謝-天瓏資訊圖書"
                }
                ],
                "template_type": "generic"
            },
            "type": "template"
        }
    }
    return data

def reply_postback_contact_us():
    data = {
              "text": "信箱：steven@tenlong.com.tw"
    }

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
