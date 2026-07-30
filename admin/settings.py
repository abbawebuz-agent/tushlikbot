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
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_trusted_origins.split(",") if o.strip()] if _csrf_trusted_origins else []

# Helpful default for local testing (e.g. http://localhost:8080)
if not os.getenv("PUBLIC_BASE_URL"):
    port = os.getenv("INTERNAL_NGINX_PORT", "8080")
    CSRF_TRUSTED_ORIGINS.extend(
        [
            f"http://localhost:{port}",
            f"http://127.0.0.1:{port}",
        ]
    )

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

INSTALLED_APPS = [
    "unfold",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'backend.apps.BackendConfig',
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

# --- Static files on S3-compatible storage (optional) ---
# Enabled only when USE_S3_STATIC is truthy AND the required credentials are set.
# When disabled, static files keep using the local STATIC_ROOT above.
USE_S3_STATIC = os.getenv("USE_S3_STATIC", "").strip().lower() in ("1", "true", "yes", "on")

if USE_S3_STATIC:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    # Custom endpoint for S3-compatible providers (MinIO, Yandex, R2, VK Cloud, ...)
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL") or None
    # Explicit region. Default "auto" (valid for Cloudflare R2) so boto3 does NOT
    # fall back to the host's AWS_REGION/AWS_DEFAULT_REGION (Railway injects e.g.
    # "sjc", which R2 rejects with InvalidRegionName). Set a real region for AWS/Yandex.
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME") or "auto"
    # Optional CDN / public domain in front of the bucket (no scheme, e.g. "cdn.example.com").
    # Be forgiving: strip an accidental scheme/trailing slash so we don't emit
    # broken URLs like "https://https//pub-....r2.dev/...".
    _custom_domain = (os.getenv("AWS_S3_CUSTOM_DOMAIN") or "").strip()
    _custom_domain = _custom_domain.split("://", 1)[-1].strip("/")
    AWS_S3_CUSTOM_DOMAIN = _custom_domain or None
    # addressing style: "virtual" (bucket.host) or "path" (host/bucket, common for MinIO)
    AWS_S3_ADDRESSING_STYLE = os.getenv("AWS_S3_ADDRESSING_STYLE") or None

    # Public, cacheable, no signed URLs for static assets.
    AWS_QUERYSTRING_AUTH = False
    # No object ACL by default: modern providers (Cloudflare R2, AWS with ACLs
    # disabled) don't use ACLs — public read is granted at the bucket level
    # (R2: public bucket + r2.dev/custom domain). Set AWS_S3_DEFAULT_ACL=public-read
    # only for providers that require per-object ACLs (e.g. classic Tigris/MinIO).
    _acl = os.getenv("AWS_S3_DEFAULT_ACL", "").strip()
    AWS_DEFAULT_ACL = _acl or None
    AWS_S3_FILE_OVERWRITE = True
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

    # Prefix inside the bucket where collectstatic uploads files.
    STATIC_LOCATION = os.getenv("AWS_STATIC_LOCATION", "static").strip("/")

    _s3_options = {
        "bucket_name": AWS_STORAGE_BUCKET_NAME,
        "location": STATIC_LOCATION,
        "querystring_auth": AWS_QUERYSTRING_AUTH,
        "default_acl": AWS_DEFAULT_ACL,
        "file_overwrite": AWS_S3_FILE_OVERWRITE,
        "object_parameters": AWS_S3_OBJECT_PARAMETERS,
        "access_key": AWS_ACCESS_KEY_ID,
        "secret_key": AWS_SECRET_ACCESS_KEY,
        "endpoint_url": AWS_S3_ENDPOINT_URL,
        "region_name": AWS_S3_REGION_NAME,
        "custom_domain": AWS_S3_CUSTOM_DOMAIN,
        "addressing_style": AWS_S3_ADDRESSING_STYLE,
    }
    # Drop unset keys so django-storages/boto3 fall back to their own defaults.
    _s3_options = {k: v for k, v in _s3_options.items() if v is not None}

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": _s3_options,
        },
    }

    # STATIC_URL is still required by Django; point it at the bucket/CDN so any
    # code reading settings.STATIC_URL directly gets a correct base URL.
    if AWS_S3_CUSTOM_DOMAIN:
        STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"
    elif AWS_S3_ENDPOINT_URL:
        STATIC_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/{STATIC_LOCATION}/"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
    },
}
