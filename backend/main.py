from __future__ import annotations

import os
import platform
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from avito_session_core import AvitoAuthBootstrap, build_config_from_env


class AvitoAuthStatusResponse(BaseModel):
    authorized: bool
    display_name: str | None = None
    rating_value: str | None = None
    message: str | None = None


class AvitoInteractiveAuthResponse(BaseModel):
    status: str
    message: str
    authorized: bool = False


app = FastAPI(title="Avito Poster API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InteractiveAuthManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._status = "idle"
        self._message = "Авторизация ещё не запускалась."
        self._authorized = False

    def start(self) -> AvitoInteractiveAuthResponse:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return self.snapshot()

            if self._display_is_required_but_missing():
                self._status = "error"
                self._message = (
                    "Backend запущен без графического DISPLAY. Для интерактивной авторизации нужен браузер на хосте backend "
                    "или отдельный VNC/noVNC слой."
                )
                self._authorized = False
                return self.snapshot()

            self._status = "starting"
            self._message = "Подготавливаем браузер для авторизации Avito."
            self._authorized = False
            self._thread = threading.Thread(target=self._run_flow, daemon=True)
            self._thread.start()
            return self.snapshot()

    def snapshot(self) -> AvitoInteractiveAuthResponse:
        return AvitoInteractiveAuthResponse(
            status=self._status,
            message=self._message,
            authorized=self._authorized,
        )

    def _run_flow(self) -> None:
        try:
            config = build_config_from_env()
            config.headless = False
            bootstrap = AvitoAuthBootstrap(config)
            bootstrap.authorize_interactive_auto_save(progress_callback=self._set_status)

            snapshot = bootstrap.read_profile_snapshot()
            authorized = bool(snapshot and snapshot.display_name and snapshot.rating_value)
            with self._lock:
                self._status = "completed"
                self._message = "Сессия Avito сохранена и готова к использованию."
                self._authorized = authorized
        except Exception as error:
            with self._lock:
                self._status = "error"
                self._message = str(error)
                self._authorized = False

    def _set_status(self, status: str, message: str) -> None:
        with self._lock:
            self._status = status
            self._message = message

    def _display_is_required_but_missing(self) -> bool:
        if platform.system().lower() != "linux":
            return False

        return not bool(os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))


interactive_auth_manager = InteractiveAuthManager()


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
                "Данные авторизации Avito ещё не сохранены. Сначала нажмите кнопку "
                "'Авторизоваться на Avito', завершите вход и дождитесь сохранения сессии."
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
            message=(
                "Сессия Avito не подтверждена. Если вы ещё не входили, нажмите "
                "'Авторизоваться на Avito' и пройдите вход в браузере."
            ),
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


@app.post("/api/avito/auth/start", response_model=AvitoInteractiveAuthResponse)
def start_avito_auth() -> AvitoInteractiveAuthResponse:
    return interactive_auth_manager.start()


@app.get("/api/avito/auth/progress", response_model=AvitoInteractiveAuthResponse)
def avito_auth_progress() -> AvitoInteractiveAuthResponse:
    return interactive_auth_manager.snapshot()