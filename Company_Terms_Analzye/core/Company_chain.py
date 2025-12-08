from Company_Terms_Analzye.schemas.Company_dto import CompanyAnalysisResponse, LegalVulnerability, InterAnalysis
from Company_Terms_Analzye.core.Company_config import PROMPT_COMPANY_TEXT, PROMPT_WORST_SCENARIO

#-------[LangChain Core]--------------------
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence, RunnableMap
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

#--------------------------------------------
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()
#--------------------------------------------

# 멀티 체인을 위한 체인 2개 생성
# 취약점 분석 후 분석 결과 -> 시나리오 생성 체인 입력 형태

# 취약점 분석 체인
# 정밀한 분석을 위해 자유도 0 설정
analyze_llm = ChatOpenAI(temperature=0.0,model="gpt-4o-mini").bind(
    response_format={"type": "json_object"}
)

# 시나리오 생성 체인
# 창의성을 위해 자유도 0.7 설정
scenario_llm = ChatOpenAI(temperature=0.7,model="gpt-4o-mini")

# 체인 1 취약점 분석 체인 생성
analyze_parser = JsonOutputParser(pydantic_object=InterAnalysis)
analyze_prompt = ChatPromptTemplate.from_template(
    PROMPT_COMPANY_TEXT,
    partial_variables={"format_instructions": analyze_parser.get_format_instructions()}
)

analyze_chain = (
    analyze_prompt
    | analyze_llm
    | analyze_parser
)

# 체인 2 최악의 시나리오 작성 체인 생성
scenario_parser = StrOutputParser()
scenario_prompt = ChatPromptTemplate.from_template(PROMPT_WORST_SCENARIO) # DTO 기반 프롬프트 작성 필요 X

scenario_chain = (
    scenario_prompt
    | scenario_llm
    | scenario_parser
)

# 최종 DTO에 최악의 시나리오 삽입
def combine(input: dict) -> CompanyAnalysisResponse:
    analyze = input["analyze"]
    scenario = input["scenario"]

    return CompanyAnalysisResponse(
        riskLevel=analyze["riskLevel"],
        summary=analyze["summary"],
        vulnerabilities=analyze["vulnerabilities"],
        worstScenario=scenario
    )

company_chain = (
    RunnableMap({
        "analyze": analyze_chain
    })
    | RunnableMap({
        "analyze" : lambda x: x["analyze"],
        "scenario" : (lambda x: {"result": str(x["analyze"])})
        | scenario_chain
    })
    | RunnableLambda(combine)
)