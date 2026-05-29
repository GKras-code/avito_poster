from __future__ import annotations

import json
import os
import platform
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from playwright.sync_api import (
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)


@dataclass
class AvitoAuthConfig:
    """Базовые настройки для запуска авторизации и сохранения сессии."""

    base_url: str = "https://www.avito.ru/"
    storage_state_path: Path = Path("data") / "avito_storage_state.json"
    cookies_path: Path = Path("data") / "avito_cookies.json"
    user_data_dir: Path = Path("data") / "avito_browser_profile"
    headless: bool = False
    slow_mo_ms: int = 150
    timeout_ms: int = 30_000
    browser_channel: Optional[str] = None


@dataclass
class AvitoProfileSnapshot:
    """Краткий слепок данных профиля для проверки авторизации."""

    profile_url: str
    display_name: str
    wallet_value: Optional[str]
    rating_value: Optional[str]


class AvitoAuthBootstrap:
    """Основа для авторизации на Avito и сохранения авторизованной сессии."""

    def __init__(self, config: Optional[AvitoAuthConfig] = None) -> None:
        self.config = config or AvitoAuthConfig()

    def authorize_and_save(self) -> None:
        """Открывает Avito в постоянном профиле, ждёт ручной авторизации и сохраняет сессию."""
        self._ensure_output_dirs()

        with sync_playwright() as playwright:
            context = self._open_persistent_context(playwright)
            page = context.pages[0] if context.pages else context.new_page()
            page.set_default_timeout(self.config.timeout_ms)
            page.goto(self.config.base_url, wait_until="domcontentloaded")

            self._prepare_login_flow(page)
            self._wait_for_manual_login(page)
            self._save_session(context)

            print("Сессия сохранена.")
            print(f"storage_state: {self.config.storage_state_path.resolve()}")
            print(f"cookies: {self.config.cookies_path.resolve()}")
            print(f"browser profile: {self.config.user_data_dir.resolve()}")

            context.close()

    def authorize_interactive_auto_save(
        self,
        timeout_seconds: int = 900,
        poll_interval_seconds: float = 2.0,
        progress_callback=None,
    ) -> bool:
        """Открывает браузер для ручного входа и автоматически сохраняет сессию после успешной авторизации.

        Сценарий: пользователь сам кликает кнопку входа, вводит логин/пароль,
        решает captcha и вводит SMS-код. Скрипт только отслеживает момент,
        когда страница перестаёт выглядеть как неавторизованная, и сохраняет сессию.
        """
        self._ensure_output_dirs()

        with sync_playwright() as playwright:
            context = self._open_persistent_context(playwright)
            page = context.pages[0] if context.pages else context.new_page()
            page.set_default_timeout(self.config.timeout_ms)
            page.goto(self.config.base_url, wait_until="domcontentloaded")
            self._prepare_login_flow(page)

            self._notify_progress(
                progress_callback,
                "running",
                "Браузер открыт. Выполните вход на Avito в появившемся окне.",
            )

            deadline = time.time() + timeout_seconds
            while time.time() < deadline:
                page.wait_for_timeout(int(poll_interval_seconds * 1000))

                if self._looks_authorized(page):
                    self._stabilize_page_after_manual_login(page)
                    self._save_session(context)
                    context.close()
                    self._notify_progress(
                        progress_callback,
                        "completed",
                        "Авторизация завершена, данные сессии сохранены.",
                    )
                    return True

            context.close()
            raise TimeoutError(
                "Время ожидания авторизации истекло. Попробуйте снова и завершите вход быстрее."
            )

    def check_saved_session(self) -> bool:
        """Возвращает True, если на странице профиля прочитались имя и рейтинг."""
        profile_snapshot = self.read_profile_snapshot()
        if profile_snapshot is None:
            return False

        return bool(profile_snapshot.display_name and profile_snapshot.rating_value)

    def read_profile_snapshot(self) -> Optional[AvitoProfileSnapshot]:
        """Открывает `/profile` и читает признаки авторизованного профиля."""
        with sync_playwright() as playwright:
            context = self.create_authorized_context(playwright)
            page = context.new_page()
            page.set_default_timeout(self.config.timeout_ms)
            page.goto(f"{self.config.base_url.rstrip('/')}/profile", wait_until="domcontentloaded")
            self._stabilize_page_after_manual_login(page)

            profile_sidebar = page.locator('div[data-marker="profile-sidebar"]')
            avatar = page.locator('div[data-marker="profile-sidebar-head/avatar"]')
            wallet_locator = page.locator('span[data-marker="sidebar-wallet-value"]')
            rating_locator = page.locator('meta[itemprop="ratingValue"]')

            profile_marker_found = self._wait_for_any_profile_marker(
                profile_sidebar,
                avatar,
                wallet_locator,
                rating_locator,
            )
            if not profile_marker_found:
                if self._looks_authorized(page):
                    print("Кнопка входа скрыта, но маркеры профиля не появились вовремя.")
                else:
                    print("Профиль не открылся: страница выглядит неавторизованной.")
                context.close()
                return None

            display_name = self._safe_text(avatar, attribute_name="title") or ""
            wallet_value = self._safe_text(wallet_locator)
            rating_value = self._safe_text(rating_locator, attribute_name="content")

            snapshot = AvitoProfileSnapshot(
                profile_url=page.url,
                display_name=display_name.strip(),
                wallet_value=wallet_value,
                rating_value=rating_value,
            )
            context.close()
            return snapshot

    def verify_additem_access(self) -> str:
        """Проверяет, что из сохранённой сессии доступен переход к размещению объявления."""
        with sync_playwright() as playwright:
            context = self.create_authorized_context(playwright)
            page = context.new_page()
            page.set_default_timeout(self.config.timeout_ms)
            page.goto(self.config.base_url, wait_until="commit")

            add_item_link = page.locator('a[href="/additem"]')
            add_item_link.first.wait_for(state="visible")
            add_item_link.first.click()

            self._stabilize_page_after_manual_login(page)
            page_text = self._extract_page_text(page)

            context.close()
            return page_text[:100]

    def create_authorized_context(self, playwright: Playwright) -> BrowserContext:
        """Создаёт новый контекст из уже сохранённой авторизованной сессии."""
        storage_state_path = self.config.storage_state_path
        if not storage_state_path.exists():
            raise FileNotFoundError(
                "Файл storage_state не найден. Сначала выполните authorize_and_save()."
            )

        launch_kwargs = {
            "headless": self.config.headless,
            "slow_mo": self.config.slow_mo_ms,
        }
        if self.config.browser_channel:
            launch_kwargs["channel"] = self.config.browser_channel

        browser = playwright.chromium.launch(**launch_kwargs)
        context = browser.new_context(storage_state=str(storage_state_path))
        context.set_default_timeout(self.config.timeout_ms)
        return context

    def _open_persistent_context(self, playwright: Playwright) -> BrowserContext:
        """Стартует постоянный профиль браузера для ручного пользовательского входа."""
        launch_kwargs = {
            "headless": self.config.headless,
            "slow_mo": self.config.slow_mo_ms,
            "args": ["--disable-gpu"],
        }

        if self.config.browser_channel:
            launch_kwargs["channel"] = self.config.browser_channel

        try:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.config.user_data_dir),
                locale="ru-RU",
                **launch_kwargs,
            )
        except Exception:
            self._reset_persistent_profile_dir()
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.config.user_data_dir),
                locale="ru-RU",
                **launch_kwargs,
            )

        context.set_default_timeout(self.config.timeout_ms)
        return context

    def _prepare_login_flow(self, page: Page) -> None:
        """Подготавливает ручной вход на странице Avito."""
        print("Открыта главная страница Avito в постоянном профиле браузера.")
        print("Сейчас сценарий рассчитан на полностью ручной вход.")
        print("После успешного входа нажмите Enter в консоли для сохранения сессии.")

    def _wait_for_manual_login(self, page: Page) -> None:
        """Ждёт ручной авторизации и даёт простой способ проверить результат."""
        print()
        print("После того как войдёте в аккаунт, вернитесь в консоль.")
        print("Нажмите Enter, чтобы сохранить текущую авторизованную сессию.")
        input()

        self._stabilize_page_after_manual_login(page)

    def _stabilize_page_after_manual_login(self, page: Page) -> None:
        """Мягко стабилизирует страницу после ручного входа."""
        try:
            page.wait_for_load_state("load", timeout=5_000)
        except PlaywrightTimeoutError:
            print("Не дождались состояния load, продолжаю без него.")

        try:
            page.wait_for_load_state("domcontentloaded")
        except PlaywrightTimeoutError:
            print("Не дождались состояния domcontentloaded, продолжаю без него.")

        try:
            page.wait_for_load_state("networkidle", timeout=5_000)
        except PlaywrightTimeoutError:
            print(
                "Страница продолжает фоновые запросы, сохраняю сессию без ожидания networkidle."
            )

    def _looks_authorized(self, page: Page) -> bool:
        """Если кнопка входа видна, считаем сессию неактивной."""
        login_button = page.locator('a[data-marker="header/login-button"]')
        return login_button.count() == 0

    def _wait_for_any_profile_marker(self, *locators) -> bool:
        """Ждёт любой устойчивый маркер профиля, полезно для headless/Linux сценариев."""
        for locator in locators:
            try:
                locator.first.wait_for(state="attached", timeout=5_000)
                return True
            except PlaywrightTimeoutError:
                continue

        return False

    def _safe_text(self, locator, attribute_name: Optional[str] = None) -> Optional[str]:
        """Читает текст или атрибут локатора, если элемент присутствует."""
        if locator.count() == 0:
            return None

        target = locator.first
        try:
            if attribute_name:
                value = target.get_attribute(attribute_name)
            else:
                value = target.inner_text(timeout=2_000)
        except PlaywrightTimeoutError:
            return None

        if value is None:
            return None

        normalized_value = " ".join(value.split())
        return normalized_value or None

    def _notify_progress(self, callback, status: str, message: str) -> None:
        if callback is not None:
            callback(status, message)

    def _extract_page_text(self, page: Page) -> str:
        """Возвращает очищенный текст страницы для простой диагностики."""
        body = page.locator("body")
        body.wait_for(state="attached", timeout=5_000)
        raw_text = body.inner_text(timeout=5_000)
        normalized_text = " ".join(raw_text.split())
        return normalized_text

    def _save_session(self, context: BrowserContext) -> None:
        """Сохраняет полное состояние контекста и отдельный JSON с cookies."""
        storage_state_path = self.config.storage_state_path
        cookies_path = self.config.cookies_path

        context.storage_state(path=str(storage_state_path))

        cookies = context.cookies()
        cookies_path.write_text(
            json.dumps(cookies, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _ensure_output_dirs(self) -> None:
        self.config.storage_state_path.parent.mkdir(parents=True, exist_ok=True)
        self.config.cookies_path.parent.mkdir(parents=True, exist_ok=True)

    def _reset_persistent_profile_dir(self) -> None:
        """Удаляет повреждённый профиль браузера и создаёт новый пустой каталог."""
        profile_dir = self.config.user_data_dir
        if profile_dir.exists():
            shutil.rmtree(profile_dir, ignore_errors=True)
        profile_dir.mkdir(parents=True, exist_ok=True)


def build_config_from_env() -> AvitoAuthConfig:
    """Позволяет переопределять базовые настройки через переменные окружения."""
    browser_channel = os.getenv("AVITO_BROWSER_CHANNEL") or None
    default_channel = _default_browser_channel(browser_channel)
    default_headless = _default_headless_mode()

    return AvitoAuthConfig(
        headless=_env_flag("AVITO_HEADLESS", default_headless),
        browser_channel=default_channel,
        storage_state_path=Path(
            os.getenv("AVITO_STORAGE_STATE_PATH", "data/avito_storage_state.json")
        ),
        cookies_path=Path(os.getenv("AVITO_COOKIES_PATH", "data/avito_cookies.json")),
        user_data_dir=Path(
            os.getenv("AVITO_USER_DATA_DIR", "data/avito_browser_profile")
        ),
    )


def _default_browser_channel(explicit_channel: Optional[str]) -> Optional[str]:
    """Подбирает разумный браузер по умолчанию для ручного входа."""
    if explicit_channel is not None:
        return explicit_channel

    system_name = platform.system().lower()
    if system_name == "windows":
        return "chrome"

    return None


def _default_headless_mode() -> bool:
    """На Linux-сервере без DISPLAY по умолчанию нужен headless-режим."""
    system_name = platform.system().lower()
    has_display = bool(os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))
    return system_name == "linux" and not has_display


def _env_flag(name: str, default: bool) -> bool:
    """Читает булевый флаг из окружения с запасом по форматам значений."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    normalized = raw_value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}