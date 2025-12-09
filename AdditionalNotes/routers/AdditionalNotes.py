from typing import List
from fastapi import APIRouter

from AdditionalNotes.core.AdditionalNotes_chain import (
    generate_action_guidelines,
    parse_question_to_additional_input,
)
from AdditionalNotes.schemas.AdditionalNotes_dto import (
    ActionGuideline,
    NewAnalysisResult,
    QuestionPayload,
)

router = APIRouter(tags=["AdditionalNotes"])


@router.post("/AdditionalNotes/guidelines-from-question", response_model=List[ActionGuideline])
def get_action_guidelines_from_question(
    analysis_result: NewAnalysisResult,
    payload: QuestionPayload,
):
    """자연어 질문 + 분석 결과 → 행동 지침"""
    # 1) 질문 파싱
    additional_input = parse_question_to_additional_input(payload.question)
    
    # 2) unfair_clauses 추출 (Pydantic → dict)
    unfair_clauses = [clause.model_dump() for clause in analysis_result.unfairClauses]
    
    # 3) 지침 생성
    guidelines = generate_action_guidelines(unfair_clauses, additional_input)
    return guidelines