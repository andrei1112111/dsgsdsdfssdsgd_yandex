from flask import Flask, request
import logging
import json
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:
        sessionStorage[user_id] = {'suggests': ["начать"]}
        res['response']['text'] = 'Привет! В этом навыке я заставлю тебя купить слона. Скажи НАЧАТЬ.'
        res['response']['buttons'] = get_suggests(user_id)
        return
    if 'помощь' in req['request']['original_utterance'].lower() or 'что ты умеешь' in req['request'][
        'original_utterance'].lower():
        sessionStorage[user_id] = {'suggests': ["начать"]}
        res['response']['text'] = 'Чтобы начать игру скажи НАЧАТЬ, а чтобы закончить скажи ХВАТИТ.'
        res['response']['buttons'] = get_suggests(user_id)
        return
    if req['request']['original_utterance'].lower() == 'начать':
        sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!"]}
        res['response']['text'] = 'Привет. Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in ['ладно', 'куплю', 'покупаю', 'хорошо']:
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return
    try:
        res['response']['text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
        res['response']['buttons'] = get_suggests(user_id)
    except Exception:
        sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!"]}
        res['response']['text'] = 'Ну купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
    if 'хватит' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Вы так и не купили слона('
        res['response']['end_session'] = True
        return


def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session
    if len(suggests) < 2 and suggests[0]['title'] != 'начать':
        suggests.append({"title": "Ладно", "url": "https://market.yandex.ru/search?text=слон", "hide": True})
    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    app.run()
