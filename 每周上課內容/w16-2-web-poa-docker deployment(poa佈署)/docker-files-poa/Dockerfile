# 使用官方 Python 基礎映像檔含有Debian作業系統
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 升級 pip
RUN pip install --upgrade pip setuptools wheel

# 複製專案檔案
COPY django-web-poa /app/

# 複製需求檔案並安裝依賴
# 
COPY django-web-poa/requirements.txt /app/
# 使用 --no-cache-dir 參數避免緩存
# 這樣可以確保每次都從最新的源安裝依賴
# 安裝環境的依賴
RUN pip install --no-cache-dir -r requirements.txt

# 將 app 目錄加入 Python 路徑
ENV PYTHONPATH=/app

# 複製啟動腳本 指定從根路徑的完整路徑
COPY docker-files-poa/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 執行啟動腳本
ENTRYPOINT ["/entrypoint.sh"]
