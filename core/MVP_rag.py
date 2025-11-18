#-------[LangChain RAG]--------------------
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from data.LAW_TEXT import LAW_TEXT
from langchain_openai import OpenAIEmbeddings

retriever = None # RAG 사용을 위해 검색기 retriever 전역변수 선언

# RAG 셋업 함수, FastAPI 구동시 최초 1회 실행
# 텍스트를 임베딩하여 Vector DB에 저장하는 함수
def setup_rag():
    global retriever
    if not LAW_TEXT or "(사용자 작업 필요)" in LAW_TEXT:
        print("경고: LAW_TEXT가 비어있습니다. RAG 기능이 비활성화됩니다.")
        print("법률 URL의 전체 텍스트를 LAW_TEXT 변수에 복사해 주세요.")
        return

    # 1. 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100
    )
    docs = text_splitter.create_documents([LAW_TEXT])
    
    # 2. 임베딩
    embeddings = OpenAIEmbeddings()
    
    # 3. 벡터 저장소 (FAISS 사용)  install 필요!!!!!
    # docs를 임베딩하여 FAISS 벡터 저장소를 생성
    vector_store = FAISS.from_documents(docs, embeddings)
    
    # 4. 검색기 생성
    # 이 검색기는 k=5 (가장 유사한 5개) 조각을 검색
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    print("RAG 벡터 저장소 및 검색기(Retriever)가 성공적으로 준비되었습니다.")

def get_retriever():
    return retriever