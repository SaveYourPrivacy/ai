# ai

# [SaveYourPrivacy] 

# 목차
1. [프로젝트 소개]
2. [주요 기능]
3. [전체 구조]
4. [기술 스택]
5. [시작 가이드]
    * [설치]
    * [실행]

# 프로젝트 소개
[SaveYourPrivacy]은 어렵고 복잡한 약관에 대해 사용자가 쉽게 접근할 수 있게해주는 약관분석 서비스입니다.

- 특징 1: 사용자에 따라 차별화된 서비를 제공합니다. (소비자용 / 기업용)
- 특징 2: 소비자용 기능에서는 약관의 불공정성, 기업용 기능에서는 약관의 취약점을 분석합니다.
- 특징 3: 분석 결과를 바탕으로 추가적인 기능을 제공합니다.


# 주요 기능
* 불공정 약관 분석기능   : 소비자가 분석 희망약관과 집중분석 카테고리를 입력하면, 불공정 조항이 존재하는지에 대해         
                         분석해드립니다.
* 취약 약관 분석기능     : 기업이 분석 희망약관과 집중분석 카테고리를 입력하면, 취약 조항이 존재하는지에 대해
                         분석하고 해당 취약점이 악용됐을 때의 시나리오를 출력합니다.
* 약관 개선사항 제안기능  : 약관 분석 결과를 바탕으로 약관 개선사항을 제안해드립니다.
* 추가 행동지침 제안기능  : 약관 분석 결과를 바탕으로 소비자의 질문에 맞춰 이후 행동지침을 제안해드립니다.
* 컴플레인 메일 작성기능  : 약관 분석 결과를 바탕으로 소비자가 기업에 항의하기위한 컴플레인 메일을 작성해드립니다.
* 실제 피해사례 검색기능  : 취약점 악용시나리오와 유사한 실제 피해사례를 제시해 드립니다.
* 분석결과 엑셀반환 기능  : 분석 결과를 엑셀로 정리해 반환합니다. (기능 구현만 하고 서비스X, 프론트 미구현)


# 전체 구조
src/
├── AdditionalNotes/                  # 추가 행동 지침 제안 기능 API
│   ├── core/                         # 기능 핵심 코드 패키지
│   │   ├── AdditionalNotes_chain.py  # 추가 행동 지침 생성 LangChain 코드
│   │   └── AdditionalNotes_config.py # LLM 프롬프트
│   │
│   ├── routers/                      # 추가 행동지침 제안 기능 API 처리 패키지
│   │   └── AdditionalNotes.py        # API 처리 FastAPI 기반 코드
│   │
│   └── schemas/                      # DTO 패키지
│       └── AdditionalNotes_dto.py    # 추가 행동 지침 제안 기능 Req&Res DTO 코드
│
├── CaseSearch/                  # 실제 피해사례 검색 기능 API
│   ├── core/                    # 기능 핵심 코드 패키지
│   │   ├── CaseSearch_chain.py  # 실제 피해사례 검색 기능 LangChain 코드
│   │   └── CaseSearch_config.py # LLM 프롬프트
│   │
│   ├── routers/                 # API 처리 패키지
│   │   └── CaseSearch.py        # API 처리 FastAPI 기반 코드
│   │
│   └── schemas/                 # DTO 패키지
│       └── CaseSearch_dto.py    # API Req&Res DTO 코드
│
├── Company_Terms_Analzye/              # 기업용 약관 취약점 분석 기능 API
│   ├── core/                           # 기능 핵심 코드 패키지
│   │   ├── Company_chain.py            # 취약점 분석 LangChain 코드
│   │   └── Company_config.py           # 취약점 분석 프롬프트
│   │
│   ├── routers/                        # 취약점 분석 API 처리 패키지
│   │   └── Company_Terms_Analzye.py    # API 처리 FastAPI 기반 코드
│   │
│   └── schemas/                        # DTO 패키지
│       └── Company_DTO.py              # 취약점 분석 기능 Req&Res DTO 코드
│
├── Complain_Email/           # 컴플레인 메일 작성 기능 API
│   ├── core/                 # 기능 핵심 코드 패키지
│   │   ├── Email_chain.py    # 컴플레인 메일 생성 LangChain 코드
│   │   └── Email_config.py   # 컴플레인 메일 생성 프롬프트
│   │
│   ├── routers/              # 취약점 분석 API 처리 패키지
│   │   └── Complain_Email.py # API 처리 FastAPI 기반 코드
│   │
│   └── schemas/              # DTO 패키지
│       └── Email_dto.py      # 컴플레인 메일생성 기능 Req&Res DTO 코드
│
├── Improvement/                  # 약관 개선사항 제안 기능 API
│   ├── core/                     # 기능 핵심 코드 패키지
│   │   ├── Improvement_chain.py  # 약관 개선사항 제안 기능 LangChain 코드
│   │   └── Improvement_config.py # LLM 프롬프트
│   │
│   ├── routers/                  # API 처리 패키지
│   │   └── Improvement_Email.py  # API 처리 FastAPI 기반 코드
│   │
│   └── schemas/                  # DTO 패키지
│       └── Improvement_dto.py    # API Req&Res DTO 코드
│
├── ResponseExcel/            # 약관 분석 결과 엑셀 반환 기능 (프론트 미구현...)
│   ├── core/                 # 기능 핵심 코드 패키지
│   │   └── makeExcel.py      # 분석 결과 엑셀 작성 코드
│   │
│   └── routers/              # 분석 결과 엑셀 반환 API 처리 패키지
│       └── MVPExcel.py       # API 처리 FastAPI 기반 코드
│
├── Terms_Analyze/           # 소비자용 불공정 약관 분석 기능 API
│   ├── core/                # 기능 핵심 코드 패키지
│   │   ├── MVP_chain.py     # 불공정 약관 분석 기능 LangChain 코드
│   │   ├── MVP_config.py    # LLM 프롬프트
│   │   └── MVP_rag.py       # 약관분석의 기반자료가 될 Vector DB 임베딩 코드
│   │
│   ├── data/                # 임베딩 될 기반 법률 자료 패키지
│   │   ├── advertisement.txt     # 광고 관련 법률
│   │   ├── auto_payment.txt      # 자동결제 관련 법률
│   │   ├── LAW_TEXT.py           # 약관작성 관련 법률 (이전 버전활용/현재 활용 X)
│   │   ├── liability.txt         # 책임제한 관련 법률
│   │   ├── privacy.txt           # 개인정보 관련 법률
│   │   └── refund.txt            # 환불 관련 법률
│   │
│   ├── routers/              # API 처리 패키지
│   │   └── MVP.py            # API 처리 FastAPI 기반 코드
│   │
│   └── schemas/              # DTO 패키지
│       └── MVP_dto.py        # API의 Req&Res DTO 코드
│
├── MVP_backup.py              # 앱 초기버전 백업 코드(현재 활용 X)
└── MVP_main.py                # 백엔드 실행 (라우터 통합 코드)


# 기술 스택
|      분류      |      기술                                 |
| -------------- | ---------------------------------------- |
| 개발 언어      | Python 3.12.2                             |
| 활용 라이브러리 | LangChain, FAISS, Google Search, pydantic |
| LLM           | gpt-4o-mini                               |
| API 처리       | FastAPI                                   |


# 시작 가이드 

# 전제 조건
[Python 3.12.2] 환경에서 동작합니다.

# 설치
1. 저장소를 클론합니다.
   VS 코드 기준
   git clone https://github.com/SaveYourPrivacy/ai.git

2. 프로젝트 디렉토리 최상단에 위치합니다.

3. 본인이 사용할 가상환경을 활성화한 후 패키지 설치를 진행합니다.
   pip install -r requirements.txt

4. 프로젝트 디렉토리 최상단에서 벡엔드 실행코드를 구동합니다.
   fastapi dev .\MVP_main.py

5. 앱을 구동합니다. (프론트엔드 README 참고)