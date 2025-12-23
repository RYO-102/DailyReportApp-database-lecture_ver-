FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /app

# 必要なパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードのコピー
COPY . .

# サーバー起動
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]