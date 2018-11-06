import argparse
import logging

import requests
from flask import Flask, request, Response
from flask_restful import Resource, Api

PAGE_ACCESS_TOKEN = 'EAAWdYsDjndwBAPS99g8M1yU8FXIyUa2qlqDFCjdgNNzgvxyrvMxHJsIy6EeC1ku2Run1ZAZCAvFEonEghRQUKel0CYwBIgaLlbrCP8bHrT4yaXcOdGZA0YD7MOI9HGjb1AURZByVUIgJESZCJKusJUzH9xQGZC7z3dX40zUloI3BB8n7eOrbWd'
API_URL = 'https://graph.facebook.com/'
API_VERSION = 'v3.2'
VERIFY_TOKEN = '12345678'

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
                "text": "多元成家範例" 
            },
            {
                "locale": "en_US",
                "text": "multiple message demo" 
            },
            {
                "locale": "zh_TW",
                "text": "多元訊息範例" 
            },
        ],
        "persistent_menu": [
            {
                'locale': 'default',
                'call_to_actions': [
                    {
                        'title': '範例列表',
                        'type': 'postback',
                        'payload': 'menu'
                    },
                    {
                        'title': '購票',
                        'type': 'web_url',
                        'url': 'https://tenlong.kktix.cc/events/facebook-messenger-chatbot-101'
                    },
                    {
                        "title": "相關連結",
                        "type": "nested",
                        "call_to_actions":[
                            {
                                'title': '松果城市',
                                'type': 'web_url',
                                'url': 'https://www.pycone.com/'
                            },
                            {
                                'title': '天瓏書局',
                                'type': 'web_url',
                                'url': 'https://www.tenlong.com.tw/'
                            }
                        ]
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

quick_replies = [
    {
        "content_type": "text",
        "title": "圖片(image)",
        "image_url": "https://i.imgur.com/Ig9vfRn.jpg",
        "payload": "image",
    },
    {
        "content_type": "text",
        "title": "圖片(image)re",
        "payload": "image_reusable",
    },
    {
        "content_type": "text",
        "title": "按鈕範本(button)",
        "payload": "button",
    },
    {
        "content_type": "text",
        "title": "一般範本(generic)",
        "payload": "generic",
    },
    {
        "content_type": "text",
        "title": "清單範本(list)",
        "payload": "list",
    },
    {
        "content_type": "location"
    },
    {
        "content_type":"user_phone_number"
    },
    {
        "content_type":"user_email"
    }
]

postbacks = {
    "menu": {
        "text": "這是純文字訊息",
        "quick_replies": quick_replies
    },
    "image": {
        "attachment": {
            "type": "image",
            "payload": {
                "url": "https://i.imgur.com/Ig9vfRn.jpg"
            }
        },
        "quick_replies": quick_replies
    },
    "image_reusable": {
        "attachment": {
            "type": "image",
            "payload": {
                "url": "https://i.imgur.com/Ig9vfRn.jpg",
                "is_reusable": True
            }
        },
        "quick_replies": quick_replies
    },
    "button": {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "button",
                "text": "這是按鈕範本的樣子",
                "buttons": [ # 最多三個按鈕
                    {
                        "type": "web_url",
                        "url": "https://tenlong.kktix.cc/events/facebook-messenger-chatbot-101",
                        "title": "Kktix售票",
                    },
                    {
                        "type": "web_url",
                        "url": "https://www.pycone.com/",
                        "title": "松果城市網站",
                        "webview_height_ratio": "full",
                    }, 
                    {
                        "type": "postback",
                        "title": "主選單",
                        "payload": "menu"
                    }
                ]
            }
        },
        "quick_replies": quick_replies
    },
    "generic": {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [ # 陣列裡面最多放十個項目
                    {
                        "title":"Facebook Messenger 聊天機器人實作班",
                        "image_url":"https://i.imgur.com/Ig9vfRn.jpg",
                        "subtitle":"課程將手把手教你使用 Python 建立自己的第一個聊天機器人",
                        "default_action": {
                            "type": "web_url",
                            "url": "https://tenlong.kktix.cc/events/facebook-messenger-chatbot-101",
                        },
                        "buttons": [ # 最多放三個按鈕
                            {
                                "type": "web_url",
                                "url": "https://www.pycone.com/",
                                "title": "松果城市網站",
                            }, 
                            {
                                "type": "postback",
                                "title": "主選單",
                                "payload": "menu"
                            }

                        ]
                    },
                    {
                        "title":"天瓏書局",
                        "image_url":"https://blog.gcp.expert/material/2018/08/%E5%A4%A9%E7%93%8F.png",
                        "subtitle":"最齊全的電腦書專賣店，天瓏提供專業電腦中文書、英文書、簡體書、電子開發板",
                        "default_action": {
                            "type": "web_url",
                            "url": "https://www.tenlong.com.tw/",
                        },
                        "buttons": [
                            {
                                "type": "web_url",
                                "url": "https://www.tenlong.com.tw/",
                                "title": "天瓏書局",
                            }, 
                            {
                                "type": "web_url",
                                "url": "https://www.pycone.com/",
                                "title": "松果城市網站",
                            }, 
                            {
                                "type": "postback",
                                "title": "主選單",
                                "payload": "menu"
                            }
                        ]
                    },
                ]
            }
        },
        "quick_replies": quick_replies
    },
    "list": {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [ # 2-4個項目
                    {
                        "title": "Facebook Messenger 聊天機器人實作班",
                        "subtitle": "課程將手把手教你使用 Python 建立自己的第一個聊天機器人",
                        "image_url": "https://i.imgur.com/Ig9vfRn.jpg",
                        "buttons": [ # 只能有1個項目
                            {
                                "title": "網址",
                                "type": "web_url",
                                "url": "https://tenlong.kktix.cc/events/facebook-messenger-chatbot-101"
                            }
                        ]
                    },
                    {
                        "title": "松果城市",
                        "subtitle": "松果城市為企業轉型的最佳夥伴. 松果城市為企業量身打造全方位的智能系統與人才訓練",
                        "image_url": "https://i.imgur.com/AcipQzu.png",
                        "buttons": [
                            {
                                "title": "網址",
                                "type": "web_url",
                                "url": "https://www.pycone.com/",         
                            }
                        ]
                    },
                    {
                        "title": "天瓏書局",
                        "subtitle": "最齊全的電腦書專賣店，天瓏提供專業電腦中文書、英文書、簡體書、電子開發板",
                        "default_action": {
                            "type": "web_url",
                            "url": "https://www.tenlong.com.tw/",
                        }
                    }
                ],
                "buttons": [
                    {
                        "title": "主選單",
                        "type": "postback",
                        "payload": "menu"
                    }
                ]
            }
        },
        "quick_replies": quick_replies
    },
}

def handle_postback(sender_psid, received_postback):
    payload = received_postback['payload']

    response = postbacks.get(payload, {"text": "你說什麼？"})

    call_send_api(sender_psid, response)


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