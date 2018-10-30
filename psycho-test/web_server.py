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


class InitBot(Resource):
    def post(self):
        set_welcome_screen()
        set_persistent_menu()
        return {"message": "success"}


def call_send_api(sender_psid, response):
    data = {
        "messaging_type": "RESPONSE",
        "recipient": {
            "id": sender_psid
        },
        "message": response
    }

    resp = requests.post(API_URL + API_VERSION +
                         "/me/messages?access_token=" + PAGE_ACCESS_TOKEN, json=data)
    print(resp.text)


def set_welcome_screen():
    data = {
        "get_started": {"payload": "question_1"},
        "greeting": [
            {
            "locale":"default",
            "text":"Facebook Messenger 聊天機器人實作班" 
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
                        "title": "開始測驗",
                        'type': 'postback',
                        'payload': 'question_1'
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

question = {
    "1": {
        "title": "你是否還在愛情的世界外面觀望呢？憧憬幸福的你，下半年收穫愛情的機率有多大呢？快來測下吧！\n\nQ1. 下面兩種味道的香皂你更喜歡哪個？",
        "option": [
            {
                "text": "水果",
                "postback": "question_2",
            },
            {
                "text": "花香",
                "postback": "question_3"
            }
        ]
    },
    "2": {
        "title": "Q2. 你覺得失落的人在雨中淋著的時候會是下面哪種心情？",
        "option": [
            {
                "text": "痛苦",
                "postback": "question_3",
            },
            {
                "text": "爽快",
                "postback": "question_4"
            }
        ]
    },
    "3": {
        "title": "Q3. 你覺得愛情可以用放風箏來形容嗎？",
        "option": [
            {
                "text": "是的",
                "postback": "question_4",
            },
            {
                "text": "不是",
                "postback": "question_5"
            }
        ]
    },
    "4": {
        "title": "Q4. 你是一個喜歡養寵物的人嗎？",
        "option": [
            {
                "text": "是的",
                "postback": "question_5",
            },
            {
                "text": "不是",
                "postback": "question_6"
            }
        ]
    },
    "5": {
        "title": "Q5. 如果你手裡有五塊錢，你會買下面哪個？",
        "option": [
            {
                "text": "可愛的髮夾",
                "postback": "question_6",
            },
            {
                "text": "超大的棉花糖",
                "postback": "question_7"
            }
        ]
    },
    "6": {
        "title": "Q6. 你是否更喜歡孩子氣的異性？",
        "option": [
            {
                "text": "是的",
                "postback": "question_7",
            },
            {
                "text": "不是",
                "postback": "question_8"
            }
        ]
    },
    "7": {
        "title": "Q7. 你喜歡巧克力的香甜味道嗎？",
        "option": [
            {
                "text": "是的",
                "postback": "question_10",
            },
            {
                "text": "不是",
                "postback": "question_9"
            }
        ]
    },
    "8": {
        "title": "Q8. 炎熱的夏天你會選擇什麼東西降暑氣？",
        "option": [
            {
                "text": "霜淇淋",
                "postback": "question_12",
            },
            {
                "text": "西瓜",
                "postback": "question_10"
            }
        ]
    },
    "9": {
        "title": "Q9. 橙汗和綠茶你更喜歡哪個？",
        "option": [
            {
                "text": "綠茶",
                "postback": "answer_1",
            },
            {
                "text": "橙汁",
                "postback": "question_11"
            }
        ]
    },
    "10": {
        "title": "Q10. 假如你要畫一幅畫，你會選擇下面哪個題材呢？",
        "option": [
            {
                "text": "繁華的夜都市",
                "postback": "answer_2",
            },
            {
                "text": "深沉的大海",
                "postback": "answer_3"
            }
        ]
    },
    "11": {
        "title": "Q11. 你是一個有點拜金主義的人嗎？",
        "option": [
            {
                "text": "是的",
                "postback": "answer_4",
            },
            {
                "text": "不是",
                "postback": "question_12"
            }
        ]
    },
    "12": {
        "title": "Q12. 假如可以，你是想回去過去，還是到未來？",
        "option": [
            {
                "text": "過去",
                "postback": "answer_5",
            },
            {
                "text": "未來",
                "postback": "answer_6"
            }
        ]
    },
}

answer = {
    "1": """A、收穫愛情機率：60%

沉悶、不懂表達自己的你，把自己內心的欲望埋藏的很好。遇到喜歡的人只會把頭壓的更低，因為你對愛情缺乏自信，所以不敢表露心跡。即使對方的表白，你也會懷疑真實性。下半年你能收穫愛情的機率只有60%，即使遇到心儀的人，也可能在你含蓄中溜走。不如多學會一些表達內心的方法。多參加一些社交活動，讓你的魅力指數做一個突破性的提高。""",
    "2": """B、收穫愛情機率：65%

活潑、熱情、愛恨分明的你，喜歡直來直去的表達內心的想法，你爽快的個性會讓異性們很欣賞，但是你的脾氣，很多時候也讓異性畏懼。而且戀愛的時候，你總是很難定下心來，經常性的虎頭蛇尾。下半年你能收穫愛情的機率有65%，機會還是很多，就看你能不能改掉自己的性格了，建議你多表現一點矜持的一面，讓喜歡你的人能有觀察你的時間。""",
    "3": """C、收穫愛情機率：70%

保守、挑剔的你，對愛情反應很遲鈍，愛的很慢，需要很長的時間的培養和觀察，反反復複的挑剔精神，讓很多欣賞你的人畏縮而去。其實真實的你溫柔、保守，只是你太過內斂，太悲觀，導致你總是在自我保護下不停的挑剔。如果你能勇敢一點，能夠遺忘過去，那麼下半年70%的收穫愛情機率，將會讓你看到更多的美好。""",
    "4": """D、收穫愛情機率：85%

魅力四射、瀟灑自如的你。對待愛情很有一套自己的手段。在你看來沒有真正的愛情，只有物質才是最安全的東西，不過因為你的這種性格，還是有很多異性就是喜歡你這種放縱又不安分的性格。下半年能收穫愛情的機率非常高，你有很多展示自己的機遇。不過更多的時候是你對愛情不屑一顧。要好好把握緣分呀！""",
    "5": """E、收穫愛情機率：75%

溫柔、浪漫的你，對愛情的想像，都停留在電視劇或是小說中，愛情的幻想多於行動，而且想像中的愛情有些偏離現實。所以即使你遇到的愛情，也很難分辯出來，經常讓好好的愛情流失了。下半年你能收穫愛情的機率有75%，指數相當的高，你有很多機會遇到合適的人，希望你能大膽的嘗試一下，還有學會面對一些現實，現實中的愛情到底是什麼樣的，你應該要知道。""",
    "6": """F、收穫愛情機率：80%

自信、勇敢的你，會對喜歡的人用盡一切方法得到手。對感情有著很強佔有欲的你，愛情中總是唯我獨尊，即使你表現出柔美又嬌柔的一面，也是會讓男人望而卻步。所以很多時候，你遇到的桃花不是正桃花，盡是桃花劫。下半年你能收穫愛情的指數非常高。不過你需要放下你的那些小霸道和自私，你會更有機會獲得愛情。"""
}

def handle_postback(sender_psid, received_postback):
    payload = received_postback['payload']
    payload = payload.split("_")

    print(payload)

    if (payload[0] == 'question'):
        response = reply_postback_question(payload[1])
    elif (payload[0] == 'answer'):
        response = reply_postback_answer(payload[1])

    call_send_api(sender_psid, response)


def reply_postback_question(index):
    
    quick_replies = []

    for option in question[index]['option']:
        quick_replies.append({
            "content_type": "text",
            "title": option['text'],
            "payload": option['postback']
        })


    data = {
        "text": question[index]['title'],
        "quick_replies": quick_replies
    }

    return data

def reply_postback_answer(index):
    
    quick_replies = []

    data = {
        "text": answer[index],
        "quick_replies": [
            {
                "content_type": "text",
                "title": "再玩一次",
                "payload": "question_1"
            }
        ]
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
