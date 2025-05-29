from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
import os


class MyVectorStore:
    def __init__(self, src_dir='pdfs'):
        load_dotenv()
        files = [f"{src_dir}/{file}" for file in os.listdir(src_dir) if '.pdf' in file]
        loaders = [PyPDFLoader(file) for file in files]
        splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)

        self.docs = []
        for loader in loaders:
            self.docs.extend(loader.load())

        self.split_docs = splitter.split_documents(self.docs)


print(MyVectorStore().split_docs)
