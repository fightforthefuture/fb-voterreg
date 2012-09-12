import os
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
USE_TZ = True
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

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'kombu.transport.django',
    'djcelery',
    'south',
    'main',
    'voterapi',
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
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

BROKER_BACKEND = "django"

FACEBOOK_APP_ID = "258722907563918"
FACEBOOK_APP_SECRET = "0ebace487828ff1de2d68b1f7ff1a6f5"
FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/258722907563918/"

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
    STATIC_URL= 'http://s3.amazonaws.com/voterreg.fb/'
    INSTALLATION = "production"

    FACEBOOK_APP_ID = "220561354738022"
    FACEBOOK_APP_SECRET = environ.get("FACEBOOK_APP_SECRET", "")
    FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/220561354738022/"
else:
    INSTALLED_APPS += ("staticpages",)

try:
    from settings_local import *
except ImportError:
    pass
