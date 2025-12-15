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
    unfair_clauses: list[UnfairClause] = body.unfairClauses
    question: str = body.question

    # 1) 분석 요약
    context_str = (
        f"{summary_info.title} | "
        f"총 {summary_info.totalClauses}개 조항 중 {summary_info.unfairCount}개 불공정 조항 | "
        f"위험도: {summary_info.riskLevel}"
    )

    # 2) 주요 불공정 조항 상세 설명 (가능하면 전부)
    clause_lines: list[str] = []
    for c in unfair_clauses:
        issue = c.issues[0] if c.issues else None
        clause_lines.append(
            f"- {c.clauseNumber}: {c.text} "
            f"(문제 유형: {issue.type if issue else 'N/A'}, "
            f"설명: {issue.description if issue else 'N/A'}, "
            f"관련 법률: {issue.relatedLaw if issue else 'N/A'})"
        )

    # 3) 약관 요약 내용
    main_points_text = "\n".join([f"- {p}" for p in terms_summary.mainPoints]) if terms_summary.mainPoints else "- 없음"
    rights_text = "\n".join([f"- {r}" for r in terms_summary.keyRights]) if terms_summary.keyRights else "- 없음"
    obligations_text = "\n".join([f"- {o}" for o in terms_summary.keyObligations]) if terms_summary.keyObligations else "- 없음"

    # LLM에 넘길 situation을 “분석 결과를 그대로 풀어쓴 설명”으로 구성
    situation_text = (
        f"사용자 질문: {question}\n\n"
        f"[약관 분석 요약]\n{context_str}\n\n"
        f"[약관 주요 내용]\n{main_points_text}\n\n"
        f"[이용자의 핵심 권리]\n{rights_text}\n\n"
        f"[이용자의 핵심 의무]\n{obligations_text}\n\n"
        f"[불공정 조항 상세]\n" + ("\n".join(clause_lines) if clause_lines else "- 없음")
    )

    additional_input = AdditionalNoteInput(
        situation=situation_text,
        clause_number=None,
        session_id=body.session_id,
    )

    # 나머지 generate_action_guidelines 호출, summary_text 생성 부분은 그대로
    unfair_clause_dicts = [c.model_dump() for c in unfair_clauses]
    guidelines = generate_action_guidelines(unfair_clause_dicts, additional_input)

    if guidelines:
        primary = guidelines[0]
        summary_text = (
            f"분석 결과, 다음과 같은 불공정 조항이 확인되었습니다.\n"
            f"{clause_lines[0] if clause_lines else ''}\n\n"
            f"행동 지침: {primary.recommendation}\n"
            f"이유: {primary.reason}\n"
            f"법적 근거: {primary.related_law}"
        )
    else:
        summary_text = (
            f"[약관 분석 요약] {context_str}\n"
            f"구체적인 행동 지침을 생성하지 못했습니다. "
            f"추가 상황을 조금 더 자세히 설명해 주세요."
        )

    return SummaryResponse(summary=summary_text)