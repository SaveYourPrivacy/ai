#-----[ FastAPI ]-----------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Terms_Analyze.core.MVP_rag import setup_rag
from Terms_Analyze.routers import MVP
from Company_Terms_Analzye.routers import Company_Terms_Analzye
from AdditionalNotes.routers import AdditionalNotes

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MVP 약관분석 라우터
app.include_router(MVP.router)
#추가 상황에 따른 행동 지침 라우터
app.include_router(AdditionalNotes.router)
# 기업용 약관 취약점 분석 라우터
app.include_router(Company_Terms_Analzye.router)
# 엑셀 반환 라우터

# FastAPI 구동시 RAG 셋업을 최초 1회 실행
@app.on_event("startup")
def on_startup():
    setup_rag()