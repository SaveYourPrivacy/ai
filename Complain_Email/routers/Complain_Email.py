from fastapi import APIRouter
from langchain.memory import ConversationBufferMemory
from Terms_Analyze.schemas.MVP_dto import sessions
from Complain_Email.schemas.Email_dto import ComplaintRequest, ComplaintResponse
from Complain_Email.core.Email_chain import complain_chain

router = APIRouter(
    tags=["Complain Email"]
)

@router.post("/complain_email", response_model=ComplaintResponse)
def generate_complaint(request: ComplaintRequest) -> ComplaintResponse:
    
    # 세션에 저장된 메모리 불러오기
    memory = sessions[request.session_id]
    history = memory.load_memory_variables({})['history']
    
    print(history)

    # Request JSON 형태를 딕셔너리 형태로 변환
    input_data = request.model_dump()
    input_data["history"] = history
    
    # 프롬프트 생성 및 LLM 동작
    response = complain_chain.invoke(input_data)
    
    return response