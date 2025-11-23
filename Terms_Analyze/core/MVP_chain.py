#-------[LangChain Core]--------------------
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_core.output_parsers import JsonOutputParser

from Terms_Analyze.schemas.MVP_dto import TermsResponse
from Terms_Analyze.core.MVP_config import PromptTemplates

#--------------------------------------------
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()
#--------------------------------------------

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
    
    chain = ( # 입력값은 model_dump()가 깔끔하게 딕셔너리를 생성하므로 전처리 필요 X, 이젠 직접 딕셔너리 생성해서 넣음
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

