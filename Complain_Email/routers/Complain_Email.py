from fastapi import APIRouter
from Complain_Email.schemas.Email_dto import ComplaintRequest, ComplaintResponse
from Complain_Email.core.Email_chain import complain_chain

router = APIRouter(
    tags=["Complain Email"]
)

@router.post("/complain_email", response_model=ComplaintResponse)
def generate_complaint(request: ComplaintRequest) -> ComplaintResponse:
    
    # Request JSON 형태를 딕셔너리 형태로 변환
    input_data = request.model_dump()
    
    # 프롬프트 생성 및 LLM 동작
    response = complain_chain.invoke(input_data)
    
    return response