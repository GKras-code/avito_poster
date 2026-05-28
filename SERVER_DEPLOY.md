# Ubuntu Server Launch Guide

Этот файл описывает, как поднять Vue-интерфейс на Ubuntu-сервере `89.169.38.182` через Docker.

## Локальный запуск фронта в VS Code

Откройте проект в VS Code и перейдите в папку `web`.

Если зависимости ещё не установлены:

```bash
cd web
npm install
```

Для Windows PowerShell: если команда `npm` блокируется политикой выполнения, используйте `npm.cmd`.

Запуск dev-сервера:

```bash
cd web
npm run dev
```

Для Windows PowerShell при необходимости:

```bash
cd web
npm.cmd run dev
```

После запуска Vite покажет локальный адрес, обычно:

```text
http://localhost:5173/
```

Тестовые данные для входа:

```text
login: user
password: test
```

Production-сборка локально проверяется так:

```bash
cd web
npm run build
```

Для Windows PowerShell при необходимости:

```bash
cd web
npm.cmd run build
```

## 1. Подключение к серверу

```bash
ssh root@89.169.38.182
```

## 2. Установка Docker и Docker Compose plugin

```bash
apt update
apt install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable docker
systemctl start docker
```

## 3. Подготовка деплоя через Git

Если вы хотите обновлять сервер через `git pull`, на сервере проект должен быть именно git-репозиторием.

### Вариант A. Репозиторий ещё не клонирован на сервер

```bash
cd ~
git clone git@github.com:GKras-code/avito_poster.git avito_poster
cd ~/avito_poster
```

Используем SSH-вариант, потому что ключи уже лежат на сервере в `~/.ssh`.

Репозиторий:

```text
git@github.com:GKras-code/avito_poster.git
```

Перед первым `git clone` проверьте права и доступность ключей:

```bash
cd ~/.ssh
ls -la
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
ssh -T git@github.com
```

Если ключ называется иначе, подставьте фактическое имя файла приватного и публичного ключа.

Проверка:

```bash
cd ~/avito_poster
git remote -v
git branch
```

### Вариант B. Папка уже есть на сервере, но была загружена вручную

В таком виде `git pull` не заработает, пока папка не станет git-репозиторием. Самый чистый путь:

```bash
cd ~
mv avito_poster avito_poster_backup
git clone git@github.com:GKras-code/avito_poster.git avito_poster
```

После этого при необходимости перенесите нужные локальные файлы из `avito_poster_backup` в новый каталог.

Если вы точно понимаете, что делаете, можно инициализировать git вручную внутри существующей папки, но для серверного деплоя обычно надёжнее сделать новый `git clone`.

## 4. Сборка и запуск контейнера

```bash
cd ~/avito_poster
docker compose up -d --build
```

## 5. Проверка, что сайт поднялся

```bash
docker compose ps
docker compose logs -n 100 avito-web
curl http://127.0.0.1
```

После этого сайт должен открываться в браузере по адресу:

```text
http://89.169.38.182/
```

Тестовые данные для входа:

```text
login: user
password: test
```

## 6. Обновление после изменений

Если проект на сервере подключён к удалённому git-репозиторию, рабочий цикл такой:

```bash
cd ~/avito_poster
git pull
docker compose down
docker compose up -d --build
```

Можно короче без полного `down`, если достаточно пересборки:

```bash
cd ~/avito_poster
git pull
docker compose up -d --build
```

Если сервер спросит подтверждение нового хоста GitHub при первом подключении, ответьте `yes`.

Если хотите сначала проверить, что именно приедет с сервера:

```bash
cd ~/avito_poster
git status
git pull
git log -1 --oneline
```

## 7. Полезные команды

Остановить контейнер:

```bash
docker compose down
```

Посмотреть состояние:

```bash
docker compose ps
```

Посмотреть логи:

```bash
docker compose logs -f avito-web
```

Посмотреть текущий коммит на сервере:

```bash
git log -1 --oneline
```

Проверить, какой удалённый репозиторий привязан:

```bash
git remote -v
```

## Примечание

Я подготовил все файлы для деплоя, но сам разместить проект на сервере из этой сессии не могу, потому что у меня нет прямого SSH-доступа к `89.169.38.182`. С текущими файлами запуск выполняется указанными командами.