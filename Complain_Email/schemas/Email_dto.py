from typing import List
from pydantic import BaseModel, Field

from Terms_Analyze.schemas.MVP_dto import UnfairClause

# 컴플레인 메일 생성 DTO

#-------[ Request DTO ]--------------------------------------
class ComplaintRequest(BaseModel):
    serviceName: str = Field(description="서비스 또는 기업명")
    unfairClauses: List[UnfairClause] = Field(description="발견된 불공정 조항 목록")
    userSituation: str = Field(description="사용자의 구체적 피해 상황")
    desiredOutcome: str = Field(description="사용자가 원하는 결과")

#-------[ Response DTO ]--------------------------------------
class ComplaintResponse(BaseModel):
    title: str = Field(description="이메일 제목")
    recipient: str = Field(description="수신자")
    content: str = Field(description="이메일 본문")
    keyLegalList: List[str] = Field(description="핵심 법적 근거 리스트")