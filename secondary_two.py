from flask import Flask, request, jsonify
from time import sleep
import logging

app = Flask(__name__)

messages_list = []


@app.route("/get_messages")
def get_messages():
    return jsonify(messages_list)


@app.route("/add_message", methods=['POST'])
def add_message():
    data = request.get_json()
    message = data.get('message')
    acknowledge = {'acknowledge': True}

    if message is None:
        return "No message was sent.", 400

    sleep(10)
    messages_list.append(message)
    app.logger.debug(f'The message "{message}" has been received from {request.remote_addr} address')

    return jsonify(acknowledge)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8002)
