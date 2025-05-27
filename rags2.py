from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os
import fitz
from azure.search.documents.indexes.models import (
    ComplexField,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch
)


def extract_paragraphs(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text("text") + "\n"
    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
    return [{"id": str(i), "content": paragraph} for i, paragraph in enumerate(paragraphs)]


def main2():
    load_dotenv()


    endpoint = os.getenv("AI_SEARCH_URL")
    index_name = "my-index"
    api_key = os.getenv("AI_SEARCH_KEY")

    search_client = SearchClient(endpoint=endpoint,
                                 index_name=index_name,
                                 credential=AzureKeyCredential(api_key))

    documents = [
        {
            "id": "1",
            "content": "Azure AI Search enables semantic and vector search."
        },
        {
            "id": "2",
            "content": "It integrates with OpenAI to power RAG workflows."
        }
    ]

    result = search_client.upload_documents(documents)
    print(f"Upload result: {result}")

    results = search_client.search("openai integration")
    for result in results:
        print(result["content"])


if __name__ == '__main__':
    index_client = SearchIndexClient(endpoint=os.getenv("AI_SEARCH_URL"),
                                     credential=AzureKeyCredential(os.getenv("AI_SEARCH_KEY")))

    fields = []
