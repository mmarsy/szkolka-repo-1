import os
import logging
import json
from dotenv import load_dotenv
from openai import AzureOpenAI


class FormattedUsage(dict):
    def __init__(self, response_usage):
        super().__init__()
        self['prompt_tokens'] = response_usage.prompt_tokens
        self['completion_tokens'] = response_usage.completion_tokens
        self['total_tokens'] = response_usage.total_tokens


class MyClient(AzureOpenAI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger = logging.getLogger('USAGE')
        logger.propagate = False
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(os.getenv('USAGE_LOG_FILE'))
        formatter = logging.Formatter(fmt='%(asctime)s | %(levelname)s | %(name)s: %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.logger = logger


class Chat(list):
    def __init__(self, initial_prompt, chat_client=None, model='gpt-4o', initiative=True, logger=None,
                 chat_indicator='', user_indicator='USER: ', **kwargs):
        load_dotenv()

        if chat_client is None:
            chat_client = AzureOpenAI(
                api_version="2024-10-21",
                azure_endpoint=os.getenv("MY_BASE_URL"),
                api_key=os.getenv("API_KEY"),
            )

        if logger is None:
            logger = logging.getLogger('USAGE')
            logger.propagate = False
            logger.setLevel(logging.INFO)

            handler = logging.FileHandler(os.getenv('USAGE_LOG_FILE'))
            formatter = logging.Formatter(fmt='%(asctime)s | %(levelname)s | %(name)s: %(message)s',
                                          datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        self.logger = logger
        self.client = chat_client
        self.model = model
        self.chat_indicator = chat_indicator
        self.user_indicator = user_indicator
        super().__init__(initial_prompt)

        if initiative:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self,
                **kwargs
            )
            if self.logger is not None:
                self.logger.info(FormattedUsage(response.usage))
            response_content = response.choices[0].message.content
            print(f'{self.chat_indicator}{response_content}')
            self.append({'role': 'assistant', 'content': response_content})

    def ask(self, prompt, **kwargs):
        self.append({'role': 'user', 'content': prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self,
            **kwargs
        )
        if self.logger is not None:
            self.logger.info(FormattedUsage(response.usage))
        response_content = response.choices[0].message.content
        self.append({'role': 'assistant', 'content': response_content})
        return f'{self.chat_indicator}{response_content}'

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(json.dumps(self, indent=4))

    @staticmethod
    def read_json(filename, **kwargs):
        with open(filename, 'r') as f:
            obj = json.load(f)
            return Chat(obj, **kwargs)


if __name__ == '__main__':

    string = '''
    Your tas is to quiz user on geography. Questions should be easy. If user is correct and your response with "ADD POINT".
    In your first message explain what you will be doing. Explain, that if they want to change subject, they can and they win if they score 10 points.
    If they win, dont ask them any more questions and tell them to type "break" to end session.
    '''

    initial_prompt = [{'role': 'system', 'content': string}]
    chat = Chat(initial_prompt=initial_prompt)
    chat.save('test_save.json')
    del chat

    chat = Chat.read_json('test_save.json', initiative=False)
    chat.ask(input('USER: '))

