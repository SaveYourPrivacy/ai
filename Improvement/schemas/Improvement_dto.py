from typing import List
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from Terms_Analyze.core.MVP_config import PromptTemplates
from Terms_Analyze.core.MVP_rag import get_retriever
from Terms_Analyze.schemas.MVP_dto import TermsResponse

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class Improvement(BaseModel):
    clause_id: int
    original_clause: str
    issue_type: str
    suggested_revision: str
    legal_basis: str
    revision_reason: str

class ImprovementResponse(BaseModel):
    improvements: List[Improvement]
    overall_summary: str

def generate_improvements(analysis_result: TermsResponse) -> ImprovementResponse:
    """불공정 약관 분석 결과를 받아 개선안을 생성"""
    retriever = get_retriever()
    
    # 불공정 조항들만 추출
    unfair_clauses = analysis_result.unfairClauses or []
    if not unfair_clauses:
        return ImprovementResponse(
            improvements=[],
            overall_summary="불공정 조항이 발견되지 않았습니다."
        )
    
    # 관련 법률 검색
    relevant_laws = retriever.invoke("약관 개선 기준") or "약관규제법 제3~7조"
    
    # 개선 프롬프트 생성
    improvement_prompt = ChatPromptTemplate.from_template(PromptTemplates.IMPROVEMENT)
    parser = JsonOutputParser(pydantic_object=ImprovementResponse)
    
    chain = improvement_prompt | llm | parser
    
    input_data = {
        "unfair_clauses": unfair_clauses,
        "law_context": relevant_laws,
        "overall_summary": analysis_result.overallSummary
    }
    
    result = chain.invoke(input_data)
    return ImprovementResponse(**result)