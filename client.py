import requests
from langchain_community.chat_models.azure_openai import AzureChatOpenAi


def call_func(data=None, url="http://localhost:7071/api/hello"):
    if data is None:
        data = {"name": "dummy"}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    call_func()
