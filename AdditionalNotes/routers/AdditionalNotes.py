from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AdditionalNotes.core.AdditionalNotes_chain import generate_action_guidelines
from AdditionalNotes.schemas.AdditionalNotes_dto import (
    AdditionalNoteInput,
    AdditionalNotesRequest,
    AnalysisSummary,
    TermsSummary,
    UnfairClause,
    NewAnalysisResult,
)

router = APIRouter(tags=["AdditionalNotes"])

# 세션별로 AdditionalNotes에서만 쓰는 간단한 히스토리
_additional_sessions: Dict[str, Dict[str, Any]] = {}


class DetailedAnalysisResponse(BaseModel):
    summary: AnalysisSummary
    termsSummary: TermsSummary
    unfairClauses: List[UnfairClause]
    recommendations: List[str]
    session_id: str
    current_question: str
    analysis_guidelines: str = Field(description="세션 기반 행동 지침(약관 분석 내용은 요약 수준)")

@router.post("/AdditionalNotes", response_model=DetailedAnalysisResponse)
def get_action_guidelines_detailed(body: AdditionalNotesRequest):
    session_id = body.session_id
    question = body.question

    # 1. 분석 결과를 요청 바디에서 바로 사용
    if body.analysis_result is None:
        # 분석 결과가 아예 안 넘어오면, 지금처럼 질문만 기준으로 처리
        analysis_result = NewAnalysisResult(
            summary=AnalysisSummary(
                title="약관 분석 결과(요약 정보 사용 불가)",
                overview="analysis_result가 전달되지 않아 질문 내용만으로 행동 지침을 제공합니다.",
                totalClauses=0,
                unfairCount=0,
                riskLevel="중간",
            ),
            termsSummary=TermsSummary(mainPoints=[], keyRights=[], keyObligations=[]),
            unfairClauses=[],
            recommendations=[],
        )
    else:
        analysis_result = body.analysis_result

    # 2. 컨텍스트 생성 (이제 진짜 값 사용 가능)
    summary_info = analysis_result.summary
    context_parts = [
        f"{summary_info.title}",
        f"{summary_info.totalClauses}개 중 {summary_info.unfairCount}개 불공정",
        f"위험도: {summary_info.riskLevel}",
    ]
    session_context = " | ".join(context_parts)

    # 3. 주요 불공정 조항
    top_clauses = analysis_result.unfairClauses[:2]
    clause_lines = []
    for c in top_clauses:
        issue = c.issues[0] if c.issues else None
        clause_lines.append(
            f"{c.clauseNumber}: {c.text[:40]}... "
            f"({issue.type if issue else '문제'}, {issue.relatedLaw if issue else ''})"
        )

    additional_input = AdditionalNoteInput(
        situation=f"{question}\n[약관 분석 요약] {session_context}\n[주요 불공정 조항]\n" +
                  ("\n".join(clause_lines) if clause_lines else "없음"),
        clause_number=None,
        session_id=session_id,
    )

    guidelines = generate_action_guidelines(
        [c.model_dump() for c in analysis_result.unfairClauses],
        additional_input,
    )

    if guidelines:
        primary = guidelines[0]
        analysis_guidelines = (
            f"행동 지침: {primary.recommendation}\n"
            f"이유: {primary.reason}\n"
            f"법적 근거: {primary.related_law}"
        )
    else:
        analysis_guidelines = (
            f"분석 요약: {session_context}\n"
            f"추가 상황을 말씀해 주세요."
        )

    return DetailedAnalysisResponse(
        summary=analysis_result.summary,
        termsSummary=analysis_result.termsSummary,
        unfairClauses=analysis_result.unfairClauses,
        recommendations=analysis_result.recommendations,
        session_id=session_id,
        current_question=question,
        analysis_guidelines=analysis_guidelines,
    )