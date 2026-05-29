from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

from fastapi import FastAPI
from fastapi import File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from avito_session_core import AvitoAuthBootstrap, build_config_from_env


ROOT_DIR = Path(__file__).resolve().parent
LOCAL_AUTH_BUNDLE_DIR = ROOT_DIR / "local_auth_bundle"
LOCAL_AUTH_EXE_PATH = LOCAL_AUTH_BUNDLE_DIR / "AvitoLocalAuth.exe"
LOCAL_AUTH_BUNDLE_FILES = [
    "avito_local_auth.py",
    "requirements.txt",
    "README.md",
    "build_windows_exe.ps1",
]
EXPECTED_AUTH_ARCHIVE_FILES = {
    "avito_storage_state.json",
    "avito_cookies.json",
}


class AvitoAuthStatusResponse(BaseModel):
    authorized: bool
    display_name: str | None = None
    rating_value: str | None = None
    message: str | None = None


class AvitoSessionUploadResponse(BaseModel):
    success: bool
    message: str


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
    try:
        snapshot = bootstrap.read_profile_snapshot()
    except FileNotFoundError:
        return AvitoAuthStatusResponse(
            authorized=False,
            message=(
                "Данные авторизации Avito ещё не загружены. Нажмите 'Авторизоваться на Avito', "
                "скачайте локальный скрипт, выполните вход и загрузите архив обратно на сайт."
            ),
        )
    except Exception as error:
        return AvitoAuthStatusResponse(
            authorized=False,
            message=f"Не удалось проверить авторизацию Avito: {error}",
        )

    if snapshot is None:
        return AvitoAuthStatusResponse(
            authorized=False,
            message="Сессия Avito не подтверждена. Загрузите новый архив авторизации.",
        )

    authorized = bool(snapshot.display_name and snapshot.rating_value)
    return AvitoAuthStatusResponse(
        authorized=authorized,
        display_name=snapshot.display_name or None,
        rating_value=snapshot.rating_value or None,
        message=(
            "Авторизация подтверждена." if authorized else "Профиль открылся, но данные авторизации неполные."
        ),
    )


@app.get("/api/avito/auth-package/download")
def download_avito_auth_package() -> StreamingResponse:
    if LOCAL_AUTH_EXE_PATH.exists():
        exe_bytes = LOCAL_AUTH_EXE_PATH.read_bytes()
        exe_headers = {"Content-Disposition": 'attachment; filename="AvitoLocalAuth.exe"'}
        return StreamingResponse(io.BytesIO(exe_bytes), media_type="application/octet-stream", headers=exe_headers)

    missing_files = [name for name in LOCAL_AUTH_BUNDLE_FILES if not (LOCAL_AUTH_BUNDLE_DIR / name).exists()]
    if missing_files:
        raise HTTPException(
            status_code=500,
            detail=f"Пакет локальной авторизации неполон: {', '.join(missing_files)}",
        )

    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_name in LOCAL_AUTH_BUNDLE_FILES:
            archive.write(LOCAL_AUTH_BUNDLE_DIR / file_name, arcname=file_name)

    archive_buffer.seek(0)
    headers = {"Content-Disposition": 'attachment; filename="avito-local-auth-bundle.zip"'}
    return StreamingResponse(archive_buffer, media_type="application/zip", headers=headers)


@app.post("/api/avito/auth-package/upload", response_model=AvitoSessionUploadResponse)
async def upload_avito_auth_package(file: UploadFile = File(...)) -> AvitoSessionUploadResponse:
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Нужен zip-архив с локальной сессией Avito.")

    archive_bytes = await file.read()
    try:
        archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    except zipfile.BadZipFile as error:
        raise HTTPException(status_code=400, detail="Файл не является корректным zip-архивом.") from error

    extracted_files: dict[str, bytes] = {}
    with archive:
        for entry in archive.infolist():
            if entry.is_dir():
                continue

            target_name = Path(entry.filename).name
            if target_name in EXPECTED_AUTH_ARCHIVE_FILES and target_name not in extracted_files:
                extracted_files[target_name] = archive.read(entry)

    missing_files = EXPECTED_AUTH_ARCHIVE_FILES.difference(extracted_files)
    if missing_files:
        raise HTTPException(
            status_code=400,
            detail=f"В архиве не хватает файлов авторизации: {', '.join(sorted(missing_files))}",
        )

    for json_file_name, json_bytes in extracted_files.items():
        try:
            json.loads(json_bytes.decode("utf-8"))
        except Exception as error:
            raise HTTPException(
                status_code=400,
                detail=f"Файл {json_file_name} содержит некорректный JSON.",
            ) from error

    config = build_config_from_env()
    config.storage_state_path.parent.mkdir(parents=True, exist_ok=True)
    config.storage_state_path.write_bytes(extracted_files["avito_storage_state.json"])
    config.cookies_path.write_bytes(extracted_files["avito_cookies.json"])

    return AvitoSessionUploadResponse(
        success=True,
        message="Архив авторизации загружен. Теперь можно проверить сессию Avito на сервере.",
    )