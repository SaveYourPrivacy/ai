from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from AdditionalNotes_Legacy.core.AdditionalNotes_config import BASE_GUIDELINES
from AdditionalNotes_Legacy.schemas.AdditionalNotes_dto import (
    AdditionalNoteInput,
    ActionGuideline,
)


_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def generate_action_guidelines(unfair_clauses, additional_input: AdditionalNoteInput):
    json_format = """다음 JSON 형식으로 정확히 응답하세요:

{{
  "guidelines": [
    {{
      "recommendation": "답변"
    }}
  ]
}}

2~4개의 행동 지침을 제시하세요."""

    prompt_template = f"""법률 전문가로서, 주어진 분석 결과와 질문을 바탕으로
사용자에게 전문적인 답변을 제시해주세요. 답변을 제시할 때에는 참고해야 할 법률 조항과 약관을 명시해서 작성해야만 합니다.

## 현재 상황
{{situation}}

## 불공정 조항 요약
- 총 {{unfair_count}}개 불공정 조항
{{unfair_clauses_text}}

{json_format}

## 답변 예시
질문 1: "이용 약관의 불공정 조항 때문에 계약 해지를 원합니다. 어떻게 해야 하나요?"
답변 1: {{{{"guidelines": [
    {{{{
      "recommendation": "계약 해지를 원하시면, 먼저 서비스 제공자에게 계약 해지 의사를 서면으로 통지하세요. 또한, 약관 제5조 3항에 따르면, 계약 해지 시점까지의 이용 요금을 정산해야 합니다. 만약 서비스 제공자가 부당하게 계약 해지를 거부할 경우, 공정거래위원회에 신고할 수 있습니다."
    }}}}
]]}}}}
질문 2: "개인정보 보호를 위해 어떤 조치를 취해야 하나요?"
답변 2: {{{{"guidelines": [
    {{{{
      "recommendation": "개인정보 보호를 위해서는 약관 제3조 5항을 근거로, 서비스 제공자에게 개인정보 수집 및 이용에 대한 명확한 동의를 요청하세요. 또한, 개인정보 유출 시 즉시 관련 기관에 신고하고, 개인정보 보호법에 따라 손해배상을 청구할 수 있습니다."
    }}}}
]]}}}}
"""

    prompt = PromptTemplate.from_template(prompt_template)

    unfair_clauses_text = "\n".join(
        [
            f"- {c.get('clauseNumber', '')}: {c.get('text', '')[:100]}..."
            for c in unfair_clauses
        ]
    )

    chain = prompt | _llm

    result_text = chain.invoke(
        {
            "situation": additional_input.situation,
            "unfair_count": len(unfair_clauses),
            "unfair_clauses_text": unfair_clauses_text,
        }
    ).content

    import json
    try:
        start = result_text.find("{")
        end = result_text.rfind("}") + 1
        data = json.loads(result_text[start:end])
        guidelines_raw = data.get("guidelines", [])
        guidelines = [
            ActionGuideline(
                recommendation=g.get("recommendation", "").strip()
            )
            for g in guidelines_raw
        ]
        if not guidelines:
            raise ValueError("empty guidelines")
    except Exception:
        guidelines = [
            ActionGuideline(
                recommendation="공정거래위원회에 불공정 약관 신고를 검토하세요."
            )
        ]

    return guidelines