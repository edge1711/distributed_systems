import os
from time import sleep

from flask import Flask, request, jsonify

from lib.add_message import sort_messages_list

app = Flask(__name__)

messages_dict = {}
messages_list = []

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')


@app.route("/get_messages")
def get_messages():
    return jsonify(messages_list)


@app.route("/add_message", methods=['POST'])
def add_message():
    global messages_list

    message = request.get_json()
    message_text = message.get('message_text')
    message_order = message.get('order')

    response = {
        'acknowledge': True
    }

    if message_text is None:
        return "No message was sent.", 400

    sleep(2)
    messages_dict[message_order] = message_text
    messages_list = sort_messages_list(messages_dict)
    app.logger.debug(f'The message "{message_text}" has been received from {request.remote_addr}')

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=int(PORT))
