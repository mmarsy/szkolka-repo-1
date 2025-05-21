import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)


client = AzureOpenAI(
  azure_endpoint = "https://mikolaj-marsy-3981-resource.openai.azure.com/", 
  azure_ad_token_provider=token_provider,
  api_version="2024-10-21"
)


completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "When was Microsoft founded?"}
  ]
)


print(completion.model_dump_json(indent=2))