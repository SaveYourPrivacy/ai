from typing import List
from pydantic import BaseModel, Field

#-------[ DTO ]--------------------------------------
# (추가학습) Field(description=) 을 통해 각 스키마의 주석을 추가하고
#           LLM이 스키마에 데이터를 초기화할 때, 주석을 참고하게 하여 초기화할 데이터의 형식을 지정할 수 있다. 
class TermInput(BaseModel): # Post 요청을 전달하는 DTO
    term: str # 입력 약관
    category: str = Field(description="약관의 종류 (예: '환불 및 해지 조항')") # 응답 향상을 위한 약관 종류

class AnalysisSummary(BaseModel): # 최종 DTO의 첫 요소, 분석 약관 요약 및 평가
    title: str = Field(description="분석 보고서의 제목 (예: '약관 분석 요약')")
    overview: str = Field(description="전체적인 분석 결과에 대한 한 줄 요약(예: 총 6개의 조항 중 3개의 조항에서 소비자에게 불리한 불공정 조항이 발견되었습니다.)")
    totalClauses: int = Field(description="분석한 약관의 총 조항 수")
    unfairCount: int = Field(description="발견된 불공정 조항의 개수")
    riskLevel: str = Field(description="약관의 전체적인 위험도 (예: '높음', '중간', '낮음')")
class TermsSummary(BaseModel): # 최종 DTO의 두번째 요소, 약관의 상세요약, 사용자 핵심 권리, 사용자 핵심 의무
    mainPoints: List[str] = Field(description="약관의 주요 내용 요약 리스트 (3개 내외)")
    keyRights: List[str] = Field(description="사용자가 가지는 핵심 권리 요약 리스트")
    keyObligations: List[str] = Field(description="사용자가 부담하는 핵심 의무 요약 리스트")

# RAG를 이용하여 법률 조항 위반 근거를 작성하게 함
class Issue(BaseModel): # UnfairClause 객체 속 문제점 항목의 세부 요소, 컨테이너 클래스
    type: str = Field(description="불공정 이슈의 유형 (예: '절차 위반', '개인정보 침해', '면책 조항 과다')")
    description: str = Field(description="해당 이슈가 왜 문제인지에 대한 상세 설명")
    severity: str = Field(description="이슈의 심각도 (예: '상', '중', '하')")
    relatedLaw: str = Field(description="위반되는 [법률 근거]의 구체적 조항 (예: '약관규제법 제X조')")

# 최종 DTO의 세번째 요소, 불공정 약관 구절별 상세
class UnfairClause(BaseModel): # 각 불공정 약관 구절과 이유를 묶어 List에 초기화하기 위한 컨테이너 클래스
    id: int = Field(description="식별 ID (1부터 시작)")
    clauseNumber: str = Field(description="해당 조항의 번호 (예: '제3조 제1항')")
    text: str = Field(description="문제가 되는 약관의 원문 텍스트")
    issues: List[Issue] = Field(description="해당 조항에서 발견된 문제점들의 리스트")

class TermsResponse(BaseModel): # 분석기의 처리결과를 최종 반환하는 DTO
    summary: AnalysisSummary = Field(description="전체 분석 요약 정보")
    termsSummary: TermsSummary = Field(description="약관 상세 내용 요약 (주요점, 권리, 의무)")
    unfairClauses: List[UnfairClause] = Field(description="발견된 불공정 조항 목록")
    recommendations: List[str] = Field(description="사용자 또는 기업에게 제안하는 개선 사항 또는 행동 지침 리스트")
    
