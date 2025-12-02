from typing import Optional
from pydantic import BaseModel, Field

#-------[ Request DTO ]--------------------------------------
class AdditionalNoteInput(BaseModel):
    situation: str = Field(description="추가 상황 설명 (예: '계약 해지 요청')")
    clause_number: Optional[str] = Field(default=None, description="관련 약관 조항 번호(Optional)")


#-------[ Response DTO ]--------------------------------------

#추가 사항에 대한 행동 지침 출력
class ActionGuideline(BaseModel):
    recommendation: str = Field(description="권장 행동 지침")
    reason: str = Field(description="행동 지침의 이유 또는 법적 근거 설명")
    related_law: str = Field(description="참고할 법률 조항이나 판례")