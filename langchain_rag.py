from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_vdms.vectorstores import VDMS, VDMS_Client
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os
import socket


load_dotenv()


def start_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        s.listen()
        print(f"Listening on port {port}...")
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)


def setup(loaders=None, splitter=None):  # -> list[Document]
    if loaders is None:
        loaders = [
            PyPDFLoader('pdfs/husserl1.pdf'),
            PyPDFLoader('pdfs/husserl2.pdf')
        ]

    if splitter is None:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100, separators=['\n', '.'])

    docs = []
    for loader in loaders:
        docs.extend(loader.load())

    return splitter.split_documents(docs)


def get_chroma_vectordb(documents=None, embedding=None, persist_directory=None):
    if embedding is None:
        embedding = AzureOpenAIEmbeddings(
            azure_endpoint=os.getenv("MY_BASE_URL"),
            azure_deployment='text-embedding-3-small',
            openai_api_version='2024-12-01-preview',

        )

    if documents is None:
        documents = setup()

    vectordb = Chroma.from_documents(documents=documents[1:10],
                                     embedding=embedding,)
    return vectordb


def get_vdms_vectordb(documents=None, embedding=None):
    if embedding is None:
        embedding = AzureOpenAIEmbeddings(
            azure_endpoint=os.getenv("MY_BASE_URL"),
            azure_deployment='text-embedding-3-small',
            openai_api_version='2024-12-01-preview',

        )

    if documents is None:
        documents = setup()

    collection_name = "test_collection_faiss_L2"
    vdms_client = VDMS_Client(host="localhost", port=55555)
    vector_store = VDMS(
        client=vdms_client,
        embedding=embedding,
        collection_name=collection_name,
        engine="FaissFlat",
        distance_strategy="L2",
    )

    import logging

    logging.basicConfig()
    logging.getLogger("langchain_vdms.vectorstores").setLevel(logging.INFO)

    from langchain_core.documents import Document

    document_1 = Document(
        page_content="I had chocolate chip pancakes and scrambled eggs for breakfast this morning.",
        metadata={"source": "tweet"},
        id=1,
    )

    document_2 = Document(
        page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",
        metadata={"source": "news"},
        id=2,
    )

    document_3 = Document(
        page_content="Building an exciting new project with LangChain - come check it out!",
        metadata={"source": "tweet"},
        id=3,
    )

    document_4 = Document(
        page_content="Robbers broke into the city bank and stole $1 million in cash.",
        metadata={"source": "news"},
        id=4,
    )

    document_5 = Document(
        page_content="Wow! That was an amazing movie. I can't wait to see it again.",
        metadata={"source": "tweet"},
        id=5,
    )

    document_6 = Document(
        page_content="Is the new iPhone worth the price? Read this review to find out.",
        metadata={"source": "website"},
        id=6,
    )

    document_7 = Document(
        page_content="The top 10 soccer players in the world right now.",
        metadata={"source": "website"},
        id=7,
    )

    document_8 = Document(
        page_content="LangGraph is the best framework for building stateful, agentic applications!",
        metadata={"source": "tweet"},
        id=8,
    )

    document_9 = Document(
        page_content="The stock market is down 500 points today due to fears of a recession.",
        metadata={"source": "news"},
        id=9,
    )

    document_10 = Document(
        page_content="I have a bad feeling I am going to get deleted :(",
        metadata={"source": "tweet"},
        id=10,
    )

    documents = [
        document_1,
        document_2,
        document_3,
        document_4,
        document_5,
        document_6,
        document_7,
        document_8,
        document_9,
        document_10,
    ]

    doc_ids = [str(i) for i in range(1, 11)]
    vector_store.add_documents(documents=documents, ids=doc_ids)

    # vector_store.add_documents(documents=documents, ids=[str(i) for i, _ in enumerate(documents)])
    return vector_store


# vectordb = get_vectordb()
# print('...')
# question = 'Czym jest apriori?'
# docs = vectordb.similarity_search(question, k=3)
# print(docs[0].page_content)

print(get_vdms_vectordb())
