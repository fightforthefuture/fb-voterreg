import os
import sys
from os import environ

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECT_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
def rel(*x):
    return os.path.join(PROJECT_ROOT, *x)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite'
    }
}

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = False
MEDIA_ROOT = rel('media')
MEDIA_URL = '/media/'
STATIC_ROOT = rel('collected')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    rel('static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = '(*542w29r^lq8_zi+jq6j31semg(u8-+vv$dhqwm9d9p5u61s%'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    "middleware.FacebookMiddleware"
)

ROOT_URLCONF = 'voterreg.urls'

WSGI_APPLICATION = 'voterreg.wsgi.application'

TEMPLATE_DIRS = (
    rel('templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "context_processors.add_settings",
    "context_processors.add_fbuid",
    "context_processors.add_source" )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'gunicorn',
    'kombu.transport.django',
    'djcelery',
    'south',
    'main',
    'voterapi',
    'staticpages',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class':'logging.StreamHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

BROKER_BACKEND = "django"

FACEBOOK_APP_ID = "258722907563918"
FACEBOOK_APP_SECRET = "0ebace487828ff1de2d68b1f7ff1a6f5"
FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/258722907563918/"

VOTIZEN_API_KEY = "" # secret
USE_FAKE_VOTIZEN_API = False

if environ.get("RACK_ENV", None) == "production":
    import dj_database_url

    DEBUG = False

    DATABASES = {
        'default': dj_database_url.config(default='postgres://localhost') 
        }

    INSTALLED_APPS += ("gunicorn", "storages",)

    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

    AWS_STORAGE_BUCKET_NAME = 'voterreg.fb'
    AWS_ACCESS_KEY_ID = 'AKIAIFSCVO2GAEACNIVA'
    AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_CUSTOM_DOMAIN = "s3.amazonaws.com/voterreg.fb"
    STATIC_URL= 'https://s3.amazonaws.com/voterreg.fb/'
    INSTALLATION = "production"

    VOTIZEN_API_KEY = environ.get("VOTIZEN_API_KEY", "")

    FACEBOOK_APP_ID = "220561354738022"
    FACEBOOK_APP_SECRET = environ.get("FACEBOOK_APP_SECRET", "")
    FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/votewithfriends/"

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https',)

    BASE_URL = "https://voterreg-facebook.herokuapp.com"

    KM_CODE = "8be66fb91e7ca782ba39688f6448862be1698c4e"

    EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME', "")
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD', "")
else:
    BASE_URL = "http://local.voterreg.org:8000"
    KM_CODE = "cccb2596f575fe692e22013c8329c5dbf98e4db7"
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from settings_local import *
except ImportError:
    pass
