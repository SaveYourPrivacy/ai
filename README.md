# ai

## 📁 프로젝트 구조

```
src/
├── AdditonalNotes/                 #추가 행동지침
│   ├── core/
│   |  ├── AdditonalNotes_chain.py
│   |  └── AdditonalNotes_config.py
│   ├── routers/
│   |  └── AdditonalNotes.py
│   └── schemas/
│      └── AdditonalNotes_dto.py
├── CaseSearch/                  #유사한 사례 검색
│   ├── core/
│   |  ├── CaseSearch_chain.py
│   |  └── CaseSearch_config.py
│   ├── routers/
│   |  └── CaseSearch.py
│   └── schemas/
│      └── CaseSearch_dto.py
├── Company_Terms_Analyze/
│   ├── core/
│   |  ├── Company_chain.py
│   |  └── Company_config.py
│   ├── routers/
│   |  └── Company_Terms_Analzye.py
│   ├── schemas/
│     └── Company_dto.py
│   └── .DS_Store
├── Complain_Email/
│   ├── core/
│   |  ├── Email_chain.py
│   |  └── Email_config.py
│   ├── routers/
│   |  └── Complain_Email.py
│   └── schemas/
│      └── Email_dto.py
├── Improvement/                  #추가 개선 사항
│   ├── core/
│   |  ├── Improvement_chain.py
│   |  └── Improvement_config.py
│   ├── routers/
│   |  └── Improvement.py
│   └── schemas/
│      └── Improvement_dto.py
├── ResponseExcel/
│   ├── core/
│   |  └── makeExcel.py
│   ├── routers/
│   |  └── MVPExcel.py
│   └── .DS_Store
├── Term_Analyze/
│   ├── core/
│   |  ├── MVP_chain.py
│   |  ├── MVP_config.py
│   |  └── MVP_rag.py
│   ├── data/
│   |  ├── LAW_TEXT.py
│   |  ├── advertisement.txt
│   |  ├── auto_payment.txt
│   |  ├── liability.txt
│   |  ├── privacy.txt
│   |  └── refund.txt
│   ├── routers/
│   |  └── MVP.py
│   └── schemas/
│      ├── .DS_Store
│      └── MVP_dto.py
├── data/
│     └── .DS_Store
│
├── MVP_backup.py
├── MVP_main.py
└── main.jsx                 
```

## 🎯 주요 기능

### 1. 추가 행동 지침
- **사용자 질문 기반 상황 텍스트 구성**
  - 사용자 입력 질문만으로 situation 텍스트 생성
- **행동 지침 생성 결과 처리**
  - LMM이 생성한 행동 지침 리스트 중 첫 번째 항목만 사용
- **요약 응답 추출 로직**
  - primary 가이드라인의 recommendation을 최종 요약으로 반환
- **예외 처리 및 사용자 안내**
  - 가이드라인이 없을 경우, 추가 상황 설명 요청 메시지 반환
- **출력 구조 단순화**
  - SummaryResponse DTO로 요약 문장만 반환환


### 2. 유사한 사례 검색
- **구글 검색하여 관련 실제 사항 출력**
  - 최악의 시나리오을 기반으로 검색 쿼리 생성
  - Google 검색 엔진을 활용해 불공정 약관 관련 실제 피해 사례 수집
  - 검색 결과는 URL 원문을 유지한 상태로 전달
  - LMM을 통해 결과를 title/summary 형태로 구조화
  - 최종적으로 실제 피해 사례 리스트를 DTO 형태로 변환

### 3. 구체적인 약관 개선 사항 제공
- **분석 결과 전달**: FastAPI에서 약관 분석 결과  + category 수신
- **법령 RAG 검색**:
  - get_retriever(category)로 카테고리별 법령 조회
  - 검색 실패 시 기본 법령 컨텍스트 사용
- **LMM 입력 구성**: 불공정 조항 + 분석 요약 + 법령 컨텍스트를 함꼐 전달
- **출력 구조 과정**: JSON Parser 로 ImprovementResponse 형태로 변환
- 법령 근거 기반 개선안 생성 -> 일관성-신뢰도 향상

