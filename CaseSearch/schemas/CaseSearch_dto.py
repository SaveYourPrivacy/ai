from typing import List
from pydantic import BaseModel, Field

# 기존 CaseSearch DTO들
class Case(BaseModel):
    case_title: str = Field(description="사례 제목")
    summary: str = Field(description="사례 요약")
    related_clause: str = Field(description="관련 불공정 조항")
    outcome: str = Field(description="사례 결과")
    source_url: str = Field(description="출처 링크")

class CaseSearchResponse(BaseModel):
    cases: List[Case] = Field(description="발견된 피해 사례들")
    search_query: str = Field(description="실제 검색된 쿼리")
    total_results: int = Field(description="검색된 사례 수")

# ✅ 새로 추가: 실제 MVP 분석 결과 DTO
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
    analysis_result: AnalysisResult = Field(..., description="MVP/analyze 결과")
    category: str = Field(default="B2C", description="계약 유형")
    question: str = Field(..., description="피해 사례 검색 질문")