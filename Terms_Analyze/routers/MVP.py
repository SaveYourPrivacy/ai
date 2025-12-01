from typing import List
from fastapi import APIRouter
from Terms_Analyze.schemas.MVP_dto import ActionGuideline, AdditionalNoteInput, TermInput, TermsResponse, UnfairClause
from Terms_Analyze.core.MVP_rag import get_retriever
from Terms_Analyze.core.MVP_chain import term_chain

from AdditionalNotes.MVP_AdditionalNotes import generate_action_guidelines

router = APIRouter(
    tags=["UnfairTerm Analysis"]
)

#-----[ FastAPI ]-----------------------
@router.post("/terms_analyze", response_model=TermsResponse)
def analyze(input: TermInput) -> TermsResponse:
    
    retriever = get_retriever()
    # RAG 생성 실패시 예외처리
    if retriever is None:
        print("경고: 검색기가 준비되지 않았습니다. RAG 없이 일반 분석을 수행합니다.")
        law_context_text = "일반 상식 (법률 데이터 로드 실패)"
    else:
        # 입력 약관으로 법률 DB 검색
        law_context_docs = retriever.invoke(input.term)
        
        # 검색된 문서(docs)들을 하나의 텍스트로 합침
        law_context_text = "\n\n".join([doc.page_content for doc in law_context_docs])

    # model_dump() 대신 직접 LLM 프롬프트에 입력될 딕셔너리 구성
    chain_input = {
        "term": input.term,
        "category": input.category,
        "law_context": law_context_text
    }
    
    # LLM 호출 및 출력값 반환
    response = term_chain.invoke(chain_input) # response는 parser에 의해 생성된 딕셔너리가 초기화됨.
    
    return response

#추가 사항 입력시 행동 지침 출력
@router.post("/MVP/Additional", response_model=List[ActionGuideline])
def get_action_guidelines(
    unfair_clauses: List[UnfairClause],  # 이전 분석 결과 일부 또는 전체 전달
    additional_input: AdditionalNoteInput
):
    guidelines = generate_action_guidelines(unfair_clauses, additional_input)
    return guidelines