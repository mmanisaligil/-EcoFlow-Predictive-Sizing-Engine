from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.routes_analyze import analyze
from app.domain.models import AnalyzeRequest
from app.exports.excel.exporter import export_analysis_to_xlsx

router = APIRouter(tags=["export"])


@router.post("/export/xlsx")
def export_xlsx(payload: AnalyzeRequest) -> StreamingResponse:
    analysis = analyze(payload)
    data = export_analysis_to_xlsx(analysis)
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=ecoflow_analysis.xlsx"},
    )
