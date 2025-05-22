import os
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()
logger = logging.getLogger('USAGE')
logging.basicConfig(filename='logs/usage.md', level=logging.INFO)


client = AzureOpenAI(
    api_version="2024-10-21",
    azure_endpoint=os.getenv("MY_BASE_URL"),
    api_key=os.getenv("API_KEY"),
)


class FormattedUsage(dict):
    def __init__(self, response_usage):
        super().__init__()
        self['prompt_tokens'] = response_usage.prompt_tokens
        self['completion_tokens'] = response_usage.completion_tokens
        self['total_tokens'] = response_usage.total_tokens


class Chat(list):
    def __init__(self, initial_prompt, chat_client=client, model='gpt-4o', initiative=True):
        self.client = chat_client
        self.model = model
        super().__init__(initial_prompt)

        if initiative:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self
            )
            response_content = response.choices[0].message.content
            print(f'CHAT: {response_content}')
            self.append({'role': 'assistant', 'content': response_content})

    def ask(self, prompt, to_print=True):
        self.append({'role': 'user', 'content': prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self
        )
        logger.info(FormattedUsage(response.usage))
        response_content = response.choices[0].message.content
        if to_print:
            print(f'CHAT: {response_content}')

        self.append({'role': 'assistant', 'content': response_content})
