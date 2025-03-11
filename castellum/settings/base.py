from pathlib import Path

from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent


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
    'bootstrap_colors',
    'phonenumber_field',
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
    'castellum.audit',
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

    'django.contrib.auth.middleware.LoginRequiredMiddleware',

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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
    'django.contrib.auth.backends.ModelBackend',
    'castellum.studies.backends.StudyPermissionBackend',
]

AUTH_USER_MODEL = 'castellum_auth.User'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

DEFAULT_EXCEPTION_REPORTER = 'castellum.utils.debug.ExceptionReporter'

# Internationalization

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale'
]

LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
]


# Static files (CSS, JavaScript, Images)

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'castellum.utils.finders.NpmFinder',
]

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    },
}

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR.parent / 'static'

MEDIA_URL = 'media/'

NPM_PATH = BASE_DIR.parent / 'node_modules'

NPM_FILES = [
    Path('bootstrap', 'dist', 'css', 'bootstrap.min.css'),
    Path('bootstrap', 'dist', 'css', 'bootstrap.min.css.map'),
    Path('bootstrap', 'dist', 'js', 'bootstrap.min.js'),
    Path('bootstrap', 'dist', 'js', 'bootstrap.min.js.map'),
    Path('jdenticon', 'dist', 'jdenticon.min.js'),
    Path('jdenticon', 'dist', 'jdenticon.min.js.map'),
    Path('jquery', 'dist', 'jquery.min.js'),
    Path('qr', 'index.js'),
    Path('qr', 'index.js.map'),
    Path('@popperjs', 'core', 'dist', 'umd', 'popper-lite.min.js'),
    Path('@popperjs', 'core', 'dist', 'umd', 'popper-lite.min.js.map'),
    Path('@fortawesome', 'fontawesome-free', 'css', 'fontawesome.min.css'),
    Path('@fortawesome', 'fontawesome-free', 'css', 'solid.min.css'),
    Path('@fortawesome', 'fontawesome-free', 'webfonts', 'fa-solid-900.woff2'),
    Path('select2', 'dist', 'css', 'select2.min.css'),
    Path('select2', 'dist', 'js', 'select2.min.js'),
    Path('select2', 'dist', 'js', 'i18n', 'de.js'),
    Path('@ttskch', 'select2-bootstrap4-theme', 'dist', 'select2-bootstrap4.min.css'),
    Path('fullcalendar', 'all', 'global.js'),
    Path('fullcalendar', 'locales', 'de/global.js'),
    Path('fullcalendar', 'skeleton.css'),
    Path('fullcalendar-scheduler', 'all', 'global.js'),
    Path('@fullcalendar', 'bootstrap5', 'global.js'),
    Path('@fullcalendar', 'bootstrap5', 'theme.css'),
]

BOOTSTRAP5 = {
    'set_placeholder': False,
}

AXES_LOCKOUT_TEMPLATE = 'axes-lockout.html'
