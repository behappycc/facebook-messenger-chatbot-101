def set_messenger_profile():
    data = {
        "get_started": {"payload": "question_1"},
        "greeting": [
            {
            "locale":"default",
            "text":"Facebook Messenger 聊天機器人實作班" 
            }
        ],
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
    resp = requests.post(
        API_URL + API_VERSION + 
        "/me/messenger_profile?access_token=" + 
        PAGE_ACCESS_TOKEN, json=data)