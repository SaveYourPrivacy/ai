from typing import List
from pydantic import BaseModel, Field

# 기업용 약관 취약점 분석 DTO

#-------[ Request DTO ]--------------------------------------

class CompanyAnalysisRequest(BaseModel):
    term: str = Field(..., description="분석할 약관 텍스트 원문")
    category: str = Field(description="약관의 종류 (예: '환불', '광고', '개인정보')")

#-------[ Response DTO ]--------------------------------------
# class LegalVulnerability(BaseModel):
#     clause: str = Field(description="문제가 식별된 약관 조항 원문")
#     riskLevel: str = Field(description="법적 리스크 수준 (반드시 '높음', '중간', '낮음' 중 하나)")
#     relatedLaw: str = Field(description="위반되는 [법률 근거]의 구체적 조항 (예: '약관규제법 제X조')")
#     vulnerabilityType: str = Field(description="취약점 유형 (예: '법적 효력 없음', '모호한 표현', '과도한 면책')")
#     description: str = Field(description="해당 조항이 왜 법적으로 취약한지 상세 설명")
#     suggestion: str = Field(description="리스크를 제거하기 위한 구체적인 수정 제안")

# class CompanyAnalysisResponse(BaseModel):
#     riskLevel: str = Field(description="약관의 전반적인 법적 위험도 (반드시 '높음', '중간', '낮음' 중 하나)")
#     summary: str = Field(description="클라이언트 보고용 전체 요약")
#     vulnerabilities: List[LegalVulnerability] = Field(description="발견된 법적 취약점 목록")
#     worstScenario: str = Field(description="발견된 모든 취약점이 악용되었을 때 발생할 수 있는 종합적이고 구체적인 최악의 사태 (단일 시나리오)")

# class InterAnalysis(BaseModel): # 멀티 체인용 dto
#     riskLevel: str = Field(description="약관의 전반적인 법적 위험도")
#     summary: str = Field(description="클라이언트 보고용 전체 요약")
#     vulnerabilities: List[LegalVulnerability] = Field(description="발견된 법적 취약점 목록")

    #=======================
#
#-------[ Response DTO ]-------------------------------------- 불공정 약관 분석과 형태 통일
class CompanyAnalysisSummary(BaseModel):
    title: str = Field(description="보고서 제목 (예: '기업 약관 취약점 진단 보고서')")
    overview: str = Field(description="전체적인 분석 결과에 대한 한 줄 요약(예: 총 6개의 조항 중 3개의 조항에서 악용가능성이 있는 취약 조항이 발견되었습니다.)")
    totalClauses: int = Field(description="분석한 약관의 총 조항 수")
    vulnerabilityCount: int = Field(description="발견된 취약 조항의 개수")
    riskLevel: str = Field(description="약관의 전체적인 위험도 (예: '높음', '중간', '낮음')")
class CompanyTermsSummary(BaseModel):
    mainPoints: List[str] = Field(description="약관의 주요 내용 요약 리스트 (3개 내외)")
    keyRights: List[str] = Field(description="기업이 보유한 핵심 권한 요약 리스트")
    keyObligations: List[str] = Field(description="기업이 져야 할 법적 의무 요약 리스트")
class Issue(BaseModel):
    riskType: str = Field(description="취약점 유형 (예: '법적 효력 없음', '규제 위반', '모호한 조항')") 
    description: str = Field(description="해당 조항이 왜 법적으로 취약한지 상세 설명")
    severity: str = Field(description="리스크 심각도 (예: '높음', '중간', '낮음')")
    relatedLaw: str = Field(description="위반 소지가 있는 [법률 근거]의 구체적 조항 (예: '약관규제법 제X조')")
class VulnerableClause(BaseModel):
    id: int = Field(description="식별 ID (1부터 시작)")
    clauseNumber: str = Field(description="해당 취약 조항 번호 (예: '제3조 제1항')")
    text: str = Field(description="취약점이 발견된 약관의 조항 원문")
    issues: List[Issue] = Field(description="해당 조항의 법적 리스크(취약점)들의 리스트") 

# [최종 반환 DTO]
class CompanyAnalysisResponse(BaseModel):
    summary: CompanyAnalysisSummary = Field(description="전체 약관 분석 요약 정보")
    termsSummary: CompanyTermsSummary = Field(description="약관 상세 내용 요약 (주요점, 권한, 의무)")
    vulnerabilities: List[VulnerableClause] = Field(description="발견된 법적 취약점 조항 목록") 
    recommendations: List[str] = Field(description="기업에게 제안하는 리스크 제거를 위한 구체적인 수정 제안 리스트")
    worstScenario: str = Field(description="발견된 모든 취약점이 악용되었을 때 발생할 수 있는 종합적이고 구체적인 최악의 사태 (단일 시나리오)") # session_id 대응

# [멀티 체인용 중간 DTO] =========================================================
# worstScenario 생성을 위해 먼저 추출할 데이터 구조
class InterAnalysis(BaseModel):
    summary: CompanyAnalysisSummary
    termsSummary: CompanyTermsSummary
    vulnerabilities: List[VulnerableClause]
    recommendations: List[str]