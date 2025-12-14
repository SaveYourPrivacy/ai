from typing import List, Optional
from fastapi import APIRouter
import uuid
from pydantic import BaseModel, Field

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

class CombinedRequest(BaseModel):
    analysis_result: NewAnalysisResult
    payload: QuestionPayload
    session_id: Optional[str] = Field(None, description="세션 ID")

@router.post("/AdditionalNotes", response_model=List[ActionGuideline])
def get_action_guidelines_from_question(request: CombinedRequest):
    session_id = request.session_id or str(uuid.uuid4())
    print(f"{'새 세션' if request.session_id is None else '기존 세션'}: {session_id}")
    
    additional_input = parse_question_to_additional_input(request.payload.question)
    additional_input.session_id = session_id  # 동적 할당
    
    unfair_clauses = [clause.model_dump(mode='python') for clause in request.analysis_result.unfairClauses]
    
    guidelines = generate_action_guidelines(unfair_clauses, additional_input)
    
    return guidelines