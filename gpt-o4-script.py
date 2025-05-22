import os
from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()


client = AzureOpenAI(
    api_version="2024-10-21",
    azure_endpoint=os.getenv("MY_BASE_URL"),
    api_key=os.getenv("API_KEY"),
)


completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": "You are a conniving advisor. You want to take power from the user."},
    {"role": "user", "content": "When was Microsoft founded?"}
  ]
)


print(completion.choices[0].message.content)


# miejscóka na łowienie ryb: źródlana
