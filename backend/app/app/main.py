from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.agents.orchestrator import ArchitectureAssistantOrchestrator
from app.schemas import AnalyzeResponse, RecommendResponse, RequirementRequest
from app.services.knowledge_base import (
    build_knowledge_graph,
    load_architecture_styles,
    load_course_knowledge,
    load_test_cases,
)
from app.services.llm import LLMConfigurationError, LLMServiceError
from app.services.llm_cache import LLMCache


app = FastAPI(
    title="软件架构风格智能助手",
    description="基于 DeepSeek LLM、Agent 协作和规则引擎的软件体系结构风格推荐系统。",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).resolve().parents[3]
STATIC_DIR = ROOT_DIR / "frontend" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_orchestrator() -> ArchitectureAssistantOrchestrator:
    return ArchitectureAssistantOrchestrator()


def safe_error_detail(exc: Exception) -> str:
    text = f"{type(exc).__name__}: {exc}"
    return text.encode("ascii", errors="backslashreplace").decode("ascii")


@app.get("/")
async def index() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail=f"Frontend entry not found: {index_path}")
    return FileResponse(index_path)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<rect width="64" height="64" rx="14" fill="#006241"/>'
        '<path d="M22 46 32 16l10 30h-7l-2-7h-8l-2 7h-7Zm5-13h10l-5-15-5 15Z" fill="#fff"/>'
        "</svg>"
    )
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/styles")
async def styles() -> list[dict]:
    return load_architecture_styles()


@app.get("/api/examples")
async def examples() -> list[dict]:
    return load_test_cases()


@app.get("/api/course-knowledge")
async def course_knowledge() -> dict:
    return load_course_knowledge()


@app.get("/api/knowledge-graph")
async def knowledge_graph() -> dict:
    return build_knowledge_graph()


@app.get("/api/cache/stats")
async def cache_stats() -> dict:
    return LLMCache().stats()


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: RequirementRequest) -> AnalyzeResponse:
    try:
        return await get_orchestrator().analyze(request.requirement)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail=f"LLM response schema validation failed: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal server error: {safe_error_detail(exc)}") from exc


@app.post("/api/recommend", response_model=RecommendResponse)
async def recommend(request: RequirementRequest) -> RecommendResponse:
    try:
        return await get_orchestrator().recommend(request.requirement)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail=f"LLM response schema validation failed: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal server error: {safe_error_detail(exc)}") from exc
