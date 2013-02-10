import django.conf.global_settings as global_settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (('Elliot Marsden', 'elliot.marsden@gmail.com'),)
MANAGERS = ADMINS
AUTH_PROFILE_MODULE = 'accounts.UserProfile'
LOGIN_URL = '/accounts/login/'

TIME_ZONE = 'GB'
LANGUAGE_CODE = 'en-gb'
USE_I18N = True
USE_L10N = True
USE_TZ = True
SITE_ID = 1
SECRET_KEY = 'm+zq&*bxrmw-&ppq3_2jfjil!af4%840-(r-%%p^z_*vk(9#!*'

PROJECT_DIR = '/home/ejm/Pantry/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_DIR + 'pantry.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'store',
    'tesco',
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

ROOT_URLCONF = 'pantry.urls'

STATIC_ROOT = '/static'
STATICFILES_DIRS = (PROJECT_DIR + 'css',)
STATIC_URL = '/static/'

MEDIA_ROOT = PROJECT_DIR + 'media/'
MEDIA_URL = '/media/'

TEMPLATE_DIRS = (PROJECT_DIR + 'templates',)
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + ('template_context_processors.current_path',)
