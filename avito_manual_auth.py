from avito_session_core import AvitoAuthBootstrap, build_config_from_env


def main() -> None:
    # Отдельный файл только для ручной авторизации и сохранения сессии.
    # Сценарий использования:
    # 1. Запустить этот файл.
    # 2. В открывшемся браузере вручную войти в аккаунт Avito.
    # 3. Вернуться в консоль и нажать Enter.
    # 4. Получить storage_state, cookies и постоянный профиль браузера.
    #
    # Для Ubuntu-сервера есть два практичных варианта:
    # - сделать первичный вход локально, затем перенести data/avito_storage_state.json
    #   и при необходимости data/avito_cookies.json на сервер;
    # - если сессия должна быть получена именно на сервере, запускать этот файл
    #   в графической сессии сервера через VNC, RDP/XRDP, noVNC или X11-forwarding.
    #
    # В полностью headless-режиме без окна браузера ручной логин невозможен.
    config = build_config_from_env()
    bootstrap = AvitoAuthBootstrap(config)
    bootstrap.authorize_and_save()


if __name__ == "__main__":
    main()