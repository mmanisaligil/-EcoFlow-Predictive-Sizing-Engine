from fastapi import FastAPI

from app.api.routes_analyze import router as analyze_router
from app.api.routes_export import router as export_router
from app.api.routes_health import router as health_router
from app.api.routes_metadata import router as metadata_router
from app.data.cache import get_data_cache

app = FastAPI(title="ecoflow-sizing-v13", version="1.3.0")

app.include_router(health_router)
app.include_router(metadata_router)
app.include_router(analyze_router)
app.include_router(export_router)


@app.on_event("startup")
def startup_validation() -> None:
    get_data_cache()
