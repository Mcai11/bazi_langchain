from fastapi import FastAPI, Query
from pydantic import BaseModel, SecretStr
from app.vectorstore import similarity_search
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fengshuijewery.myshopify.com",
        "https://5uaame-ip-38-90-17-41.tunnelmole.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 你的路由注册
from app.bazi_interpret import router as bazi_router
app.include_router(bazi_router)

class AskRequest(BaseModel):
    question: str
    k: int = 3

@app.get("/")
def read_root():
    return {"message": "Welcome to the LangChain FastAPI Starter!"}

@app.post("/ask")
def ask(request: AskRequest):
    try:
        from app.llm_factory import create_llm
        
        # Retrieve relevant chunks
        docs = similarity_search(request.question, k=request.k)
        context = "\n".join([doc.page_content for doc in docs])
        prompt = f"根据以下内容回答问题：\n{context}\n\n问题：{request.question}\n答案："
        
        # Get answer from LLM
        llm = create_llm()
        answer = llm.invoke(prompt)
        return {"answer": answer.content if hasattr(answer, 'content') else str(answer)}
    
    except Exception as e:
        return {"answer": f"处理问题时出现错误: {str(e)}"} 