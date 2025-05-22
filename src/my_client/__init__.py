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
