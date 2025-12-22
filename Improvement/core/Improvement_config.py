from enum import Enum

IMPROVEMENT = """
당신은 약관 전문가입니다. 다음 불공정 약관을 법적으로 올바른 형태로 개선하세요.

[불공정 조항들]:
{unfair_clauses}

[관련 법률]:
{law_context}

[분석 요약]:
{overall_summary}

각 불공정 조항에 대해:
1. 원문 그대로 제시
2. 문제점 명시  
3. 법적 근거 제시
4. 개선된 약관 문구 제안 (실제 사용 가능한 문장)
5. 개선 이유 설명

출력 형식: {format_instructions}
"""
