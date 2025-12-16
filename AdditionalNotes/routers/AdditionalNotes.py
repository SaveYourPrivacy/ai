from fastapi import APIRouter
import ast

from Terms_Analyze.schemas.MVP_dto import sessions as user_sessions
from Company_Terms_Analzye.schemas.Company_dto import sessions as company_sessions
from AdditionalNotes.core.AdditionalNotes_chain import generate_action_guidelines
from AdditionalNotes.schemas.AdditionalNotes_dto import (
    AdditionalNoteInput,
    NotesFromTermsRequest,
    SummaryResponse,
)

router = APIRouter(tags=["AdditionalNotes"])


@router.post("/AdditionalNotes", response_model=SummaryResponse)
def get_action_guidelines_from_terms(request: NotesFromTermsRequest) -> SummaryResponse:
    memory = None
    if request.session_id in user_sessions:
        memory = user_sessions[request.session_id]
    elif request.session_id in company_sessions:
        memory = company_sessions[request.session_id]
    else:
        raise ValueError(f"세션 ID를 찾을 수 없습니다: {request.session_id}")

    # 메모리의 첫 번째 입력 메시지에서 약관 분석 결과 추출
    messages = memory.chat_memory.messages
    terms_analysis = None

    if messages and len(messages) > 0:
        first_input = messages[0].content
        try:
            start_idx = first_input.find("{")
            end_idx = first_input.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                dict_str = first_input[start_idx:end_idx]
                # Python dict 표현식을 파싱
                terms_analysis = ast.literal_eval(dict_str)
        except Exception as e:
            print(f"메모리 파싱 오류: {e}")

    # situation 텍스트 생성
    situation_text = f"사용자 질문: {request.question}"

    # AdditionalNoteInput 생성
    additional_input = AdditionalNoteInput(
        situation=situation_text,
        session_id=request.session_id,
    )

    # generate_action_guidelines 호출 - 전체 약관 분석 결과 전달
    guidelines = generate_action_guidelines(terms_analysis, additional_input)

    # 응답 생성
    if guidelines:
        primary = guidelines[0]
        summary_text = primary.recommendation
    else:
        summary_text = (
            "구체적인 행동 지침을 생성하지 못했습니다. "
            "추가 상황을 조금 더 자세히 설명해 주세요."
        )

    return SummaryResponse(summary=summary_text)