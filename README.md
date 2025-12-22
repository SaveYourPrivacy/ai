# ai

## 📁 프로젝트 구조

```
src/
├── AdditonalNotes/
│   ├── core/
│   |  ├── AdditonalNotes_chain.py
│   |  ├── AdditonalNotes_config.py
│   ├── routers/
│   |  ├── AdditonalNotes.py
│   ├── schemas/
│   |  ├── AdditonalNotes_dto.py
├── CaseSearch/
│   ├── core/
│   |  ├── CaseSearch_chain.py
│   |  ├── CaseSearch_config.py
│   ├── routers/
│   |  ├── CaseSearch.py
│   ├── schemas/
│   |  ├── CaseSearch_dto.py
├── Company_Terms_Analyze/
│   ├── core/
│   |  ├── AdditonalNotes_chain.py
│   |  ├── AdditonalNotes_config.py
│   ├── routers/
│   |  ├── AdditonalNotes.py
│   ├── schemas/
│   |  ├── AdditonalNotes_dto.py
├── Complain_Email/
│   ├── core/
│   |  ├── AdditonalNotes_chain.py
│   |  ├── AdditonalNotes_config.py
│   ├── routers/
│   |  ├── AdditonalNotes.py
│   ├── schemas/
│   |  ├── AdditonalNotes_dto.py
├── Improvement/
│   ├── core/
│   |  ├── Improvement_chain.py
│   |  ├── Improvement_config.py
│   ├── routers/
│   |  ├── Improvement.py
│   ├── schemas/
│   |  ├── Improvement_dto.py
├── ResponseExcel/
│   ├── core/
│   |  ├── AdditonalNotes_chain.py
│   |  ├── AdditonalNotes_config.py
│   ├── routers/
│   |  ├── AdditonalNotes.py
│   ├── schemas/
│   |  ├── AdditonalNotes_dto.py
├── Term_Analyze/
│   ├── core/
│   |  ├── AdditonalNotes_chain.py
│   |  ├── AdditonalNotes_config.py
│   ├── routers/
│   |  ├── AdditonalNotes.py
│   ├── schemas/
│   |  ├── AdditonalNotes_dto.py
├── data/
│
├── api/                       # API 통신 레이어
│   ├── termsAnalysis.js      # 소비자용 약관 분석 API
│   ├── businessAnalysis.js   # 기업용 약관 분석 API
│   ├── questionAnswer.js     # 추가 질문 API
│   ├── complaintEmail.js     # 컴플레인 메일 생성 API
│   └── similarCases.js       # 유사 사례 검색 API
│
├── styles/                    # CSS 파일 (컴포넌트와 동일한 구조)
│   ├── common/
│   └── home/
│
├── App.jsx                    # 루트 컴포넌트
└── main.jsx                   # 앱 진입점
```

## 🎯 주요 기능

### 1. 소비자용 약관 분석

#### 약관 입력
- **직접 입력**: 텍스트 영역에 약관 내용 직접 입력
- **파일 업로드**: PDF 파일 업로드로 간편한 분석
- **약관 종류 선택**: 환불/해지, 자동결제, 개인정보, 책임제한, 광고 등 카테고리 선택

#### 분석 결과
- **요약 정보**: 전체 조항 수, 불공정 조항 수, 위험도 표시
- **약관 주요 내용**: 핵심 내용, 주요 권리, 주요 의무
- **불공정 조항 상세**:
  - 조항 번호 및 원문
  - 문제점 유형 및 심각도
  - 법적 근거 (관련 법령)
  - 상세 설명

#### 추가 기능
- **질의응답**: 분석 결과에 대한 추가 질문 가능
- **컴플레인 메일 템플릿**: 분석 결과 기반 자동 생성된 메일 템플릿 제공

### 2. 기업용 약관 분석

#### 약관 취약점 분석
- **취약점 식별**: 약관 내 잠재적 위험 요소 파악
- **심각도 평가**: 각 취약점의 위험도 측정 (높음/중간/낮음)
- **개선 권고사항**: 구체적인 개선 방안 제시

#### 악용 시나리오
- **최악의 시나리오**: 약관 조항이 악용될 수 있는 시나리오 제시
- **유사 실제 사례**: AI가 검색한 실제 발생 사례 연결

#### 추가 기능
- **질의응답**: 분석 결과에 대한 추가 질문 가능
