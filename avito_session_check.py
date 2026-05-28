from avito_session_core import AvitoAuthBootstrap, build_config_from_env


def main() -> None:
    # Отдельный файл для проверки уже сохранённой сессии.
    # Сценарий использования:
    # 1. Сначала получить storage_state через avito_manual_auth.py.
    # 2. Затем запустить этот файл.
    # 3. Скрипт откроет Avito из сохранённой сессии и сообщит, активна ли она.
    config = build_config_from_env()
    bootstrap = AvitoAuthBootstrap(config)
    profile_snapshot = bootstrap.read_profile_snapshot()
    is_authorized = bootstrap.check_saved_session()

    if is_authorized and profile_snapshot is not None:
        print(f"Профиль открыт: {profile_snapshot.profile_url}")
        print(f"Имя профиля: {profile_snapshot.display_name}")
        if profile_snapshot.rating_value:
            print(f"Рейтинг профиля: {profile_snapshot.rating_value}")
        if profile_snapshot.wallet_value:
            print(f"Баланс кошелька: {profile_snapshot.wallet_value}")
        print(f"Результат проверки: {is_authorized}")
        print("Проверка завершена успешно.")
    else:
        print("Результат проверки: False")
        raise SystemExit("Сохранённая сессия неактивна. Нужна повторная ручная авторизация.")


if __name__ == "__main__":
    main()