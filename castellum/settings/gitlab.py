from .default import *

SECRET_KEY = 'i#$kwk(s24ysn+l%+c!*z9u4+45)oex!-s#!bux#wf2pv2cc0d'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db_default',
    },
    'contacts': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db_contacts',
    }
}

DOMAINS = {
    'contact': '04d0e64e-a58a-41b3-bf6b-7a90dae84199',
}
