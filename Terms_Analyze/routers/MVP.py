from typing import List
from fastapi import APIRouter
import uuid
from langchain.memory import ConversationBufferMemory
from Terms_Analyze.schemas.MVP_dto import TermInput, TermsResponse, UnfairClause
from Terms_Analyze.core.MVP_rag import get_retriever
from Terms_Analyze.core.MVP_chain import term_chain
from Terms_Analyze.schemas.MVP_dto import sessions

router = APIRouter(
    tags=["UnfairTerm Analysis"]
)

#-----[ FastAPI ]-----------------------
@router.post("/terms_analyze", response_model=TermsResponse)
def analyze(input: TermInput) -> TermsResponse:
    
    # 수정된 부분: 카테고리 기반 검색기 호출
    # 입력 카테고리는 반드시 '광고', '환불', '개인정보', '책임제한', '자동결제' 중 하나
    retriever = get_retriever(input.category)

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

    session_id = str(uuid.uuid4())
    memory = ConversationBufferMemory(return_messages=True)

    # LLM 호출 및 출력값 반환
    response = term_chain.invoke(chain_input) # response는 parser에 의해 생성된 딕셔너리가 초기화됨.

    memory.save_context(
        {"input":f"이것은 방금 분석된 약관의 불공정 조항들입니다. \n {response}"},
        {"output": "네, 해당 정보를 바탕으로 컴플레인 메일 작성을 도와드리겠습니다."}
    )

    sessions[session_id] = memory
    response["session_id"] = session_id
    
    return response
