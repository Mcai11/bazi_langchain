import os
from app.utils import load_pdf_text, split_texts
from app.vectorstore import add_documents
from langchain_core.documents import Document

BOOKS_DIR = "books"

if __name__ == "__main__":
    for filename in os.listdir(BOOKS_DIR):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(BOOKS_DIR, filename)
            print(f"Loading PDF: {file_path}")
            pages = load_pdf_text(file_path)
            # 判断是否为图片版（所有页都无有效文本）
            if not any(page.strip() for page in pages):
                print(f"Skipped (likely image-based PDF): {filename}")
                continue
            print([len(page) for page in pages])
            print(f"Loaded {len(pages)} pages from {filename}.")

            print("Splitting text into chunks...")
            chunks = split_texts(pages, chunk_size=1000, chunk_overlap=100)
            print(f"Created {len(chunks)} chunks from {filename}.")

            docs = [Document(page_content=chunk, metadata={"source": filename}) for chunk in chunks]

            print(f"Adding documents from {filename} to vector store...")
            add_documents(docs)
            print(f"Ingestion complete for {filename}!\n") 