from typing import List
from pydantic import BaseModel, Field

class Case(BaseModel):
    title: str = Field(description="사례 제목")
    summary: str = Field(description="사례 요약")
    url: str = Field(description="출처 링크")

class CaseSearchResponse(BaseModel):
    cases: List[Case] = Field(description="발견된 피해 사례들")

# 새로 추가: 실제 MVP 분석 결과 DTO
class AnalysisIssue(BaseModel):
    type: str = Field(description="문제 유형")
    description: str = Field(description="문제 설명")
    severity: str = Field(description="위험도")
    relatedLaw: str = Field(description="관련 법률")

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

class AnalysisResult(BaseModel):
    summary: AnalysisSummary
    termsSummary: dict = Field(default_factory=dict)
    unfairClauses: List[UnfairClause] = []
    recommendations: List[str] = []

class CaseSearchRequest(BaseModel):
    worstScenario: str = Field(..., description="Company Terms Analyze 응답의 최악의 시나리오 텍스트만 전달")