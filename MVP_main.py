#-----[ FastAPI ]-----------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Terms_Analyze.core.MVP_rag import setup_rag
from Terms_Analyze.routers import MVP
from Complain_Email.routers import Complain_Email

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


# FastAPI 구동시 RAG 셋업을 최초 1회 실행
@app.on_event("startup")
def on_startup():
    setup_rag()