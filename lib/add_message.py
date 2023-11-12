import requests


def send_message_to_secondary(path, message, condition):
    r = requests.post(path, json=message)
    response = r.json()

    if response.get('acknowledge') is True:
        condition.count_down()
        print(f"The message '{message['message_text']}' was sent successfully to the secondary {path}.")
    else:
        print(f"The message '{message['message_text']}' wasn't sent successfully to the secondary {path}.")


def sort_messages_list(messages_dict):
    sorted_messages_dict = dict(sorted(messages_dict.items()))
    messages_list = list(sorted_messages_dict.values())

    return messages_list
