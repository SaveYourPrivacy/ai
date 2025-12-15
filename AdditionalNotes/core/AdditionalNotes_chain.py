from typing import List, Dict, Any, Optional
from threading import local
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from AdditionalNotes.core.AdditionalNotes_config import BASE_GUIDELINES
from AdditionalNotes.schemas.AdditionalNotes_dto import (
    AdditionalNoteInput,
    ActionGuideline,
    ActionGuidelineResponse
)

# Thread-safe 세션 저장소
_sessions_container = local()

def _get_sessions() -> Dict[str, ConversationBufferMemory]:
    if not hasattr(_sessions_container, 'sessions'):
        _sessions_container.sessions = {}
    return _sessions_container.sessions

def get_session_memory(session_id: str):
    """Thread-safe 세션 메모리 관리"""
    sessions = _get_sessions()
    if session_id not in sessions:
        print(f"새 세션 생성: {session_id}")
        sessions[session_id] = ConversationBufferMemory(
            return_messages=True,
            memory_key="history"
        )
    else:
        print(f"기존 세션 로드: {session_id}")
    return sessions[session_id]

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def generate_action_guidelines(
    unfair_clauses: List[Dict[str, Any]],
    additional_input: AdditionalNoteInput,
) -> List[ActionGuideline]:
    """완전 수정: PromptTemplate + 수동 파싱"""
    
    memory = get_session_memory(additional_input.session_id)
    
    # 안전한 chat_history 변환
    chat_history_str = "이전 대화 없음"
    try:
        memory_vars = memory.load_memory_variables({})
        messages = memory_vars.get("history", [])
        if messages:
            chat_history_str = "\n".join([
                f"사용자: {getattr(msg, 'content', str(msg))[:200]}" 
                if "human" in str(msg).lower() 
                else f"AI: {getattr(msg, 'content', str(msg))[:200]}"
                for msg in messages[-4:]
            ])
            print(f"📝 이전 대화 ({len(messages)}개):\n{chat_history_str[:150]}...")
    except Exception as e:
        print(f"대화 로드 실패: {e}")
    
    # BASE_GUIDELINES 통합
    base_guidelines_str = "\n".join([f"• {k}: {v}" for k, v in BASE_GUIDELINES.items()])
    
    # 1. 수동 JSON 형식 지시사항 (PydanticOutputParser 제거)
    json_format = """다음 JSON 형식으로 정확히 응답하세요:

{{
  "guidelines": [
    {{
      "recommendation": "구체적인 행동 지침",
      "reason": "행동 이유 및 법적 근거", 
      "related_law": "관련 법률 조항"
    }}
  ],
  "session_id": "세션ID"
}}

2~4개의 행동 지침을 제시하세요."""
    
    # 2. PromptTemplate 사용 (변수 문제 완전 해결)
    prompt_template = f"""불공정 약관 전문가로서, 주어진 세션 컨텍스트를 분석하여 실질적 행동 지침을 제시하세요.

## 세션 분석 근거
{chat_history_str}

## 현재 상황
{additional_input.situation}

## 불공정 조항
불공정 조항 수: {len(unfair_clauses)}개

**중요**: 세션 컨텍스트를 참고하여 다음 단계의 구체적 행동을 제시하세요.

{json_format}"""

    prompt = PromptTemplate.from_template(prompt_template)
    
    # LLM에 직접 프롬프트 전달 + JSON 강제
    chain = prompt | _llm
    
    # 3. 실제 데이터 포함하여 invoke
    result_text = chain.invoke({
        "unfair_clauses": "\n".join([f"- {c['clauseNumber']}: {c['text'][:100]}..." for c in unfair_clauses])
    }).content
    
    print(f"LLM 원본 응답: {result_text[:200]}...")
    
    # 4. 수동 JSON 파싱 (안전성 최우선)
    try:
        import json
        # JSON만 추출
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        json_str = result_text[start_idx:end_idx]
        result_dict = json.loads(json_str)
        
        # Pydantic 검증
        result = ActionGuidelineResponse.model_validate(result_dict)
        
    except Exception as e:
        print(f"JSON 파싱 실패: {e}")
        print("기본 응답으로 대체")
        # 기본 응답
        result = ActionGuidelineResponse(
            guidelines=[
                ActionGuideline(
                    recommendation="공정거래위원회에 불공정 약관 신고",
                    reason="불공정 약관 규제법 위반 가능성",
                    related_law="약관의 규제에 관한 법률 제6조"
                )
            ],
            session_id=additional_input.session_id or ""
        )
    
    # 메모리 저장
    try:
        guideline_texts = [g.recommendation[:30] for g in result.guidelines]
        memory.save_context(
            {"input": additional_input.situation},
            {"output": f"[{', '.join(guideline_texts)}]"}
        )
    except Exception as e:
        print(f"메모리 저장 실패: {e}")
    
    print(f"행동 지침 {len(result.guidelines)}개 생성!")
    return result.guidelines

def _get_extractor_chain():
    prompt_template = """사용자의 질문에서 다음 정보를 추출하여 JSON으로 응답하세요:

{{
  "situation": "사용자 상황 (필수)",
  "clause_number": "조항 번호 (없으면 null)"
}}

질문: {question}"""

    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | _llm
    
    def parse_with_chain(question: str) -> AdditionalNoteInput:
        try:
            result_text = chain.invoke({"question": question}).content
            import json
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            data = json.loads(result_text[start:end])
            data["session_id"] = None
            return AdditionalNoteInput.model_validate(data)
        except:
            return AdditionalNoteInput(
                situation=question[:50] + "..." if len(question) > 50 else question,
                clause_number=None,
                session_id=None
            )
    return parse_with_chain

# 전역 체인 (한번만 생성)
_parse_chain = _get_extractor_chain()

def parse_question_to_additional_input(question: str) -> AdditionalNoteInput:
    try:
        result = _parse_chain(question)
        print(f"질문 파싱 성공: {result.situation}")
        return result
    except Exception as e:
        print(f"[ERROR] Question parsing failed: {e}")
        return AdditionalNoteInput(
            situation=question[:50] + "..." if len(question) > 50 else question,
            clause_number=None,
            session_id=None
        )