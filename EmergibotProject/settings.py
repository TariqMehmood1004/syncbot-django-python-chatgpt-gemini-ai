import os
from pathlib import Path
import requests
from decouple import config



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-s)mx(#@%6o95p+_ix#agzm9%4#yw+1!z0fvl$sch!xao8x^g3!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

API_BASE_URL = "http://localhost:8000/api/v2"
API_AUTH_TOKEN = "FuvdsJQxeTeMfTlR7KVYbTiAQ0QnGRJPIgCG0S1D"


CSRF_COOKIE_SECURE = False  # Set to True for production if using HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
]

GEMINI_API_KEY = config('GEMINI_API_KEY', default='your-gemini-api-key')

ENVIRONMENT = "development"

if ENVIRONMENT == "development":
    ALLOWED_HOSTS = ['*']
elif ENVIRONMENT == "production":
    ALLOWED_HOSTS = ['Your Production Domain']
else:
    ALLOWED_HOSTS = ['*']


DJANGO_ALLOW_ASYNC_UNSAFE = True
SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'whitenoise.runserver_nostatic',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    "django_browser_reload",
    'rest_framework',
    'EmergibotApp',
    'maintenance_mode',
    'django_htmx',
    'channels',
    'services',
    'logs',
    'humanize',
]

# Configure DRF Default Authentication Classes
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # Token Authentication
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Restrict access to authenticated users
    ],
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

MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']
MIDDLEWARE += ['django_htmx.middleware.HtmxMiddleware']
MIDDLEWARE += ['EmergibotApp.middleware.chat_session.ChatSessionMiddleware']
MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]

ROOT_URLCONF = 'EmergibotProject.urls'

TEMPLATES_DIR = BASE_DIR / 'templates'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'EmergibotProject.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# Email settings - CREDENTIALS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'TariqMehmood@thedarkbytes.com'  # Your Outlook email
EMAIL_HOST_PASSWORD = 'Y@611026051774uq'  # Your Outlook email password or app password
DEFAULT_FROM_EMAIL = 'TariqMehmood@thedarkbytes.com'  # Default sender email
ADMIN_DEFAULT_FROM_EMAIL = 'info@thedarkbytes.com'

# Internationalization
def get_current_timezone():
    try:
        # Use an external API to determine the location based on IP
        response = requests.get("http://ip-api.com/json/")
        response.raise_for_status()
        data = response.json()
        timezone = data.get("timezone", "UTC")  # Fallback to UTC
        print(f"Detected Time Zone: {timezone}")
        return timezone
    except Exception as e:
        print(f"Error detecting timezone: {e}")
        return "UTC"

LANGUAGE_CODE = 'en-us'
TIME_ZONE = get_current_timezone()  # Dynamically detect and set the time zone
USE_I18N = True
USE_TZ = True


## MAINTENANCE MODE
MAINTENANCE_MODE = False # True/False/None
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True   # True/False/None
MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = True # True/False/None
MAINTENANCE_MODE_TEMPLATE = "503.html"
MAINTENANCE_MODE_STATUS_CODE = 503
MAINTENANCE_MODE_RETRY_AFTER = 3600 # 1 hour
## MAINTENANCE MODE


## STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static',]

if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
## STATIC FILES


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
