import os
from pathlib import Path
from data import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "%=t^sd84zv9x!l(y%-d%gla)x^w%lk(o)ewr=%g7_p+qz6m#$-"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# CSRF
# Comma-separated list, e.g. "https://bot.example.com,https://admin.example.com"
_csrf_trusted_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "").strip()
if _csrf_trusted_origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_trusted_origins.split(",") if o.strip()]

# Application definition

INSTALLED_APPS = [
    "unfold",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'backend',
]

# Unfold (modern Django admin UI)
UNFOLD = {
    "SITE_TITLE": os.getenv("ADMIN_SITE_TITLE", "Tushlikbot"),
    "SITE_HEADER": os.getenv("ADMIN_SITE_HEADER", "Tushlikbot Admin"),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'admin.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': config.DATABASE,
#         'USER': config.PGUSER,
#         'PASSWORD': config.PGPASSWORD,
#         'HOST': "localhost",
#         'PORT': '5432',
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if os.getenv("POSTGRES_HOST"):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", config.DATABASE),
        "USER": os.getenv("POSTGRES_USER", config.PGUSER),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", config.PGPASSWORD),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'admin/static')
]
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
