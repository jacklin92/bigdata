import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ij^*zz$7bd!#2&dhq_&5y+36@=&*8+m0nil9f2q8@_wu8q4$9w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # App CORS跨域資源共享App
    'corsheaders',
    
    # GPT模型應用
    'app_llm_classifier',
    'app_ollama_usage',
    
    # Bert模型應用
    'app_sentiment_bert',
    'app_news_classification_bert',
    # LLM introduction
    'app_llm_introduction',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # allow CORS #允許跨站請求(跨域資源共享)
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'website_configs.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'website_configs.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Allow CORS  #允許所有跨站請求(跨域資源共享)
CORS_ORIGIN_ALLOW_ALL = True


# Force script name for URL prefixing when behind reverse proxy
# 當Django應用部署在Nginx或Apache等反向代理伺服器後面時，可能需要設定URL前綴，用來導向不同的應用程式
# 這裡設定的前綴會影響到所有的URL路由，確保在Nginx或Apache等伺服器上也有相同的設定
# FORCE_SCRIPT_NAME = '/llm/'


# 生產或佈署階段 nginx須設定遇到URL前綴去STATIC_ROOT設定的目錄下去尋找靜態檔案
# Django 會解析HTML模板的{%static 'img/logo.png'%}的路徑
# STATIC_URL是靜態檔案的URL前綴，當瀏覽器請求靜態檔案時，會使用這個URL前綴
# Django runserver會解析STATIC_URL的設定，但只會取URL前綴之後的路徑的靜態檔案
# 生產階段:nginx會解析STATIC_URL的設定，已經有先設定好對應的路徑，到對應的路徑((STATIC_ROOT)去取得靜態檔案
# STATIC_URL = '/static/' # URL prefix for static files
STATIC_URL = '/static/llm/' # URL prefix for static files


# 生產佈署階段會將STATICFILES_DIRS的靜態檔案收集到 STATIC_ROOT置放
# 這裡是靜態檔案的收集目錄，當執行python manage.py collectstatic時，會去STATICFILES_DIRS定義的目錄去收集靜態檔案複製到這個目錄下
# nginx會去這個目錄下尋找靜態檔案
# 這裡是docker-compose的時候使用的靜態檔案設定
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/llm') # 這種寫法也可以，會將靜態檔案放在 staticfiles/llm 資料夾下

# Static files (CSS, JavaScript, Images)
# 靜態檔案的目錄，這裡是放置靜態檔案的目錄，Django會自動去這個目錄尋找靜態檔案
# 將所有靜態檔案放在專案根目錄 static/ 資料夾
# 在STATICFILES_DIRS中必須指定這個用來蒐集靜態檔案的的路徑
STATIC_DIR = os.path.join(BASE_DIR, 'static') # 置放靜態檔案的目錄 Directory where static files are collected

# 生產或佈署階段
# 蒐集collectstatic時，去這裡定義的目錄蒐集靜態static檔案
# 若有新的檔案，需要重新製作新的容器，才會再去更新python manage.py collectstaticfiles
# 生產佈署階段會將STATICFILES_DIRS的靜態檔案收集到 STATIC_ROOT置放
STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, "static"),
    # BASE_DIR / 'static', # 這種寫法也可以
    STATIC_DIR, # 這種寫法也可以
    # 可加上其它你置放靜態檔案的目錄
]
