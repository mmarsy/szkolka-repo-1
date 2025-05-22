from my_client import Chat


string = '''
Your tas is to quiz user on geography. Questions should be easy. If user is correct and your response with "ADD POINT".
In your first message explain what you will be doing. Explain, that if they want to change subject, they can and they win if they score 10 points.
If they win, dont ask them any more questions and tell them to type "break" to end session.
'''

initial_prompt = [{'role': 'system', 'content': string}]
chat = Chat(initial_prompt=initial_prompt)

while True:
    prompt = input('USER: ')
    if prompt.lower() == 'break':
        break
    chat.ask(prompt)
