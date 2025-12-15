from fastapi import APIRouter,UploadFile,Form
import pdfplumber
import uuid
from langchain.memory import ConversationBufferMemory
from Company_Terms_Analzye.schemas.Company_dto import CompanyAnalysisResponse,CompanyAnalysisRequest,sessions
from Company_Terms_Analzye.core.Company_chain import company_chain
from Terms_Analyze.core.MVP_rag import get_retriever

router = APIRouter(
    tags=["Company Terms Analyze"]
)

def extract_pdf(pdf_file: UploadFile) -> str:
    with pdfplumber.open(pdf_file.file) as pdf:
        text = ""
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

@router.post("/company_terms_analyze", response_model=CompanyAnalysisResponse)
def analyze_company( input: CompanyAnalysisRequest ) -> CompanyAnalysisResponse:
    
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

    chain_input = {
        "term": input.term,
        "category": input.category,
        "law_context": law_context_text
    }

    response = company_chain.invoke(chain_input)

    session_id = str(uuid.uuid4())
    memory = ConversationBufferMemory(return_messages=True)

    memory.save_context(
        {"input": f"이것은 방금 분석된 약관의 취약 조항들입니다. \n {response}"},
        {"output": "네, 해당 정보를 바탕으로 요청사항을 도와드리겠습니다."}
    )

    sessions[session_id] = memory
    response.session_id = session_id

    print(memory)

    return response


# PDF 입력
@router.post("/company_terms_analyze/pdf", response_model=CompanyAnalysisResponse)
def analyze_company_from_pdf ( file: UploadFile, 
                              category: str= Form(..., description="집중분석 카테고리")  ) -> CompanyAnalysisResponse:
    
    term_text = extract_pdf(file)
    retriever = get_retriever(category)
    # RAG 생성 실패시 예외처리
    if retriever is None:
        print("경고: 검색기가 준비되지 않았습니다. RAG 없이 일반 분석을 수행합니다.")
        law_context_text = "일반 상식 (법률 데이터 로드 실패)"
    else:
        # 입력 약관으로 법률 DB 검색
        law_context_docs = retriever.invoke(term_text)
        
        # 검색된 문서(docs)들을 하나의 텍스트로 합침
        law_context_text = "\n\n".join([doc.page_content for doc in law_context_docs])

    chain_input = {
        "term": term_text,
        "category": category,
        "law_context": law_context_text
    }
    
    response = company_chain.invoke(chain_input)

    session_id = str(uuid.uuid4())
    memory = ConversationBufferMemory(return_messages=True)

    memory.save_context(
        {"input": f"이것은 방금 분석된 약관의 불공정 조항들입니다. \n {response}"},
        {"output": "네, 해당 정보를 바탕으로 요청사항을 도와드리겠습니다."}
    )

    sessions[session_id] = memory
    response.session_id = session_id

    return response