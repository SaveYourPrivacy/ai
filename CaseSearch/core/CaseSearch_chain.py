from dotenv import load_dotenv
load_dotenv()

#DuckDuckGo 무료 검색 (API 키 필요 없음!)
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from CaseSearch.schemas.CaseSearch_dto import CaseSearchResponse
from CaseSearch.core.CaseSearch_config import CASESEARCH

#무료 Google 검색 대체 (DuckDuckGo)
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

def generate_cases(analysis_result: dict, question: str) -> CaseSearchResponse:
    category = analysis_result.get("category", "B2C")
    search_query = f'"{category}" 불공정 약관 피해 사례 판례 {question}'

    try:
        search_results = search.run(search_query)
    except Exception as e:
        print(f"검색 실패: {e}")
        return CaseSearchResponse(
            cases=[],
            search_query=search_query,
            total_results=0,
        )

    result_dict = case_chain.invoke({
        "search_results": search_results,
        "analysis_result": analysis_result,
        "question": question,
    })

    response = CaseSearchResponse(**result_dict)

    return response