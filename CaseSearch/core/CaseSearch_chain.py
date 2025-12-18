from dotenv import load_dotenv
load_dotenv()

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from CaseSearch.schemas.CaseSearch_dto import CaseSearchResponse
from CaseSearch.core.CaseSearch_config import CASESEARCH

search = DuckDuckGoSearchAPIWrapper()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1).bind(
    response_format={"type": "json_object"}
)

parser = JsonOutputParser(pydantic_object=CaseSearchResponse)
prompt = ChatPromptTemplate.from_template(
    CASESEARCH,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

case_chain = prompt | llm | parser


def generate_cases(worst_scenario: str) -> CaseSearchResponse:
    # worst_scenario 내용을 일부 잘라서 검색 쿼리 생성
    base = worst_scenario.replace("\n", " ")[:80]
    search_query = f'"불공정 약관 피해 사례" {base}'

    try:
        # 문자열 말고 구조화된 결과 받기
        results = search.results(search_query, max_results=5)
    except Exception as e:
        return CaseSearchResponse(cases=[])

    # LLM에 넘길 때는 리스트 그대로 문자열화해서 전달
    result_dict = case_chain.invoke({
        "search_results": results,
        "worst_scenario": worst_scenario,
    })

    return CaseSearchResponse(**result_dict)