import io
import openpyxl
from openpyxl.styles import Alignment # 줄바꿈을 위해 Alignment만 남김
from Terms_Analyze.schemas.MVP_dto import TermsResponse
from Company_Terms_Analzye.schemas.Company_dto import CompanyAnalysisResponse

def create_consumer_report_excel(data: TermsResponse) -> io.BytesIO:
    wb = openpyxl.Workbook()
    
    # [시트 1: 요약 정보]
    ws_summary = wb.active
    ws_summary.title = "분석 요약"
    
    # 데이터 입력 (스타일링 제거)
    ws_summary.append(["항목", "내용"])
    ws_summary.append(["보고서 제목", data.summary.title])
    ws_summary.append(["개요", data.summary.overview])
    ws_summary.append(["총 조항 수", data.summary.totalClauses])
    ws_summary.append(["불공정 조항 수", data.summary.unfairCount])
    ws_summary.append(["위험도", data.summary.riskLevel])
    
    # [시트 2: 불공정 조항 상세]
    ws_detail = wb.create_sheet("불공정 조항 상세")
    ws_detail.append(["ID", "조항 번호", "약관 원문", "이슈 유형", "설명", "심각도", "관련 법률"])
    
    for clause in data.unfairClauses:
        for issue in clause.issues:
            ws_detail.append([
                clause.id,
                clause.clauseNumber,
                clause.text,
                issue.type,
                issue.description,
                issue.severity,
                issue.relatedLaw
            ])
    
    # 텍스트 줄바꿈 설정 (가독성을 위한 최소한의 조치)
    for row in ws_detail.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

def create_company_report_excel(data: CompanyAnalysisResponse) -> io.BytesIO:
    wb = openpyxl.Workbook()
    
    # [시트 1: 경영진 요약]
    ws_summary = wb.active
    ws_summary.title = "경영진 요약"
    
    # DTO 변경 사항 반영:
    # overallRiskLevel -> riskLevel
    # executiveSummary -> summary
    # worstCaseScenario -> worstScenario
    # complianceCheck -> 삭제됨
    
    ws_summary.append(["항목", "내용"])
    ws_summary.append(["종합 위험도", data.riskLevel])
    ws_summary.append(["요약 보고", data.summary])
    ws_summary.append(["최악의 시나리오", data.worstScenario])
    
    # [시트 2: 법적 취약점 목록]
    ws_detail = wb.create_sheet("법적 취약점")
    
    # DTO 변경 사항 반영:
    # relatedLaw 추가됨
    # abusePotential 삭제됨
    # improvementSuggestion -> suggestion
    headers = ["조항 원문", "위험도", "유형", "관련 법률", "설명", "수정 제안"]
    ws_detail.append(headers)
    
    for vuln in data.vulnerabilities:
        ws_detail.append([
            vuln.clause,
            vuln.riskLevel,
            vuln.vulnerabilityType,
            vuln.relatedLaw,    # 신규 필드
            vuln.description,
            vuln.suggestion     # 필드명 변경됨
        ])
        
    # 스타일링: 텍스트 줄바꿈 (Wrap Text) 및 상단 정렬
    for row in ws_detail.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    
    for row in ws_summary.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer