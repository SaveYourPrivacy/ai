from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AdditionalNotes.core.AdditionalNotes_chain import (
    generate_action_guidelines,
    parse_question_to_additional_input,
    get_session_memory
)
from AdditionalNotes.schemas.AdditionalNotes_dto import (
    AdditionalNoteInput
)

router = APIRouter(tags=["AdditionalNotes"])

_session_storage: dict = {}

class SimpleRequest(BaseModel):
    session_id: str = Field(..., description="세션 ID")
    question: str = Field(..., description="질문")

class SimpleResponse(BaseModel):
    summary: str

@router.post("/AdditionalNotes", response_model=SimpleResponse)
def get_action_guidelines_simple(request: SimpleRequest):
    session_id = request.session_id
    print(f"🔄 세션: {session_id} | {request.question[:30]}...")
    
    # 1. 세션 초기화
    if session_id not in _session_storage:
        _session_storage[session_id] = {
            "unfair_clauses": [{
                "id": 1,
                "clauseNumber": "제X조",
                "text": "세션 기반 불공정 조항",
                "issues": [{"type": "기본", "description": "약관 문제", "severity": "중간", "relatedLaw": "약관규제법"}]
            }],
            "questions": [],
            "previous_guidelines": []
        }
    
    # 2. 질문 파싱 + LLM 실행
    additional_input = parse_question_to_additional_input(request.question)
    additional_input.session_id = session_id
    
    session_data = _session_storage[session_id]
    unfair_clauses = session_data["unfair_clauses"]
    guidelines = generate_action_guidelines(unfair_clauses, additional_input)
    
    if guidelines and len(guidelines) > 0:
        primary = guidelines[0]
        
        # 핵심만 깔끔하게 추출
        action = primary.recommendation.strip()
        reason = primary.reason.strip()
        
        # 행동과 이유 중복 제거 후 자연스럽게 연결
        if action.lower() in reason.lower():
            # 이유에 행동이 포함되어 있으면 이유만 사용
            summary = reason
        else:
            # 행동 + 이유 자연스럽게 연결
            summary = f"{action} {reason}"
        
        # 마침표만 정리 (중복 제거)
        summary = summary.replace('..', '.').strip()
        if not summary.endswith('.'):
            summary += '.'
        
    else:
        summary = "구체적인 행동 지침을 확인해주세요."
    
    # 3. 세션 업데이트
    session_data["previous_guidelines"] = [
        {"recommendation": g.recommendation, "reason": g.reason} for g in guidelines
    ]
    session_data["questions"].append(request.question)
    
    print(f"요약: {summary}")
    
    return SimpleResponse(summary=summary)