from Improvement.schemas.Improvement_dto import ImprovementResponse  
from Improvement.core.Improvement_config import IMPROVEMENT  

#-------[LangChain Core]--------------------
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import JsonOutputParser

#--------------------------------------------
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()
#--------------------------------------------

# 불공정 약관 개선 체인
improvement_llm = ChatOpenAI(temperature=0.1, model="gpt-4o-mini").bind(
    response_format={"type": "json_object"}
)

parser = JsonOutputParser(pydantic_object=ImprovementResponse)  

improvement_prompt = ChatPromptTemplate.from_template(
    IMPROVEMENT,  
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

def get_improvement_chain(
        llm: ChatOpenAI, 
        prompt: ChatPromptTemplate, 
        parser: JsonOutputParser
) -> RunnableSequence:
    """
    약관 개선을 위한 LangChain 체인 생성
    """
    chain = ( 
        prompt
        | llm
        | parser
    )
    return chain

improvement_chain = get_improvement_chain(
    improvement_llm,
    improvement_prompt,
    parser
)

# 개선안 생성 함수 (이전 generate_improvements 대체)
def generate_improvements(analysis_result: dict) -> ImprovementResponse:
    """
    불공정 약관 분석 결과를 받아 개선안을 생성
    """
    from Terms_Analyze.core.MVP_rag import get_retriever
        
    retriever = get_retriever()
    
    # 관련 법률 검색 (약관 개선 기준)
    law_docs = retriever.invoke("약관 개선 기준 불공정 조항 수정")
    law_context = "\n".join([doc.page_content for doc in law_docs]) if law_docs else "약관규제법 제3~7조"
    
    chain_input = {
        "unfair_clauses": analysis_result.get("unfairClauses", []),
        "overall_summary": analysis_result.get("overallSummary", ""),
        "law_context": law_context
    }
    
    result = improvement_chain.invoke(chain_input)
    return ImprovementResponse(**result)