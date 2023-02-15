from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_bootstrap5',
    'phonenumber_field',
    'parler',
    'stronghold',
    'mfa',

    'castellum.utils',
    'castellum.castellum_auth',
    'castellum.studies',
    'castellum.subjects',
    'castellum.pseudonyms',
    'castellum.contacts',
    'castellum.recruitment',
    'castellum.execution',
    'castellum.data_protection',
    'castellum.appointments',
    'castellum.broadcast_messages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'stronghold.middleware.LoginRequiredMiddleware',

    'castellum.castellum_auth.middlewares.UserExpirationMiddleware',
    'castellum.castellum_auth.middlewares.AutoLogoutMiddleware',
    'castellum.castellum_auth.middlewares.UserLanguageMiddleware',
]

ROOT_URLCONF = 'castellum.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'castellum.utils.context_processors.get_settings',
                'castellum.broadcast_messages.context_processors.get_broadcast_messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'castellum.wsgi.application'


DATABASE_ROUTERS = [
    'castellum.utils.routers.Router',
]

APP_DB_ROUTER = {
    'contacts': 'contacts',
    'geofilters': 'contacts',
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation

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

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "castellum.studies.backends.StudyPermissionBackend",
]

AUTH_USER_MODEL = 'castellum_auth.User'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

DEFAULT_EXCEPTION_REPORTER = 'castellum.utils.debug.ExceptionReporter'

# Internationalization
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / 'locale']


# Static files (CSS, JavaScript, Images)

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'npm.finders.NpmFinder',
]

# enable cache busting
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

NPM_ROOT_PATH = BASE_DIR.parent

NPM_FILE_PATTERNS = {
    'bootstrap': [
        'dist/css/bootstrap.min.css',
        'dist/js/bootstrap.min.js',
    ],
    'jdenticon': ['dist/jdenticon.min.js'],
    'jquery': ['dist/jquery.min.js'],
    '@popperjs': ['core/dist/umd/popper-lite.min.js'],
    '@fortawesome/fontawesome-free': [
        'css/all.min.css',
        'webfonts/fa-regular-400.woff2',
        'webfonts/fa-regular-400.ttf',
        'webfonts/fa-brands-400.woff2',
        'webfonts/fa-brands-400.ttf',
        'webfonts/fa-solid-900.woff2',
        'webfonts/fa-solid-900.ttf',
        'webfonts/fa-v4compatibility.woff2',
        'webfonts/fa-v4compatibility.ttf',
    ],
    'select2': [
        'dist/css/select2.min.css',
        'dist/js/select2.min.js',
        'dist/js/i18n/de.js',
    ],
    '@ttskch/select2-bootstrap4-theme': [
        'dist/select2-bootstrap4.min.css',
    ],
    'fullcalendar-scheduler': [
        'index.global.min.js',
    ],
    '@fullcalendar': [
        'core/locales/de.global.min.js',
        'bootstrap/index.global.min.js',
    ],
    'cbor-js': [
        'cbor.js',
    ],
}

BOOTSTRAP5 = {
    'set_placeholder': False,
}

AXES_LOCKOUT_TEMPLATE = 'axes-lockout.html'
