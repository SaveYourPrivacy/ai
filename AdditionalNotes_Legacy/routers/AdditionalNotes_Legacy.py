from typing import List
from fastapi import APIRouter, HTTPException

from AdditionalNotes_Legacy.core.AdditionalNotes_chain import generate_action_guidelines
from AdditionalNotes_Legacy.schemas.AdditionalNotes_dto import (
    AdditionalNoteInput,
    NotesFromTermsRequest,
    SummaryResponse,
    UnfairClause,
    AnalysisSummary,
    TermsSummary,
)

router = APIRouter(tags=["AdditionalNotes_Legacy"])


@router.post("/AdditionalNotes_Legacy", response_model=SummaryResponse)
def get_action_guidelines_from_terms(body: NotesFromTermsRequest) -> SummaryResponse:
    summary_info: AnalysisSummary = body.summary
    terms_summary: TermsSummary = body.termsSummary
    unfair_clauses: List[UnfairClause] = body.unfairClauses
    question: str = body.question

    # 1) 분석 요약
    context_str = (
        f"{summary_info.title} | "
        f"총 {summary_info.totalClauses}개 조항 중 {summary_info.unfairCount}개 불공정 조항 | "
        f"위험도: {summary_info.riskLevel}"
    )

    # 2) 불공정 조항 설명 문자열들
    clause_lines: List[str] = []
    for c in unfair_clauses:
        issue = c.issues[0] if c.issues else None
        clause_lines.append(
            f"- {c.clauseNumber}: {c.text} "
            f"(문제 유형: {issue.type if issue else 'N/A'}, "
            f"설명: {issue.description if issue else 'N/A'}, "
            f"관련 법률: {issue.relatedLaw if issue else 'N/A'})"
        )

    # 3) 약관 요약
    main_points_text = "\n".join([f"- {p}" for p in terms_summary.mainPoints]) if terms_summary.mainPoints else "- 없음"

    # LLM situation 구성
    situation_text = (
        f"사용자 질문: {question}\n\n"
        f"[약관 분석 요약]\n{context_str}\n\n"
        f"[약관 주요 내용]\n{main_points_text}\n\n"
        f"[불공정 조항 상세]\n" + ("\n".join(clause_lines) if clause_lines else "- 없음")
    )

    additional_input = AdditionalNoteInput(
        situation=situation_text,
        clause_number=None,
        session_id=body.session_id,
    )

    # 4) LLM 호출
    try:
        unfair_clause_dicts = [c.model_dump() for c in unfair_clauses]
        guidelines = generate_action_guidelines(unfair_clause_dicts, additional_input)
    except Exception as e:
        # 여기서 None 리턴하면 422가 나오는 원인이 되니, 반드시 예외 던지기
        raise HTTPException(500, f"행동 지침 생성 중 오류가 발생했습니다: {e}")

    # 5) 요약 문자열 생성 (항상 summary_text에 문자열 할당)
    if guidelines:
        primary = guidelines[0]

        basis = ""
        if unfair_clauses:
            first_clause = unfair_clauses[0]
            first_issue = first_clause.issues[0] if first_clause.issues else None
            law = first_issue.relatedLaw if first_issue else ""
            basis = f"{first_clause.clauseNumber} 내용이 {law}에 따라 불공정 조항에 해당할 수 있습니다."

        if basis:
            summary_text = f"{basis} 따라서, {primary.recommendation}"
        else:
            summary_text = primary.recommendation
    else:
        summary_text = (
            "약관 분석 결과를 바탕으로 구체적인 행동 지침을 제시하기 어렵습니다. "
            "추가 상황을 조금 더 자세히 설명해 주세요."
        )

    # 6) 반드시 SummaryResponse 인스턴스를 리턴
    return SummaryResponse(summary=summary_text)