from typing import List, Dict, Any
from pydantic import BaseModel, Field


# 추가 상황 입력 DTO 예시
class AdditionalNoteInput(BaseModel):
    situation: str = Field(description="추가 상황 설명 (예: '계약 해지 요청')")
    clause_number: str = Field(default=None, description="관련 약관 조항 번호(Optional)")


# 행동 지침 출력 DTO 예시
class ActionGuideline(BaseModel):
    recommendation: str = Field(description="권장 행동 지침")
    reason: str = Field(description="행동 지침의 이유 또는 법적 근거 설명")
    related_law: str = Field(description="참고할 법률 조항이나 판례")


# 기본 행동 지침 매핑 예시
BASE_GUIDELINES = {
    "계약 해지 요청": "계약 해지 의사를 서면으로 명확히 전달하고, 필요한 경우 법률 상담을 권장합니다.",
    "피해 신고": "소비자 보호원이나 공정거래위원회에 피해 신고를 접수하세요.",
    "면책 조항 과다": "면책 조항이 과도한 경우 공정거래위원회에 시정을 요구할 수 있습니다.",
    "개인정보 침해": "개인정보 보호위원회 등에 신고하고, 개인정보 보호 관련 법률을 확인하세요.",
}


def generate_action_guidelines(
    unfair_clauses: List[Dict[str, Any]], 
    additional_input: AdditionalNoteInput
) -> List[ActionGuideline]:
    guidelines = []

    situation = additional_input.situation
    clause_num = additional_input.clause_number

    # 예외 케이스 처리 및 기본 매핑 활용
    if situation in BASE_GUIDELINES:
        recommendation = BASE_GUIDELINES[situation]
        reason = "해당 상황에 대해 일반적으로 권장되는 행동 지침입니다."
        related_law = "약관규제법 및 관련 소비자 보호법 규정 참조"
        guidelines.append(
            ActionGuideline(recommendation=recommendation, reason=reason, related_law=related_law)
        )
    else:
        # 추가 분석 기반 맞춤 지침
        matched_clause = None
        for clause in unfair_clauses:
            if clause_num and clause.clauseNumber == clause_num:
                matched_clause = clause
                break

        if matched_clause:
            recommendation = f"조항 {clause_num} 관련하여 법률 상담 및 공정위 신고를 준비하세요."
            reason = "해당 조항이 불공정 조항으로 분석되어, 추가 조치가 필요합니다."
            related_law = ", ".join([issue["relatedLaw"] for issue in matched_clause["issues"]])
            guidelines.append(
                ActionGuideline(recommendation=recommendation, reason=reason, related_law=related_law)
            )
        else:
            # 디폴트 지침
            recommendation = "분석된 불공정 약관에 대해 공정거래위원회 신고 및 법률 상담을 권장합니다."
            reason = "추가 상황이 명확하지 않거나 특정 조항과 매칭되지 않아 일반 지침을 제공합니다."
            related_law = "약관규제법 등 관련 법령"
            guidelines.append(
                ActionGuideline(recommendation=recommendation, reason=reason, related_law=related_law)
            )

    return guidelines