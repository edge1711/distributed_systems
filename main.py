from flask import Flask, request, jsonify
import requests
import logging


SECONDARY_PATHS = [
    'http://secondary_one:8001/add_message',
    'http://secondary_two:8002/add_message'
]


app = Flask(__name__)

messages_list = []


@app.route("/get_messages")
def get_messages():
    return jsonify(messages_list)


@app.route("/add_message", methods=['POST'])
def add_message():
    data = request.get_json()
    message = data.get('message')
    if message is None:
        return "No message was sent.", 400

    for s in SECONDARY_PATHS:
        response = send_message_to_secondary(message, s)
        if response.get('acknowledge') is True:
            logging.info(f"The message '{message}' was sent successfully to the secondary {s}.")
        else:
            return f"The message '{message}' wasn't sent successfully to the secondary {s}.", 400

    messages_list.append(message)

    return f"The message '{message}' was sent successfully to all secondaries and to the master", 200


def send_message_to_secondary(message, path):
    data = {"message": message}
    r = requests.post(path, json=data)
    response = r.json()

    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
