import os
from time import sleep

from flask import Flask, request, jsonify


app = Flask(__name__)

messages_list = []

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')


@app.route("/get_messages")
def get_messages():
    return jsonify(messages_list)


@app.route("/add_message", methods=['POST'])
def add_message():
    data = request.get_json()
    message = data.get('message')
    response = {
        'acknowledge': True
    }

    if message is None:
        return "No message was sent.", 400

    sleep(10)
    messages_list.append(message)
    app.logger.debug(f'The message "{message}" has been received from {request.remote_addr}')

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=int(PORT))
