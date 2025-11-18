from enum import Enum
from typing import List

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()

#-------[LangChain Core]--------------------
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_core.output_parsers import JsonOutputParser

#-------[LangChain RAG]--------------------
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from LAW_TEXT import LAW_TEXT

#-----[ FastAPI ]-----------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

retriever = None # RAG 사용을 위해 검색기 retriever 전역변수 선언

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#---------------------------------------------------

# RAG 셋업 함수, FastAPI 구동시 최초 1회 실행
# 텍스트를 임베딩하여 Vector DB에 저장하는 함수
def setup_rag():
    global retriever
    if not LAW_TEXT or "(사용자 작업 필요)" in LAW_TEXT:
        print("경고: LAW_TEXT가 비어있습니다. RAG 기능이 비활성화됩니다.")
        print("법률 URL의 전체 텍스트를 LAW_TEXT 변수에 복사해 주세요.")
        return

    # 1. 텍스트 분할 (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100
    )
    docs = text_splitter.create_documents([LAW_TEXT])
    
    # 2. 임베딩 (Embedding)
    embeddings = OpenAIEmbeddings()
    
    # 3. 벡터 저장소 (Vector Store) - FAISS 사용
    # docs를 임베딩하여 FAISS 벡터 저장소를 생성
    vector_store = FAISS.from_documents(docs, embeddings)
    
    # 4. 검색기 (Retriever) 생성
    # 이 검색기는 k=5 (가장 유사한 5개) 조각을 검색
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    print("RAG 벡터 저장소 및 검색기(Retriever)가 성공적으로 준비되었습니다.")

# FastAPI 구동시 RAG 셋업을 최초 1회 실행
@app.on_event("startup")
def on_startup():
    setup_rag()

#-------[ DTO ]--------------------------------------
# (추가학습) Field(description=) 을 통해 각 스키마의 주석을 추가하고
#           LLM이 스키마에 데이터를 초기화할 때, 주석을 참고하게 하여 초기화할 데이터의 형식을 지정할 수 있다. 
class TermInput(BaseModel): # Post 요청을 전달하는 DTO
    term: str # 입력 약관
    category: str = Field(description="약관의 종류 (예: '환불 및 해지 조항')") # 응답 향상을 위한 약관 종류

class UnfairClause(BaseModel): # 각 불공정 약관 구절과 이유를 묶어 List에 초기화하기 위한 컨테이너 클래스
    clause: str = Field(description="불공정으로 판별된 약관 구절")
    # (RAG 수정) '일반 상식'이 아닌 '법률 조항 위반 근거'로 수정
    reason: str = Field(description="해당 구절이 불공정한 이유 (반드시 법률 조항 위반 근거 포함)")

class TermsResponse(BaseModel): # 분석기의 처리결과를 반환하는 DTO
    isUnFair: bool = Field(description="약관에 불공정한 내용이 포함되어 있는지 여부")
    summary: str = Field(description="입력된 약관 내용의 핵심 요약")
    unfairClauses: List[UnfairClause] = Field(description="불공정 약관 구절 및 그 사유 목록")
#---------------------------------------------------------

class PromptTemplates(str, Enum):
    TERM = """
    당신은 대한민국 '약관의 규제에 관한 법률' 전문가 AI입니다.
    사용자가 [약관 텍스트]를 입력했습니다.

    당신은 당신의 일반 상식이 아닌, **반드시 아래 제공된 [법률 근거]**를 바탕으로
    [약관 텍스트]를 정밀하게 분석해야 합니다.

    특히 이 약관은 '{category}' 유형에 대한 내용입니다.
    이 분야와 관련된 [법률 근거]에 초점을 맞추어 더 정밀하게 분석하십시오.

    1. [약관 텍스트]의 핵심 내용을 요약합니다. (summary)
    2. [법률 근거]에 비추어 볼 때, [약관 텍스트]에 불공정 의심 조항이 포함되어 있는지 판단합니다. (isUnfair)
    3. 불공정 의심 조항이 있다면, 해당 [구절](clause)과 [이유](reason)를 찾아 리스트로 만듭니다.
       [이유]에는 반드시 위반되는 [법률 근거]의 조항(예: '약관규제법 제X조')을 인용해야 합니다.
       (불공정 조항이 없다면 빈 리스트 []를 반환합니다.)

    ---
    [법률 근거]:
    {law_context}
    ---
    [분석 초점]:
    {category}
    ---
    [약관 텍스트]:
    {term}
    ---

    [출력 지시]:
    당신의 응답은 반드시 JSON 형식이어야 하며, 다음 스키마를 준수해야 합니다.
    {format_instructions}
    """

# (추가학습) - bind() 를 사용하여 LLM의 반환 형태를 JSON 형태로 고정
term_llm = ChatOpenAI(temperature=0.1, model="gpt-4o-mini").bind(
    response_format={"type": "json_object"}
)

# (추가학습) - 파서 생성, LLM의 출력결과를 선언한 JSON (TermsResponse) 형태의 딕셔너리로 변환해줌
parser = JsonOutputParser(pydantic_object=TermsResponse)

# (추가학습) - 프롬프트를 생성, 생성시에 partial_variables를 이용하여 "format_instructions"에 get_format_instructions( )가
#              반환 객체의 Field(description=)을 참고하여 작성한 출력 예시가 반환함. 
term_prompt = ChatPromptTemplate.from_template(
    PromptTemplates.TERM,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

def get_llm_chain(
        llm: ChatOpenAI, 
        prompt: ChatPromptTemplate, 
        parser: JsonOutputParser
) -> RunnableSequence:
    
    chain = ( # 입력값은 model_dump()가 깔끔하게 딕셔너리를 생성하므로 전처리 필요 X
        prompt
        | llm
        | parser  # 출력값을 TermsResponse JSON형태의 딕셔너리로 반환, 때문에 출력값 전처리도 필요 X
    )
    return chain

term_chain = get_llm_chain(
    term_llm,
    term_prompt,
    parser
)


#-----[ FastAPI ]-----------------------
@app.post("/MVP", response_model=TermsResponse)
def analyze(input: TermInput) -> TermsResponse:
    
    global retriever
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