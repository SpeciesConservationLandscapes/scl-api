import os

# local, dev, prod
ENVIRONMENT = os.environ.get("ENV")
if ENVIRONMENT:
    ENVIRONMENT = ENVIRONMENT.lower()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENVIRONMENT not in ("prod",)

if ENVIRONMENT in ("dev", "prod"):
    ALLOWED_HOSTS = [host.strip() for host in os.environ["ALLOWED_HOSTS"].split(",")]
else:
    ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "rest_framework_gis",
    "django_filters",
    "django_extensions",
    "api.apps.ApiConfig",
    "corsheaders",
    "django_countries",
    "tools",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "app.wsgi.application"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("api.auth_backends.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("DB_NAME") or "scl",
        "USER": os.environ.get("DB_USER") or "postgres",
        "PASSWORD": os.environ.get("DB_PASSWORD") or "postgres",
        "PORT": os.environ.get("DB_PORT") or "5432",
    }
}

if os.getenv('GAE_INSTANCE'):
    DATABASES['default']['HOST'] = '/cloudsql/' + os.environ.get("GCP_CLOUD_SQL_CONNECTION_STRING")
else:
    DATABASES['default']['HOST'] = os.environ.get("DB_HOST") or "api_db"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

if os.getenv('GAE_INSTANCE'):
    STATIC_URL = os.environ.get("GCP_DJANGO_STATIC_URL")
else:
    STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")

APPEND_SLASH = True
CORS_ORIGIN_ALLOW_ALL = True

EE_HII_ROOTDIR = "projects/HII/v1/"
EE_SCL_ROOTDIR = "projects/SCL/v1/"
EE_SERVICE_ACCOUNT_KEY = os.environ.get("SERVICE_ACCOUNT_KEY")
GCP_PROJECT_ID = "scl3-244715"
GCP_BUCKET_SCLS = "scl-pipeline"
GCP_BUCKET_BACKUP = "scl-backup"

API_AUDIENCE = os.environ.get("API_AUDIENCE")
API_SIGNING_SECRET = os.environ.get("API_SIGNING_SECRET")
ADMIN_API_CLIENT_ID = os.environ.get("ADMIN_API_CLIENT_ID")
ADMIN_API_CLIENT_SECRET = os.environ.get("ADMIN_API_CLIENT_SECRET")
ADMIN_API_AUDIENCE = os.environ.get("ADMIN_API_AUDIENCE")
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
