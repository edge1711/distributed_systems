import os
import requests
import concurrent.futures
from itertools import repeat

from flask import Flask, request, jsonify


SECONDARY_ONE_HOST = os.getenv('SECONDARY_ONE_HOST')
SECONDARY_ONE_PORT = os.getenv('SECONDARY_ONE_PORT')

SECONDARY_TWO_HOST = os.getenv('SECONDARY_TWO_HOST')
SECONDARY_TWO_PORT = os.getenv('SECONDARY_TWO_PORT')

SECONDARY_PATHS = [
    f'{SECONDARY_ONE_HOST}:{SECONDARY_ONE_PORT}/add_message',
    f'{SECONDARY_TWO_HOST}:{SECONDARY_TWO_PORT}/add_message'
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
    thread_amount = len(SECONDARY_PATHS)

    if message is None:
        return "No message was sent.", 400

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_amount) as executor:
        results = executor.map(send_message_to_secondary, repeat(message), SECONDARY_PATHS)

        for response in results:
            if response[0].get('acknowledge') is True:
                app.logger.debug(f"The message '{message}' was sent successfully to the secondary {response[1]}.")
            else:
                return f"The message '{message}' wasn't sent successfully to the secondary {response[1]}.", 400

    messages_list.append(message)

    return f"The message '{message}' was sent successfully to all secondaries and to the master", 200


def send_message_to_secondary(message, path):
    data = {"message": message}
    r = requests.post(path, json=data)
    response = r.json()

    return response, path


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
