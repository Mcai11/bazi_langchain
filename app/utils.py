# utils.py
# Utility functions for your app

from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_pdf_text(pdf_path: str) -> List[str]:
    """
    Loads a PDF and returns a list of page texts.
    """
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    return [page.page_content for page in pages]


def split_texts(texts: List[str], chunk_size: int = 1000, chunk_overlap: int = 100) -> List[str]:
    """
    Splits a list of texts into smaller chunks for embedding.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = []
    for text in texts:
        chunks.extend(splitter.split_text(text))
    return chunks