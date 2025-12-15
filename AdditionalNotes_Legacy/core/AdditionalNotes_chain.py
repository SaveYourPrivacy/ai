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
    base_guidelines_str = "" 

    json_format = """다음 JSON 형식으로 정확히 응답하세요:

{{
  "guidelines": [
    {{
      "recommendation": "구체적인 행동 지침",
      "reason": "행동 이유 및 법적 근거",
      "related_law": "관련 법률 조항"
    }}
  ]
}}

2~4개의 행동 지침을 제시하세요."""

    prompt_template = f"""불공정 약관 전문가로서, 주어진 분석 결과와 상황을 바탕으로
사용자가 실제로 취할 수 있는 구체적인 행동 지침을 제시하세요.

## 기본 행동 지침 참고
{base_guidelines_str}

## 현재 상황
{{situation}}

## 불공정 조항 요약
- 총 {{unfair_count}}개 불공정 조항
{{unfair_clauses_text}}

{json_format}
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
                recommendation=g.get("recommendation", "").strip(),
                reason=g.get("reason", "").strip(),
                related_law=g.get("related_law", "").strip(),
            )
            for g in guidelines_raw
        ]
        if not guidelines:
            raise ValueError("empty guidelines")
    except Exception:
        guidelines = [
            ActionGuideline(
                recommendation="공정거래위원회에 불공정 약관 신고를 검토하세요.",
                reason="약관의 규제에 관한 법률에 따라 불공정 약관은 무효가 될 수 있으며, 시정 요청이 가능합니다.",
                related_law="약관의 규제에 관한 법률 제6조, 제17조",
            )
        ]

    return guidelines