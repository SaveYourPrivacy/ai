from enum import Enum
from typing import List

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()

#-------[LangChain]--------------------
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import JsonOutputParser

#-----[ FastAPI ]-----------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#---------------------------------------------------

#-------[ DTO ]--------------------------------------
# (추가학습) Field(description=) 을 통해 각 스키마의 주석을 추가하고
#           LLM이 스키마에 데이터를 초기화할 때, 주석을 참고하게 하여 초기화할 데이터의 형식을 지정할 수 있다. 
class TermInput(BaseModel): # Post 요청을 전달하는 DTO
    term: str # 입력 약관
    category: str = Field(description="약관의 종류 (예: '환불 및 해지 조항')") # 응답 향상을 위한 약관 종류

class UnfairClause(BaseModel): # 각 불공정 약관 구절과 이유를 묶어 List에 초기화하기 위한 컨테이너 클래스
    clause: str = Field(description="불공정으로 판별된 약관 구절")
    reason: str = Field(description="해당 구절이 불공정한 이유 (LLM의 일반 지식 기반)")

class TermsResponse(BaseModel): # 분석기의 처리결과를 반환하는 DTO
    isUnfair: bool = Field(description="약관에 불공정한 내용이 포함되어 있는지 여부")
    summary: str = Field(description="입력된 약관 내용의 핵심 요약")
    unfairClauses: List[UnfairClause] = Field(description="불공정 약관 구절 및 그 사유 목록")
#---------------------------------------------------------

class PromptTemplates(str, Enum):
    TERM = """
    당신은 대한민국 법률에 기반하여 약관을 분석하는 AI입니다.
    사용자가 [약관 텍스트]를 입력했습니다.

    특히 이 약관은 '{category}' 유형에 대한 내용입니다.
    이 분야에 초점을 맞추어 더 정밀하게 분석하십시오.

    1. [약관 텍스트]의 핵심 내용을 요약합니다. (summary)
    2. [약관 텍스트]에 사용자에게 불리해 보이는 '불공정 의심 조항'이 포함되어 있는지
       당신의 일반 상식선에서 판단합니다. (isUnfair)
    3. 불공정 의심 조항이 있다면, 해당 [구절](clause)과 [이유](reason)를 찾아 리스트로 만듭니다.
       (불공정 조항이 없다면 빈 리스트 []를 반환합니다.)

    [분석 초점]:
    {category}
    
    [약관 텍스트]:
    {term}

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
        parser: JsonOutputParser):
    
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
    
    # input.model_dump()가 TermInput 형태의 딕셔너리를 생성
    request = input.model_dump()
    
    response = term_chain.invoke(request) # response는 parser에 의해 생성된 딕셔너리가 초기화됨.
    
    return response


## TEST