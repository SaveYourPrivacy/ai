from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from AdditionalNotes.core.AdditionalNotes_config import BASE_GUIDELINES
from AdditionalNotes.schemas.AdditionalNotes_dto import (
    AdditionalNoteInput,
    ActionGuideline,
)


_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _build_related_law_text(matched_clause: Dict[str, Any]) -> str:
    """불공정 조항에서 관련 법령 텍스트 추출"""
    issues = matched_clause.get("issues") or []
    if not isinstance(issues, list):
        return "약관규제법 등 관련 법령"

    related_laws: List[str] = []
    for issue in issues:
        if isinstance(issue, dict):
            law = issue.get("relatedLaw")
            if isinstance(law, str) and law:
                related_laws.append(law)

    return ", ".join(related_laws) if related_laws else "약관규제법 등 관련 법령"


def _find_matched_clause(
    unfair_clauses: List[Dict[str, Any]],
    clause_num: Optional[str],
) -> Optional[Dict[str, Any]]:
    """불공정 조항에서 특정 조항 번호 찾기"""
    if not clause_num:
        return None

    for clause in unfair_clauses:
        if isinstance(clause, dict) and clause.get("clauseNumber") == clause_num:
            return clause
    return None


def generate_action_guidelines(
    unfair_clauses: List[Dict[str, Any]],
    additional_input: AdditionalNoteInput,
) -> List[ActionGuideline]:
    """
    불공정 약관 + 추가 상황 → 행동 지침 생성
    """
    guidelines: List[ActionGuideline] = []
    situation = additional_input.situation
    clause_num = additional_input.clause_number

    # 1) 기본 매핑 우선
    if situation in BASE_GUIDELINES:
        guidelines.append(
            ActionGuideline(
                recommendation=BASE_GUIDELINES[situation],
                reason="해당 상황에 대해 일반적으로 권장되는 행동 지침입니다.",
                related_law="약관규제법 및 관련 소비자 보호법 규정 참조",
            )
        )
        return guidelines

    # 2) 특정 조항 매칭
    matched_clause = _find_matched_clause(unfair_clauses, clause_num)
    if matched_clause:
        related_law_text = _build_related_law_text(matched_clause)
        guidelines.append(
            ActionGuideline(
                recommendation=f"조항 {clause_num} 관련 법률 상담 및 공정거래위원회 신고 준비",
                reason="해당 조항이 불공정으로 분석됨",
                related_law=related_law_text,
            )
        )
        return guidelines

    # 3) 기본 지침
    guidelines.append(
        ActionGuideline(
            recommendation="공정거래위원회 신고 및 법률 상담 권장",
            reason="일반적인 불공정 약관 대응 지침",
            related_law="약관규제법 등 관련 법령",
        )
    )
    return guidelines


def _get_extractor_chain():
    """자연어 → AdditionalNoteInput 변환 체인"""
    parser = JsonOutputParser(pydantic_object=AdditionalNoteInput)
    
    prompt = ChatPromptTemplate.from_template(
        """
        사용자의 질문에서 아래 두 정보를 정확히 뽑으세요:

        - situation: 행동 유형 ('계약 해지 요청', '피해 신고', '면책 조항 과다', '개인정보 침해')
        - clause_number: 조항 번호 ('제5조 2항', '제 10조', 없으면 null)

        JSON 형식으로만 출력:
        {format_instructions}

        질문: {question}
        """
    ).partial(format_instructions=parser.get_format_instructions())

    return prompt | _llm | parser


def parse_question_to_additional_input(question: str) -> AdditionalNoteInput:
    """질문 파싱 + dict → Pydantic 변환"""
    try:
        chain = _get_extractor_chain()
        result_dict = chain.invoke({"question": question})
        additional_input = AdditionalNoteInput.model_validate(result_dict)
        return additional_input
    except Exception as e:
        print(f"[ERROR] Question parsing failed: {e}")
        return AdditionalNoteInput(situation="일반 상담", clause_number=None)