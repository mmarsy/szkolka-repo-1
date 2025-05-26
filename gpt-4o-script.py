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


response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": "You are a conniving advisor. You want to take power from the user."},
    {"role": "user", "content": "When was Microsoft founded?"}
  ]
)


class FormattedUsage(dict):
    def __init__(self, response_usage):
        super().__init__()
        self['prompt_tokens'] = response_usage.prompt_tokens
        self['completion_tokens'] = response_usage.completion_tokens
        self['total_tokens'] = response_usage.total_tokens


print(response.choices[0].message.content)
logger.info(FormattedUsage(response.usage))


# miejscóka na łowienie ryb: źródlana
