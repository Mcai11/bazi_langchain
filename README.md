# LangChain FastAPI Starter

This project is a starter template for building web applications using [LangChain](https://github.com/langchain-ai/langchain) and [FastAPI](https://fastapi.tiangolo.com/).

## Features
- FastAPI backend
- LangChain integration for LLM workflows
- Ready for deployment with Uvicorn

## Setup

1. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```sh
   uvicorn app.main:app --reload
   ```

## Project Structure
```
langchain_project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── chains.py
│   ├── agents.py
│   └── utils.py
├── requirements.txt
├── README.md
└── venv/
``` 