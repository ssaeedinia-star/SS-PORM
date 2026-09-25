FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV HOME=/tmp
ENV XDG_CONFIG_HOME=/tmp

CMD ["sh", "-c", "mkdir -p /tmp/.gunicorn && gunicorn --bind 0.0.0.0:${PORT:-3000} --timeout 120 bootstrap:app"]
