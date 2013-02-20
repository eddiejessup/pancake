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
SITE_ID = 1
SECRET_KEY = 'm+zq&*bxrmw-&ppq3_2jfjil!af4%840-(r-%%p^z_*vk(9#!*'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/ejm/Pantry/pantry/pantry.db',
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
    'pantry.accounts',
    'pantry.stocks',
    'pantry.health',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
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
STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    '/home/ejm/Pantry/pantry/static/',
)
ADMIN_MEDIA_PREFIX = '/static/admin/'
MEDIA_ROOT = '/home/ejm/Pantry/pantry/media/'
MEDIA_URL = '/media/'

TEMPLATE_DIRS = (
     '/home/ejm/Pantry/pantry/templates',
)
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'pantry.template_context_processors.get_current_path',
)