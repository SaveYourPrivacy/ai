from typing import List
from pydantic import BaseModel, Field

#-------[ DTO ]--------------------------------------
# (추가학습) Field(description=) 을 통해 각 스키마의 주석을 추가하고
#           LLM이 스키마에 데이터를 초기화할 때, 주석을 참고하게 하여 초기화할 데이터의 형식을 지정할 수 있다. 
class TermInput(BaseModel): # Post 요청을 전달하는 DTO
    term: str # 입력 약관
    category: str = Field(description="약관의 종류 (예: '환불 및 해지 조항')") # 응답 향상을 위한 약관 종류

class UnfairClause(BaseModel): # 각 불공정 약관 구절과 이유를 묶어 List에 초기화하기 위한 컨테이너 클래스
    clause: str = Field(description="불공정으로 판별된 약관 구절")
    # RAG를 이용하여 법률 조항 위반 근거를 작성하게 함
    reason: str = Field(description="해당 구절이 불공정한 이유 (반드시 법률 조항 위반 근거 포함)")

class TermsResponse(BaseModel): # 분석기의 처리결과를 반환하는 DTO
    isUnFair: bool = Field(description="약관에 불공정한 내용이 포함되어 있는지 여부")
    summary: str = Field(description="입력된 약관 내용의 핵심 요약")
    unfairClauses: List[UnfairClause] = Field(description="불공정 약관 구절 및 그 사유 목록")