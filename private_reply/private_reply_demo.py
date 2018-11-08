import argparse
import logging

import requests
from flask import Flask, request, Response
from flask_restful import Resource, Api

PAGE_ACCESS_TOKEN = '<PAGE_ACCESS_TOKEN>'
API_URL = 'https://graph.facebook.com/'
API_VERSION = 'v3.2'
VERIFY_TOKEN = '<VERIFY_TOKEN>'

event_post_id = "<POST_ID>"
signal = "<COMMENT>"

def main():
    app = Flask(__name__)
    api = Api(app)
    logging.basicConfig(level=logging.DEBUG)

    api.add_resource(Webhook, '/webhook')

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

        try:
            if data['object'] == 'page':
                for entry in data['entry']:
                    if "changes" in entry:
                        handle_comment(entry)

        except KeyError as e:
            logging.debug(str(e))

        return {'message': 'EVENT_RECEIVED'}, 200

def handle_comment(entry):
    post_id = entry['changes'][0]['value']['parent_id'].split("_")[
                        1]
    item = entry['changes'][0]['value']['item']
    verb = entry['changes'][0]['value']['verb']

    if item != "comment" or verb != "add":
        return

    if post_id != event_post_id: # 如果留言的貼文不在我們的設定裡面 就結束
        return

    print("check +1")
    message = entry['changes'][0]['value']['message']

    if signal!="" and signal!=message:
        return

    sender_id = entry['changes'][0]['value']['from']['id']
    sender_name = entry['changes'][0]['value']['from']['name']
    comment_id = entry['changes'][0]['value']['comment_id']

    send_private_reply(comment_id, "私訊內容")
    send_comment(comment_id, "留言內容")


    return "ok"

def send_private_reply(comment_id, text):
    try:
        resp = requests.post(
            "{}/{}/{}/private_replies?access_token={}&message={}".format(
                API_URL, API_VERSION, comment_id, PAGE_ACCESS_TOKEN, text))
    except Exception as e:
        logging.error('Unable to send message:' + e)

def send_comment(comment_id, message):
    try:
        url = f'{API_URL}/{API_VERSION}/{comment_id}/comments'
        params = {
            'message': message,
            'access_token': PAGE_ACCESS_TOKEN
        }
        resp = requests.post(url, params=params)

    except Exception as e:
        logging.error('Unable to send message:' + e)

if __name__ == "__main__":
    main()