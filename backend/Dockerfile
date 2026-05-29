FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV TZ=Etc/UTC

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
	&& echo $TZ > /etc/timezone \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
	fluxbox \
	novnc \
	x11vnc \
	xvfb \
	&& rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/main.py ./main.py
COPY backend/entrypoint.sh ./entrypoint.sh
COPY avito_session_core.py ./avito_session_core.py

RUN chmod +x ./entrypoint.sh

EXPOSE 8000 6080

CMD ["./entrypoint.sh"]