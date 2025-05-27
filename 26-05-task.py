import os
from openai import AzureOpenAI
from dotenv import load_dotenv


load_dotenv()
# Get an Azure OpenAI chat client
chat_client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("MY_BASE_URL"),
    api_key=os.getenv("API_KEY")
)

# Initialize prompt with system message
prompt = [
    {"role": "system", "content": "You are a helpful AI assistant."}
]

# Add a user input message to the prompt
input_text = input('Question: ')
prompt.append({"role": "user", "content": input_text})

# Additional parameters to apply RAG pattern using the AI Search index
rag_params = {
    "data_sources": [
        {
            "type": "azure_search",
            "parameters": {
                "endpoint": os.getenv("AI_SEARCH_URL"),
                "index_name": "my-index1",
                "authentication": {
                    "type": "api_key",
                    "key": os.getenv("AI_SEARCH_KEY"),
                },
                # Params for vector-based query
                "query_type": "vector",
                "embedding_dependency": {
                    "type": "deployment_name",
                    "deployment_name": "text-embedding-3-small",
                },
            }
        }
    ],
}

# Submit the prompt with the index information
response = chat_client.chat.completions.create(
    model="gpt-4o",
    messages=prompt,
    extra_body=rag_params
)

# Print the contextualized response
completion = response.choices[0].message.content
print(completion)
