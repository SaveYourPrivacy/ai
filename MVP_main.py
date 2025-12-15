#-----[ FastAPI ]-----------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Terms_Analyze.core.MVP_rag import setup_rag
from Terms_Analyze.routers import MVP
from Complain_Email.routers import Complain_Email
from Company_Terms_Analzye.routers import Company_Terms_Analzye
from ResponseExcel.routers import MVPExcel
from AdditionalNotes.routers import AdditionalNotes
from Improvement.routers import Improvement

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
# 컴플레인 이메일 생성 라우터
app.include_router(Complain_Email.router)
# 기업용 약관 취약점 분석 라우터
app.include_router(Company_Terms_Analzye.router)
# 엑셀 반환 라우터
app.include_router(MVPExcel.router)
# 추가 행동 지침
app.include_router(AdditionalNotes.router)
# 구체적인 약관 개선 사항
app.include_router(Improvement.router)

# FastAPI 구동시 RAG 셋업을 최초 1회 실행
@app.on_event("startup")
def on_startup():
    setup_rag()