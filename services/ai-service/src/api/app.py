"""FastAPI application: CORS, routers, exception handlers."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.models import ExtractionError
from src.api.routers import frameworks, health

app = FastAPI(
    title="Governance Agent API",
    description="Compliance Framework Extraction & Evaluation",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(frameworks.router)


@app.exception_handler(ExtractionError)
async def extraction_error_handler(request, exc: ExtractionError):
    return JSONResponse(
        status_code=500,
        content={
            "error": "extraction_failed",
            "message": exc.message,
            "detail": exc.framework_name,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "bad_request",
            "message": str(exc),
            "detail": None,
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
