import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ij^*zz$7bd!#2&dhq_&5y+36@=&*8+m0nil9f2q8@_wu8q4$9w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
#DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',  # 跨域資源共享
    'app_top_keyword',
    'app_top_person',
    'app_top_ner',
    'app_user_keyword',
    'app_scchen',
    'app_user_keyword_association',
    'app_user_keyword_sentiment',
    'app_taipei_mayor',
    'app_correlation_analysis',
    'app_top_person_sqlalchemy_db',
    'app_top_person_db',
    'app_user_keyword_db',
    'app_user_keyword_llm_report',
    'app_poa_introduction',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', #跨站請求
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

# 資料庫設定postgres
# 這裡是使用docker-compose的時候使用的資料庫設定
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres', # Match POSTGRES_DB in docker-compose.yml
#         'USER': 'postgres', # Match POSTGRES_USER in docker-compose.yml
#         'PASSWORD': 'postgres', # Match POSTGRES_PASSWORD in docker-compose.yml
#         'HOST': 'db', # This should be the service name of the database container in docker-compose.yml
#         'PORT': 5432, # Default PostgreSQL port
#     }
# }

# 讀取環境變數
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# 允許所有跨站請求 跨域資源共享
CORS_ORIGIN_ALLOW_ALL = True



# Static files (CSS, JavaScript, Images)
# 我們置放靜態檔案在此目錄，在生產階段STATICFILES_DIRS會從這裡複製靜態檔案
STATIC_DIR = os.path.join(BASE_DIR, 'static') # 置放靜態檔案的目錄 Directory where static files are collected

# 生產或佈署階段 nginx須設定遇到URL前綴去STATIC_ROOT設定的目錄下去尋找靜態檔案
# STATIC_URL是靜態檔案的URL前綴，當瀏覽器請求靜態檔案時，會使用這個URL前綴
# Django runserver不會理會STATIC_URL的設定，只會取URL前綴之後的路徑的靜態檔案
# STATIC_URL = '/static/'  # URL prefix for static files
STATIC_URL = '/static/poa/'  # URL prefix for static files

# 生產或佈署階段
# 這裡是靜態檔案的收集目錄，當執行python manage.py collectstatic時，會去STATICFILES_DIRS定義的目錄去收集靜態檔案複製到這個目錄下
# nginx會去這個目錄下尋找靜態檔案
# 這裡是docker-compose的時候使用的靜態檔案設定
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# 生產或佈署階段
# 蒐集collectstatic時，去這裡定義的目錄蒐集靜態static檔案
# 若有新的檔案，需要重新製作新的容器，才會再去更新python manage.py collectstaticfiles
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    # BASE_DIR / 'static', # 這種寫法也可以
    # STATIC_DIR, # 這種寫法也可以
]

# Logging紀錄設定
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 保留 Django 內建 logger
    'formatters': {
        'simple': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {  # root logger 設定
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

'''
# how to show log in docker-compose
docker-compose logs -f web-poa
docker-compose logs -f web-poa --tail=100 # show last 100 lines of logs

# Example of how to use logging in your views.py or any other module
import logging
logger = logging.getLogger(__name__)

def my_view(request):
    logger.info("This is a test log message.")

'''