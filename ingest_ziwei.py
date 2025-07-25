from app.utils import load_pdf_text, split_texts
from app.vectorstore import add_documents
from langchain_core.documents import Document

PDF_PATH = "ziwei.pdf"

if __name__ == "__main__":
    print("Loading PDF...")
    pages = load_pdf_text(PDF_PATH)
    print([len(page) for page in pages])
    print(f"Loaded {len(pages)} pages.")

    print("Splitting text into chunks...")
    chunks = split_texts(pages, chunk_size=1000, chunk_overlap=100)
    print(f"Created {len(chunks)} chunks.")

    # Wrap chunks as LangChain Document objects
    docs = [Document(page_content=chunk) for chunk in chunks]

    print("Adding documents to vector store...")
    add_documents(docs)
    print("Ingestion complete!") 