import os
import sys
from os import environ

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_APP_REQUESTS = False

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


# Localization and internationalization
TIME_ZONE = 'America/Chicago'
USE_TZ = False
USE_I18N = True
USE_L10N = False
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'English'),
)
LOCALE_PATHS = (
    rel('main', 'locale'),
)


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
    'rosetta',
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
FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/votewithfriends-dev/"
FACEBOOK_OG_PLEDGE_URL = 'https://graph.facebook.com/me/votewithfriends-dev:pledge'

VOTIZEN_API_KEY = "" # secret
USE_FAKE_VOTIZEN_API = False

SESSION_COOKIE_HTTPONLY = False

# change this whenever someone with sufficient permission
# changes it in heroku/sendgrid.
EMAIL_SENDER = "app7299205@heroku.com"

environment = environ.get("RACK_ENV", 'dev')

if environment in ["production", "staging"]:
    import dj_database_url

    DEBUG = False

    from sendgridify import sendgridify
    EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT, \
        EMAIL_USE_TLS = sendgridify()

    from memcacheify import memcacheify
    CACHES = memcacheify()

    DATABASES = {
        'default': dj_database_url.config(default='postgres://localhost')
        }

    INSTALLED_APPS += ("gunicorn", "storages",)

    STATIC_URL = 'https://s3.amazonaws.com/voterreg.fb/'
    INSTALLATION = "production"

    VOTIZEN_API_KEY = environ.get("VOTIZEN_API_KEY", "")

    FACEBOOK_APP_ID = "220561354738022"
    FACEBOOK_APP_SECRET = environ.get("FACEBOOK_APP_SECRET", "")
    FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/votewithfriends/"

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https',)

    BASE_URL = "https://voterreg-facebook.herokuapp.com"

    KM_CODE = "8be66fb91e7ca782ba39688f6448862be1698c4e"

    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    AWS_ACCESS_KEY_ID = 'AKIAIFSCVO2GAEACNIVA'
    AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY", "")

if environment == 'staging':
    DEBUG = True
    AWS_STORAGE_BUCKET_NAME = 'voterreg.fb.dev'
    AWS_S3_CUSTOM_DOMAIN = "s3.amazonaws.com/voterreg.fb.dev"
    FACEBOOK_APP_ID = "381227845280044"
    BASE_URL = "https://voterreg-facebook-staging.herokuapp.com"
    FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/votewithfriends-stag/"
    USE_FAKE_VOTIZEN_API = True
    FACEBOOK_OG_PLEDGE_URL = 'https://graph.facebook.com/me/votewithfriends-stag:pledge'

if environment == 'production':
    FACEBOOK_APP_ID = "220561354738022"
    BASE_URL = "https://voterreg-facebook.herokuapp.com"
    FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/votewithfriends/"
    AWS_STORAGE_BUCKET_NAME = 'voterreg.fb'
    AWS_S3_CUSTOM_DOMAIN = "s3.amazonaws.com/voterreg.fb"
    FACEBOOK_OG_PLEDGE_URL = 'https://graph.facebook.com/me/votewithfriends:pledge'


if environment == 'dev':
    BASE_URL = "http://local.voterreg.org:8000"
    KM_CODE = "cccb2596f575fe692e22013c8329c5dbf98e4db7"
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from settings_local import *
except ImportError:
    pass
