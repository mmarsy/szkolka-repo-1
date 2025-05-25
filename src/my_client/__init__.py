import os
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI


class FormattedUsage(dict):
    def __init__(self, response_usage):
        super().__init__()
        self['prompt_tokens'] = response_usage.prompt_tokens
        self['completion_tokens'] = response_usage.completion_tokens
        self['total_tokens'] = response_usage.total_tokens


class Chat(list):
    def __init__(self, initial_prompt, chat_client=None, model='gpt-4o', initiative=True, logger=None):
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
        super().__init__(initial_prompt)

        if initiative:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self
            )
            if self.logger is not None:
                self.logger.info(FormattedUsage(response.usage))
            response_content = response.choices[0].message.content
            print(f'CHAT: {response_content}')
            self.append({'role': 'assistant', 'content': response_content})

    def ask(self, prompt):
        self.append({'role': 'user', 'content': prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self
        )
        if self.logger is not None:
            self.logger.info(FormattedUsage(response.usage))
        response_content = response.choices[0].message.content
        self.append({'role': 'assistant', 'content': response_content})
        return f'CHAT: {response_content}'


if __name__ == '__main__':
    pass
