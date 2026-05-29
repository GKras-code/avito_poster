from __future__ import annotations

import json
import platform
import zipfile
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


BASE_URL = "https://www.avito.ru/"
OUTPUT_DIR = Path("avito_auth_output")
PROFILE_DIR = OUTPUT_DIR / "browser_profile"
STORAGE_STATE_PATH = OUTPUT_DIR / "avito_storage_state.json"
COOKIES_PATH = OUTPUT_DIR / "avito_cookies.json"
ARCHIVE_PATH = Path("avito_auth_bundle.zip")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    print("Откроется браузер Chromium. Выполните вход на Avito вручную.")
    print("После завершения входа вернитесь в консоль и нажмите Enter.")

    with sync_playwright() as playwright:
        context = _launch_local_browser(playwright)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded")

        input()

        try:
            page.goto(f"{BASE_URL.rstrip('/')}/profile", wait_until="domcontentloaded")
            page.wait_for_load_state("load", timeout=5_000)
        except PlaywrightTimeoutError:
            pass

        context.storage_state(path=str(STORAGE_STATE_PATH))
        COOKIES_PATH.write_text(
            json.dumps(context.cookies(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        context.close()

    with zipfile.ZipFile(ARCHIVE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(STORAGE_STATE_PATH, arcname=STORAGE_STATE_PATH.name)
        archive.write(COOKIES_PATH, arcname=COOKIES_PATH.name)

    print(f"Готово. Загрузите архив на сайт: {ARCHIVE_PATH.resolve()}")


def _launch_local_browser(playwright):
    launch_options = {
        "user_data_dir": str(PROFILE_DIR),
        "headless": False,
        "locale": "ru-RU",
        "slow_mo": 100,
    }

    for channel in _preferred_browser_channels():
        try:
            print(f"Пробую открыть локальный браузер через канал: {channel}")
            return playwright.chromium.launch_persistent_context(
                channel=channel,
                **launch_options,
            )
        except Exception:
            continue

    print("Локальный Chrome/Edge не найден, пробую встроенный Chromium Playwright.")
    return playwright.chromium.launch_persistent_context(**launch_options)


def _preferred_browser_channels() -> list[str]:
    if platform.system().lower() == "windows":
        return ["msedge", "chrome"]

    return ["chrome"]


if __name__ == "__main__":
    main()