import requests
import json

import sys

from app.lib.comment_parser import parse_comment

def process_input(user_input):
    comment = parse_comment(user_input)

    # set the default log type if not specified by the user
    if not comment.log_type:
        user_input = '[thought]' + user_input
    return user_input

def send_input(user_input):
    data = {"log-comment": user_input}
    headers = {"Content-Type": "application/json"}

    response = requests.post("http://localhost:5000/submit", 
                             data=json.dumps(data), 
                             headers=headers)
    
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message: {response.status_code}")


if len(sys.argv) > 1:
    user_input = ' '.join(sys.argv[1:])

    user_input = process_input(user_input)

    send_input(user_input)
else:
    while True:
        user_input = input("Enter your Log: ")

        user_input = process_input(user_input)

        send_input(user_input)
