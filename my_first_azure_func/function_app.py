import azure.functions as func
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.chains import RetrievalQA
from langchain_community.chat_models.azure_openai import AzureChatOpenAI

import qdrant_client.http.exceptions as qdrant_exceptions

import os
import logging


class MyVectorStore:
    def __init__(self, src_dir='pdfs', collection_name='my_documents'):
        load_dotenv()

        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_URL"],
            azure_deployment=os.environ["EMBEDDINGS_MODEL"],
            openai_api_version=os.environ["API_VERSION"],
        )

        try:
            self.qdrant_vector_store = QdrantVectorStore.from_existing_collection(
                embedding=embeddings,
                collection_name=collection_name,
                url=os.environ["QDRANT_URL"],
                api_key=os.environ["QDRANT_API_KEY"],)
        
        except qdrant_exceptions.UnexpectedResponse:
            logging.warning(f"Collection {collection_name} does not exist. Creating a new one.")

            # Preparing to load and split documents
            files = [f"{src_dir}/{file}" for file in os.listdir(src_dir) if '.pdf' in file]
            loaders = [PyPDFLoader(file) for file in files]

            docs = []
            for loader in loaders:
                docs.extend(loader.load())
            splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
            split_docs = splitter.split_documents(docs)

            # Creating a new Qdrant vector store
            self.qdrant_vector_store = QdrantVectorStore.from_documents(
                documents=split_docs,
                embedding=embeddings,
                url=os.environ["QDRANT_URL"],
                api_key=os.environ["QDRANT_API_KEY"],
                collection_name=collection_name,
            )

    def query(self, question: str, k: int = 5):
        return self.qdrant_vector_store.max_marginal_relevance_search(question, k=k)


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    load_dotenv()

    model = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_URL"],
        azure_deployment=os.environ["CHAT_MODEL"],
        openai_api_version=os.environ["API_VERSION"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
    )

    retrival_qa = RetrievalQA.from_chain_type(llm=model, 
                              retriever=MyVectorStore().qdrant_vector_store.as_retriever(serch_kwargs={"k": 5}))
    
    try:
        user_question= req.get_json().get('question')
    
    except ValueError:
        return func.HttpResponse(
            "Please pass a query in the request body",
            status_code=400
        )

    retrival_qa_response = retrival_qa.run(user_question)
    return func.HttpResponse(retrival_qa_response, status_code=200)
    