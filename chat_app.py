from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.chains import RetrievalQA
from langchain_community.chat_models.azure_openai import AzureChatOpenAI

import qdrant_client.http.exceptions as qdrant_exceptions

import os
import logging
import time

import streamlit as st
import requests
from dotenv import load_dotenv


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


model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_URL"],
    azure_deployment=os.environ["CHAT_MODEL"],
    openai_api_version=os.environ["API_VERSION"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

# retriever=MyVectorStore(src_dir='math_pdfs', collection_name='maths').qdrant_vector_store.as_retriever(serch_kwargs={"k": 5})
retrival_qa = RetrievalQA.from_chain_type(llm=model, 
                              retriever=MyVectorStore(src_dir="math_pdfs", collection_name="maths").qdrant_vector_store.as_retriever(serch_kwargs={"k": 5}))

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input("What is up?")
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ''

        assistant_response = retrival_qa.run(prompt)
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})