from typing import List
from fastapi import APIRouter
from Terms_Analyze.schemas.MVP_dto import UnfairClause
from AdditionalNotes.schemas.AdditionalNotes_dto import ActionGuideline, AdditionalNoteInput

from AdditionalNotes.AdditionalNotes import generate_action_guidelines

router = APIRouter(
    tags=["AdditionalNotes"]
)

#-----[ FastAPI ]-----------------------

#추가 사항 입력시 행동 지침 출력
@router.post("/AdditionalNotes", response_model=List[ActionGuideline])
def get_action_guidelines(
    unfair_clauses: List[UnfairClause],  # 이전 분석 결과 일부 또는 전체 전달
    additional_input: AdditionalNoteInput
):
    guidelines = generate_action_guidelines(unfair_clauses, additional_input)
    return guidelines