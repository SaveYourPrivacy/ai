from typing import List
from pydantic import BaseModel, Field

# 기업용 약관 취약점 분석 DTO

#-------[ Request DTO ]--------------------------------------

class CompanyAnalysisRequest(BaseModel):
    term: str = Field(..., description="분석할 약관 텍스트 원문")

#-------[ Response DTO ]--------------------------------------

class LegalVulnerability(BaseModel):
    clause: str = Field(description="문제가 식별된 약관 조항 원문")
    riskLevel: str = Field(description="법적 리스크 수준 (반드시 '상', '중', '하' 중 하나)")
    relatedLaw: str = Field(description="위반되는 [법률 근거]의 구체적 조항 (예: '약관규제법 제X조')")
    vulnerabilityType: str = Field(description="취약점 유형 (예: '법적 효력 없음', '모호한 표현', '과도한 면책')")
    description: str = Field(description="해당 조항이 왜 법적으로 취약한지 상세 설명")
    suggestion: str = Field(description="리스크를 제거하기 위한 구체적인 수정 제안")

class CompanyAnalysisResponse(BaseModel):
    riskLevel: str = Field(description="약관의 전반적인 법적 위험도 (반드시 '상', '중', '하' 중 하나)")
    summary: str = Field(description="클라이언트 보고용 전체 요약")
    vulnerabilities: List[LegalVulnerability] = Field(description="발견된 법적 취약점 목록")
    worstScenario: str = Field(description="발견된 모든 취약점이 악용되었을 때 발생할 수 있는 종합적이고 구체적인 최악의 사태 (단일 시나리오)")