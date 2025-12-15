from fastapi import APIRouter
from pydantic import BaseModel, Field
from CaseSearch.schemas.CaseSearch_dto import CaseSearchResponse
from CaseSearch.core.CaseSearch_chain import generate_cases

router = APIRouter(tags=["CaseSearch"])

class CaseSearchRequest(BaseModel):
    worstScenario: str = Field(..., description="Company Terms Analyze의 worstScenario 텍스트")

@router.post("/CaseSearch/cases", response_model=CaseSearchResponse)
def search_cases(payload: CaseSearchRequest):
    """worstScenario만으로 웹 피해 사례 검색 (실제 검색 URL 사용)"""
    cases = generate_cases(payload.worstScenario)
    return cases