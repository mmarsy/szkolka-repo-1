from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
import os


class MyVectorStore:
    def __init__(self, src_dir='pdfs', collection_name='my_documents'):
        load_dotenv()
        files = [f"{src_dir}/{file}" for file in os.listdir(src_dir) if '.pdf' in file]
        loaders = [PyPDFLoader(file) for file in files]
        splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)

        self.docs = []
        for loader in loaders:
            self.docs.extend(loader.load())

        self.split_docs = splitter.split_documents(self.docs)

        embedding = AzureOpenAIEmbeddings(
            azure_endpoint=os.environ["MY_BASE_URL"],
            azure_deployment="text-embedding-3-small",
            openai_api_version="2024-12-01-preview",
        )

        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")

        self.qdrant_vectorstore = QdrantVectorStore.from_documents(
            self.split_docs,
            embedding,
            url=url,
            api_key=api_key,
            collection_name=collection_name,
        )


if __name__ == '__main__':
    my_store = MyVectorStore()
    db = my_store.qdrant_vectorstore
    current_obj = None
    while True:
        user_input = input('Ask: ')
        if user_input.lower() == 'break':
            break

        if user_input == 'inspect':
            print(current_obj)
        else:
            query = db.max_marginal_relevance_search(user_input, k=5)
            print(query)
            current_obj = query[0]
