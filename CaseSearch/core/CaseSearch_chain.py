from dotenv import load_dotenv
load_dotenv()

from langchain_google_community import GoogleSearchAPIWrapper
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from CaseSearch.schemas.CaseSearch_dto import CaseSearchResponse
from CaseSearch.core.CaseSearch_config import CASESEARCH
import os

# 구글 검색 래퍼 초기화
search = GoogleSearchAPIWrapper(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    google_cse_id=os.getenv("GOOGLE_CSE_ID")
)

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
    # worst_scenario에서 핵심 키워드 추출하여 검색 쿼리 생성
    base = worst_scenario.replace("\n", " ").strip()

    # 시나리오가 너무 길면 핵심만 추출 (첫 100자 정도)
    if len(base) > 100:
        base = base[:100]

    search_queries = [
        # 일반 피해 사례 검색
        f'{base} 피해사례',
        # 소비자 피해 검색
        f'{base} 소비자 피해',
        # 판결/소송 관련
        f'{base} 판결',
        # 약관 관련 분쟁
        f'불공정 약관 {base}',
        # 뉴스 검색
        f'{base} 사건 뉴스',
    ]

    all_results = []
    for query in search_queries:
        try:
            results = search.results(query, num_results=5)
            if results:
                all_results.extend(results)
        except Exception as e:
            print(f"검색 실패: {type(e).__name__}: {str(e)}")
            continue

    if not all_results:
        return CaseSearchResponse(cases=[])

    # 중복 제거 (같은 URL)
    seen_urls = set()
    unique_results = []
    for r in all_results:
        url = r.get('link') or r.get('url')
        if url and url not in seen_urls:
            seen_urls.add(url)
            # 구글 검색 결과 형식 통일
            unique_results.append({
                'title': r.get('title', ''),
                'snippet': r.get('snippet', ''),
                'link': url
            })

    # 최대 10개까지만 전달
    unique_results = unique_results[:10]

    result_dict = case_chain.invoke({
        "search_results": unique_results,
        "worst_scenario": worst_scenario,
    })

    return CaseSearchResponse(**result_dict)