from fastapi import APIRouter
from CaseSearch.schemas.CaseSearch_dto import (
    CaseSearchResponse, 
    CaseSearchRequest
)
from CaseSearch.core.CaseSearch_chain import generate_cases

router = APIRouter(tags=["CaseSearch"])

@router.post("/CaseSearch/cases", response_model=CaseSearchResponse)
def search_cases(payload: CaseSearchRequest):
    """불공정 약관 + 질문으로 웹 검색 → 피해 사례 반환"""
    cases = generate_cases(payload.analysis_result.dict(), payload.question)
    return cases