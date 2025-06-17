# 使用官方 Python 基礎映像檔含有Debian作業系統
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 升級 pip
RUN pip install --upgrade pip setuptools wheel

# 複製需求檔案並安裝依賴
COPY ./django-web-llm/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY ./django-web-llm /app/

# 將 app 目錄加入 Python 路徑
ENV PYTHONPATH=/app

# 複製啟動腳本
COPY ./docker-files-llm/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 執行啟動腳本
ENTRYPOINT ["/entrypoint.sh"]
