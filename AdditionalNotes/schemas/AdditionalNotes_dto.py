from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


class AdditionalNoteInput(BaseModel):
    situation: str = Field(description="추가 상황 설명 (예: '계약 해지 요청')")
    clause_number: Optional[str] = Field(
        default=None,
        description="관련 약관 조항 번호(Optional)",
    )


class ActionGuideline(BaseModel):
    recommendation: str = Field(description="권장 행동 지침")
    reason: str = Field(description="행동 지침의 이유 또는 법적 근거 설명")
    related_law: str = Field(description="참고할 법률 조항이나 판례")


# 새로운 분석 결과 구조에 맞는 DTO
class AnalysisIssue(BaseModel):
    type: str
    description: str
    severity: str
    relatedLaw: str


class UnfairClause(BaseModel):
    id: int
    clauseNumber: str
    text: str
    issues: List[AnalysisIssue] = []


class AnalysisSummary(BaseModel):
    title: str
    overview: str
    totalClauses: int
    unfairCount: int
    riskLevel: str


class TermsSummary(BaseModel):
    mainPoints: List[str]
    keyRights: List[str]
    keyObligations: List[str]


class NewAnalysisResult(BaseModel):
    summary: AnalysisSummary
    termsSummary: TermsSummary
    unfairClauses: List[UnfairClause]
    recommendations: List[str]


class QuestionPayload(BaseModel):
    question: str