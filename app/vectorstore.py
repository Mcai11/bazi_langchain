# vectorstore.py
# Integration with Postgres + pgvector for LangChain

from langchain_community.vectorstores.pgvector import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from sqlalchemy import create_engine
from app import config

DB_CONNECTION_STRING = (
    f"postgresql+psycopg2://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}"
    f"@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
)

# Use a smaller, Chinese-optimized model
embeddings = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")


def get_vectorstore(collection_name: str = "ziwei_knowledge"):
    """
    Returns a PGVector vector store instance for the given collection.
    """
    return PGVector(
        collection_name=collection_name,
        connection_string=DB_CONNECTION_STRING,
        embedding_function=embeddings,
    )


def add_documents(docs, collection_name: str = "ziwei_knowledge"):
    """
    Adds a list of documents (strings or LangChain Document objects) to the vector store.
    """
    vectorstore = get_vectorstore(collection_name)
    vectorstore.add_documents(docs)


def similarity_search(query, k=3, collection_name: str = "ziwei_knowledge"):
    """
    Performs a similarity search for the query and returns the top k results.
    """
    vectorstore = get_vectorstore(collection_name)
    return vectorstore.similarity_search(query, k=k)