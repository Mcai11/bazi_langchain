from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import json

# 使用新的简化分析器
from app.bazi_lib.bazi.simple_bazi_analyzer import SimpleBaziAnalyzer

router = APIRouter()

class BaziRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    gender: str = "男"
    use_gregorian: bool = True

@router.post("/bazi_interpret")
async def bazi_interpret(request: BaziRequest):
    """使用简化分析器的八字解读API"""
    try:
        # 1. 使用简化分析器进行八字分析
        analyzer = SimpleBaziAnalyzer(
            request.year, request.month, request.day, request.hour,
            request.gender, request.use_gregorian
        )
        
        # 2. 获取分析结果
        bazi_result = analyzer.get_compatible_result()  # 使用兼容格式
        if not bazi_result.get('success'):
            return {
                "success": False,
                "error": bazi_result.get('error', '八字分析失败'),
                "bazi_result": {},
                "base_analysis": "",
                "knowledge_context": "",
                "query_used": "",
                "llm_interpretation": "八字分析失败，无法进行解读"
            }
        
        # 3. 生成分析摘要
        analysis_summary = analyzer.get_analysis_summary()
        
        # 4. 创建LLM查询
        llm_query = analyzer.get_llm_query()
        
        # 5. 知识库检索
        knowledge_context = ""
        try:
            from app.vectorstore import similarity_search
            docs = similarity_search(llm_query, k=3)
            knowledge_context = "\n".join([doc.page_content for doc in docs])
        except Exception as e:
            knowledge_context = f"知识库检索失败: {str(e)}"
        
        # 6. LLM解读
        llm_interpretation = ""
        try:
            from app.llm_factory import create_llm
            
            prompt = f"""请根据以下八字信息和相关知识，为用户提供专业的命理解读：

八字基本信息：
{analysis_summary}

相关命理知识：
{knowledge_context}

请提供：
1. 性格特点分析
2. 事业财运分析  
3. 感情婚姻分析
4. 健康运势分析
5. 人生建议
6. 直接推荐适合佩戴的首饰或水晶材质（如黄金、银、海蓝宝、紫水晶等），请以列表形式输出在最后一行，格式不限（如- 黄金、- 海蓝宝、- 紫水晶 或 ["黄金", "海蓝宝", "紫水晶"] 等均可），数量不超过5个，不要加解释。

请用专业但易懂的语言，结合传统命理学说进行分析。"""

            llm = create_llm()
            answer = llm.invoke(prompt)
            llm_interpretation = answer.content if hasattr(answer, 'content') else str(answer)
        
        except Exception as llm_error:
            llm_interpretation = f"LLM解读失败：{str(llm_error)}"
        
        # 7. 返回结果
        return {
            "success": True,
            "bazi_result": bazi_result,
            "base_analysis": analysis_summary,
            "knowledge_context": knowledge_context,
            "query_used": llm_query,
            "llm_interpretation": llm_interpretation
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "bazi_result": {},
            "base_analysis": "",
            "knowledge_context": "",
            "query_used": "",
            "llm_interpretation": f"分析过程中出现错误：{str(e)}"
        }

@router.get("/llm_info")
def get_llm_info():
    """获取当前LLM配置信息"""
    try:
        from app.llm_factory import get_provider_info
        return get_provider_info()
    except Exception as e:
        return {"error": str(e)}

@router.post("/test_llm")
def test_llm():
    """测试LLM连接"""
    try:
        from app.llm_factory import test_llm_connection
        return test_llm_connection()
    except Exception as e:
        return {"success": False, "error": str(e)} 