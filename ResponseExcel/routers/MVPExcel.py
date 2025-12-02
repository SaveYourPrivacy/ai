from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from Terms_Analyze.schemas.MVP_dto import TermsResponse
from Company_Terms_Analzye.schemas.Company_dto import CompanyAnalysisResponse
from ResponseExcel.core.makeExcel import create_company_report_excel,create_consumer_report_excel

router = APIRouter(
    tags=["Response Excel"]
)

@router.post("/report/consumer/excel")
def report_consumer_excel(response_dto: TermsResponse):
    """
    TermsResponse DTO(JSON)를 입력받아, 이를 엑셀 파일로 변환하여 다운로드합니다.
    """
    excel_buffer = create_consumer_report_excel(response_dto)
    
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=consumer_report.xlsx"}
    )

@router.post("/report/company/excel")
def report_company_excel(response_dto: CompanyAnalysisResponse):
    """
    CompanyAnalysisResponse DTO(JSON)를 입력받아, 기업 법무팀용 엑셀 리포트로 변환하여 다운로드합니다.
    """
    excel_buffer = create_company_report_excel(response_dto)
    
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=company_legal_report.xlsx"}
    )