from fastapi import APIRouter
from Improvement.schemas.Improvement_dto import ImprovementResponse
from Improvement.core.Improvement_chain import generate_improvements
from Terms_Analyze.schemas.MVP_dto import TermsResponse

router = APIRouter(
    tags=["Improvements"]
)

@router.post("/Improvements", response_model=ImprovementResponse)
def get_improvements(analysis_result: TermsResponse):
    """불공정 약관 분석 결과를 받아 개선안 생성"""
    improvements = generate_improvements(analysis_result.dict())
    return improvements