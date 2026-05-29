from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from avito_session_core import AvitoAuthBootstrap, build_config_from_env


class AvitoAuthStatusResponse(BaseModel):
    authorized: bool
    display_name: str | None = None
    rating_value: str | None = None
    page_url: str | None = None
    page_title: str | None = None
    screenshot_base64: str | None = None


app = FastAPI(title="Avito Poster API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/avito/auth-status", response_model=AvitoAuthStatusResponse)
def avito_auth_status() -> AvitoAuthStatusResponse:
    bootstrap = AvitoAuthBootstrap(build_config_from_env())
    inspection = bootstrap.inspect_profile_page()
    snapshot = inspection.snapshot

    if snapshot is None:
        return AvitoAuthStatusResponse(
            authorized=False,
            page_url=inspection.page_url,
            page_title=inspection.page_title,
            screenshot_base64=inspection.screenshot_base64,
        )

    authorized = bool(snapshot.display_name and snapshot.rating_value)
    return AvitoAuthStatusResponse(
        authorized=authorized,
        display_name=snapshot.display_name or None,
        rating_value=snapshot.rating_value or None,
        page_url=inspection.page_url,
        page_title=inspection.page_title,
        screenshot_base64=inspection.screenshot_base64,
    )