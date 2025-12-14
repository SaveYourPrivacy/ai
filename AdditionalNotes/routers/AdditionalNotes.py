from typing import List, Optional
from fastapi import APIRouter, HTTPException
import uuid
from pydantic import BaseModel, Field

from AdditionalNotes.core.AdditionalNotes_chain import (
    generate_action_guidelines,
    parse_question_to_additional_input,
    get_session_memory
)
from AdditionalNotes.schemas.AdditionalNotes_dto import (
    ActionGuideline,
    AdditionalNoteInput
)

router = APIRouter(tags=["AdditionalNotes"])

# 전역 세션 저장소 (분석 결과 + 대화 기록)
_session_storage: dict = {}

# 단일 Request: session_id + question만!
class SimpleRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="세션 ID (없으면 자동 생성)")
    question: str = Field(..., description="질문")

@router.post("/AdditionalNotes", response_model=List[ActionGuideline])
def get_action_guidelines_simple(request: SimpleRequest):
    """통합 API: session_id + 질문만으로 모든 처리!"""
    
    # 1. 세션 ID 처리
    session_id = request.session_id or str(uuid.uuid4())
    print(f"{'🆕 새 세션' if request.session_id is None else '🔄 기존 세션'}: {session_id}")
    
    # 2. 질문 파싱
    additional_input = parse_question_to_additional_input(request.question)
    additional_input.session_id = session_id
    
    # 3. 세션 데이터 확인
    session_data = _session_storage.get(session_id, {})
    
    # 4. 분석 결과 자동 처리
    if "unfair_clauses" not in session_data or not session_data["unfair_clauses"]:
        print("⚠️ 분석 결과 없음 → 기본 불공정 조항 사용")
        # 기본 불공정 조항 (실제로는 약관 분석 API와 연동)
        unfair_clauses = [{
            "id": 1,
            "clauseNumber": "제X조",
            "text": "기본 불공정 조항 예시 (사용자 상황에 맞게 조정)",
            "issues": [{
                "type": "불공정 조항",
                "description": f"{additional_input.situation} 관련 기본 문제",
                "severity": "중간",
                "relatedLaw": "약관규제법"
            }]
        }]
        
        # 세션에 저장 (다음부터 재사용)
        _session_storage[session_id] = {
            "unfair_clauses": unfair_clauses,
            "questions": []
        }
    else:
        print("이전 분석 결과 재사용")
        unfair_clauses = session_data["unfair_clauses"]
    
    print(f"📝 상황: {additional_input.situation}")
    
    # 5. Memory + LLM 실행
    guidelines = generate_action_guidelines(unfair_clauses, additional_input)
    
    # 6. 대화 기록 업데이트
    if session_id in _session_storage:
        _session_storage[session_id]["questions"].append(request.question)
    
    return guidelines