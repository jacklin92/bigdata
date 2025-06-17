# 以下是將 Django 專案使用 Docker Compose 佈署的主要步驟，包含 Nginx、Gunicorn 和 PostgreSQL:

## 1. 建立專案結構

確保你的專案結構類似如下:

```
project_directory/
├── django_app/         # Django 專案程式碼
├── nginx/              # Nginx 設定檔
├── docker-compose.yml  # Docker Compose 配置文件
├── Dockerfile          # Django 應用程式的 Dockerfile
└── requirements.txt    # Django 專案依賴
```

## 2. 建立 Django 應用的 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY ./django_app /app/

RUN python manage.py collectstatic --noinput
```

## 3. 編寫 Nginx 設定檔

```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    
    location /static/ {
        alias /app/static/;
    }
    
    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 4. 建立 Docker Compose 文件

```yaml
version: '3'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=django_db
  
  web:
    build: .
    command: gunicorn django_project.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./django_app:/app
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/django_db
      - DEBUG=False
  
  nginx:
    image: nginx:1.21
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

## 5. 修改 Django 設定檔

確保你的 Django 設定檔 (`settings.py`) 適合生產環境且支援 PostgreSQL：

```python
# 資料庫設定
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

# 靜態檔案設定
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 6. 啟動 Docker Compose

```bash
docker-compose build
docker-compose up -d
```

## 7. 執行數據庫遷移

```bash
docker-compose exec web python manage.py migrate
```

## 8. 創建超級用戶 (選擇性)

```bash
docker-compose exec web python manage.py createsuperuser
```

這樣就完成了使用 Docker Compose 佈署 Django 專案的基本步驟，包括 Nginx 作為前端代理伺服器、Gunicorn 作為 WSGI 應用伺服器，以及 PostgreSQL 作為資料庫。