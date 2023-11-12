import os
import concurrent.futures
from itertools import repeat

from flask import Flask, request, jsonify

from lib.countdown_latch import CountDownLatch
from lib.add_message import send_message_to_secondary, sort_messages_list


SECONDARY_ONE_HOST = os.getenv('SECONDARY_ONE_HOST')
SECONDARY_ONE_PORT = os.getenv('SECONDARY_ONE_PORT')

SECONDARY_TWO_HOST = os.getenv('SECONDARY_TWO_HOST')
SECONDARY_TWO_PORT = os.getenv('SECONDARY_TWO_PORT')

SECONDARY_PATHS = [
    f'{SECONDARY_ONE_HOST}:{SECONDARY_ONE_PORT}/add_message',
    f'{SECONDARY_TWO_HOST}:{SECONDARY_TWO_PORT}/add_message'
]

app = Flask(__name__)

messages_dict = {}
messages_list = []
message_order_index = 0


@app.route("/get_messages")
def get_messages():
    return jsonify(messages_list)


@app.route("/add_message", methods=['POST'])
def add_message():
    global message_order_index, messages_list
    message_order_index += 1

    message = request.get_json()
    message['order'] = message_order_index

    message_text = message.get('message_text')
    if message_text is None:
        return "No message was sent.", 400

    write_concern = message.pop('write_concern', 1) - 1
    thread_amount = len(SECONDARY_PATHS)

    condition = CountDownLatch(write_concern)

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_amount) as executor:
        executor.map(send_message_to_secondary, SECONDARY_PATHS, repeat(message), repeat(condition))
        condition.wait()

        messages_dict[message_order_index] = message_text
        messages_list = sort_messages_list(messages_dict)
        print("The message was added to the main.")

        return f"The message '{message['message_text']}' was sent successfully to the main " \
               f"and {write_concern} secondaries.", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
