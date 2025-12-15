from typing import List, Optional
from pydantic import BaseModel, Field


class AdditionalNoteInput(BaseModel):
    situation: str = Field(description="추가 상황 설명 (예: '계약 해지 요청')")
    clause_number: Optional[str] = Field(
        default=None,
        description="관련 약관 조항 번호(Optional)",
    )
    session_id: Optional[str] = Field(None, description="세션 ID (옵션)")


class ActionGuideline(BaseModel):
    recommendation: str = Field(description="권장 행동 지침")


# Terms_Analyze 결과 구조
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


class TermsAnalyzeResult(BaseModel):
    """/terms_analyze 응답 그대로 (session_id 포함)"""
    summary: AnalysisSummary
    termsSummary: TermsSummary
    unfairClauses: List[UnfairClause]
    recommendations: List[str]
    session_id: str


class NotesFromTermsRequest(BaseModel):
    """Terms_Analyze 결과 + 사용자 질문"""
    summary: AnalysisSummary
    termsSummary: TermsSummary
    unfairClauses: List[UnfairClause]
    recommendations: List[str]
    session_id: str
    question: str = Field(..., description="사용자 질문 (추가 행동 지침이 필요한 상황 설명)")


class SummaryResponse(BaseModel):
    summary: str = Field(..., description="행동 지침 요약 문장")