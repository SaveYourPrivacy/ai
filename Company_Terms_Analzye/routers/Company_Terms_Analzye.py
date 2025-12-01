from fastapi import APIRouter
from Company_Terms_Analzye.schemas.Company_dto import CompanyAnalysisResponse,CompanyAnalysisRequest
from Company_Terms_Analzye.core.Company_chain import company_chain
from Terms_Analyze.core.MVP_rag import get_retriever

router = APIRouter(
    tags=["Company Terms Analyze"]
)

@router.post("/company_terms_analyze", response_model=CompanyAnalysisResponse)
def analyze_company( input: CompanyAnalysisRequest ) -> CompanyAnalysisResponse:
    
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

    chain_input = {
        "term": input.term,
        "law_context": law_context_text
    }
    return company_chain.invoke(chain_input)