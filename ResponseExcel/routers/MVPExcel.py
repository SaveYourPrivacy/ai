from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from Terms_Analyze.schemas.MVP_dto import TermsResponse
from Company_Terms_Analzye.schemas.Company_dto import CompanyAnalysisResponse
from ResponseExcel.core.makeExcel import create_company_report_excel,create_consumer_report_excel

router = APIRouter(
    tags=["Response Excel"]
)

@router.post("/MVP/excel")
def report_consumer_excel(response_dto: TermsResponse):

    excel_buffer = create_consumer_report_excel(response_dto)
    
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=MVP_report.xlsx"}
    )

@router.post("/company_terms_analyze/excel")
def report_company_excel(response_dto: CompanyAnalysisResponse):

    excel_buffer = create_company_report_excel(response_dto)
    
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=company_analyze_report.xlsx"}
    )