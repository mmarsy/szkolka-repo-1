from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os
import fitz
import logging
from openai import AzureOpenAI
from azure.search.documents.indexes.models import (
    ComplexField,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchAlgorithmKind
)


load_dotenv()


def extract_paragraphs(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text("text") + "\n"
    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
    return [{"id": str(i), "content": paragraph} for i, paragraph in enumerate(paragraphs)]


def get_embedding(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text("text") + "\n"
    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]

    client = AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=os.getenv("MY_BASE_URL"),
        api_key=os.getenv("API_KEY")
    )

    def embed(string):
        response = client.embeddings.create(
            input=string,
            model="text-embedding-3-small"
        )
        return response.data

    return [{"id": str(i), "content": paragraph, "contentVector": embed(paragraphs)} for i, paragraph in enumerate(paragraphs) if i < 10]


def semantic_ask(prompt="Czym jest apriori?"):
    load_dotenv()

    index_name = 'my-sophisticated-index'
    index_client = SearchIndexClient(endpoint=os.getenv("AI_SEARCH_URL"),
                                     credential=AzureKeyCredential(os.getenv("AI_SEARCH_KEY")))

    fields = [
        SimpleField(name='id', type=SearchFieldDataType.String, key=True),
        SearchableField(name='content', type=SearchFieldDataType.String),
    ]

    semantic_config = SemanticConfiguration(
        name='my-config',
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="content")]
        )
    )

    semantic_search = SemanticSearch(configurations=[semantic_config])
    semantic_settings = SemanticSearch(configurations=[semantic_config])
    scoring_profiles = []

    # Create the search index with the semantic settings
    documents = extract_paragraphs('pdfs/husserl1.pdf')
    index = SearchIndex(name=index_name, fields=fields, scoring_profiles=scoring_profiles,
                        semantic_search=semantic_search)
    result = index_client.create_or_update_index(index)
    logging.info(f'Created {result}')

    search_client = SearchClient(endpoint=os.getenv('AI_SEARCH_URL'),
                                 index_name=index_name,
                                 credential=AzureKeyCredential(os.getenv('AI_SEARCH_KEY')))
    try:
        result = search_client.upload_documents(documents=documents)
        print("Upload of new document succeeded: {}".format(result[0].succeeded))
    except Exception as ex:
        print(ex.message)

        index_client = SearchIndexClient(
            endpoint=os.getenv('AI_SEARCH_URL'), credential=AzureKeyCredential(os.getenv('AI_SEARCH_KEY')))

    results = search_client.search(query_type='semantic', semantic_configuration_name='my-semantic-config',
                                   search_text="czym jest apriori",
                                   select='content,id', query_caption='extractive',
                                   query_answer="extractive", )

    semantic_answers = results.get_answers()

    for answer in semantic_answers:
        if answer.highlights:
            print(f"Semantic Answer: {answer.highlights}")
        else:
            print(f"Semantic Answer: {answer.text}")
        print(f"Semantic Answer Score: {answer.score}\n")

    for result in results:
        print(result["@search.reranker_score"])
        print(result["HotelName"])
        print(f"Description: {result['Description']}")

        captions = result["@search.captions"]
        if captions:
            caption = captions[0]
            if caption.highlights:
                print(f"Caption: {caption.highlights}\n")
            else:
                print(f"Caption: {caption.text}\n")


def vector_ask(prompt="Czym jest apriori?"):
    load_dotenv()

    index_name = 'my-sophisticated-index'
    index_client = SearchIndexClient(endpoint=os.getenv("AI_SEARCH_URL"),
                                     credential=AzureKeyCredential(os.getenv("AI_SEARCH_KEY")))

    fields = [
        SimpleField(name='id', type=SearchFieldDataType.String, key=True),
        SearchableField(name='content', type=SearchFieldDataType.String),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="vector-config",
                kind=VectorSearchAlgorithmKind.HNSW,
                hnsw_parameters={"m": 4, "efConstruction": 400}
            )
        ]
    )


if __name__ == '__main__':
    print(get_embedding('pdfs/husserl1.pdf')[0]['contentVector'])
