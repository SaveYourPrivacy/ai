#-------[LangChain RAG]--------------------
import os
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

retrievers = {}  # 카테고리별 retriever 저장
DATA_DIR = "Terms_Analyze/data"  # txt 파일 폴더 경로

# 카테고리 선택 → 파일명 매핑
CATEGORY_TO_FILE = {
    "광고": "advertisement.txt",
    "환불": "refund.txt",
    "개인정보": "privacy.txt",
    "책임제한": "liability.txt",
    "자동결제": "auto_payment.txt",
}

# 텍스트 로드 함수
def load_text(filepath: str):
    if not os.path.exists(filepath):
        print(f"파일 없음: {filepath}")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


# RAG 셋업 함수, FastAPI 구동시 최초 1회 실행
# 텍스트를 임베딩하여 Vector DB에 저장하는 함수
def setup_rag():
    print("RAG 벡터스토어 초기화 시작")

    # 1. 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    # 2. 임베딩
    embeddings = OpenAIEmbeddings()

    # 3. 카테고리별 법률 txt를 임베딩하여 retriever 생성
    for category, filename in CATEGORY_TO_FILE.items():
        filepath = os.path.join(DATA_DIR, filename)
        file_text = load_text(filepath)

        if not file_text:
            print(f"'{category}' 카테고리 로딩 실패 (파일 미존재)")
            continue

        # 문서 생성
        docs = text_splitter.create_documents([file_text])

        # 벡터 저장소 생성
        vector_store = FAISS.from_documents(docs, embeddings)

        # 검색기 생성 
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})

        # 카테고리별 retriever 저장
        retrievers[category] = retriever

        print(f"카테고리 '{category}' RAG 벡터 저장소 생성 완료")

    print("모든 카테고리 RAG 설정 완료")


# 카테고리에 맞는 retriever 반환 함수
def get_retriever(category: str):
    return retrievers.get(category)
