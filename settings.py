import os.path
import sys

# Paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
APPS_PATH = os.path.join(PROJECT_ROOT, 'apps')
LIBS_PATH = os.path.join(PROJECT_ROOT, 'libs')
sys.path.insert(0, APPS_PATH)
sys.path.insert(0, LIBS_PATH)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SITE_THEME = "default"

ADMINS = (
    ('Glen Zangirolami', 'gzangirolami@schipul.com'),
	('Eloy Zuniga Jr.', 'ezuniga@schipul.com'),
    ('Jennifer Ulmer', 'julmer@schipul.com'),
    ('Jenny Qian', 'jqian@schipul.com'),
    ('JMO', 'jmowswalt@schipul.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tendenci50.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# email
EMAIL_HOST = '4.78.3.131'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'DO-NOT-REPLY@tendenci.com'

# user agent for external retrieval of files/images
TENDENCI_USER_AGENT = 'Tendenci/5.0 +http://www.tendenci.com'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Central'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en-us', u'English'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

THEME_ROOT = os.path.join(PROJECT_ROOT, 'themes', SITE_THEME)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/media/'

# Absolute path to the directory that holds static media.
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static')

# URL that handles the media served from STATIC_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
STATIC_URL = '/site_media/static/'

# Avatar default URL, no Gravatars
AVATAR_GRAVATAR_BACKUP = False
AVATAR_DEFAULT_URL = STATIC_URL + '/images/icons/default-user-80.jpg'
AUTO_GENERATE_AVATAR_SIZES = (128, 80, 48,)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/site_media/static/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 's$6*!=m$t0__=51^w@_tbazonjm4+fg@0+ic#bx^3rj)zc$a6i'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'swfupload.middleware.SWFUploadMiddleware',
    'swfupload.middleware.MediaUploadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'perms.middleware.ImpersonationMiddleware',
    'base.middleware.Http403Middleware',
    'redirects.middleware.RedirectMiddleware',
)

ROOT_URLCONF = 'Tendenci50.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "themes", SITE_THEME, "templates"),
    os.path.join(PROJECT_ROOT, "templates"),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    
    # tendenci context processors
    'theme.context_processors.theme',
    'site_settings.context_processors.settings',
    'base.context_processors.static_url'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.messages',

    # third party applications
    'notification',
    'pagination',
    'photologue',
    'tagging',
    'registration',
    'avatar',
    'tinymce',
    'haystack',
    'captcha',
    'south',
    'forms_builder.forms',
    
    'pluginmanager',
    
    # tendenci applications
    'base',
    'accounts',
    'perms',
    'dashboard',
    'profiles',
    'articles',
    'news',
    'stories',
    'pages',
    'events',
    'photos',
    'entities',
    'locations',
    'site_settings',
    'user_groups',
    'make_payments',
    'invoices',
    'payments',
    'accountings',
    'emails',
    'email_blocks',
    'actions',
    #'donations',
    'files',
    'contacts',
    'event_logs',
    'robots',
    'categories',
    'contributions',
    'theme_editor',
    'jobs',
    'styled_forms',
    'form_builder',
    'newsletters',
    'meta',
    'redirects',
    'directories',
    'help_files',
    'resumes',

    # celery task system, must stay at the bottom
    # of installed apps
    #'djcelery',
)

# This is the number of days users will have to activate their
# accounts after registering. If a user does not activate within
# that period, the account will remain permanently inactive and may
#be deleted by maintenance scripts provided in django-registration.
ACCOUNT_ACTIVATION_DAYS = 7 

LOGIN_REDIRECT_URL = '/dashboard'

AUTH_PROFILE_MODULE = 'profiles.Profile'
AUTHENTICATION_BACKENDS = (
    'perms.backend.ObjectPermBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# -------------------------------------- #
#    TINYMCE
# -------------------------------------- #
TINYMCE_JS_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static', 'tinymce')
TINYMCE_JS_URL = STATIC_URL + 'tinymce/tiny_mce.js'
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = False

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "stormeimage,table,paste,searchreplace,inlinepopups,tabfocus,fullscreen,media,spellchecker",
    'gecko_spellcheck': False,
    'theme': "advanced",

    # theme options
    'theme_advanced_buttons1': "bold,italic,underline,strikethrough,|,bullist,numlist,table, |,justifyleft,justifycenter,justifyright,|,link,unlink,|,image,|,pagebreak,fullscreen,code",
    'theme_advanced_buttons2': "formatselect,underline,justifyfull,forecolor,|,pastetext,pasteword,removeformat,media,charmap,|,outdent,indent,|,undo,redo",
    'theme_advanced_buttons3': "",
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_toolbar_align': "left",
    'theme_advanced_statusbar_location': "bottom",
    'theme_advanced_resizing' : True,

    'theme_advanced_resize_horizontal': True,
    'dialog_type': "modal",
    'tab_focus': ":prev, :next",
    'apply_source_formatting' : True,
    'convert_urls' : False,
    'apply_source_formatting' : False,
    'handle_event_callback' : "event_handler",
}

# -------------------------------------- #
# CACHING
# -------------------------------------- #
CACHE_DIR = PROJECT_ROOT + "/cache"
CACHE_BACKEND = "file://" + CACHE_DIR + "?timeout=604800" # 7 days

# --------------------------------------#
# Celery
# --------------------------------------#
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

# --------------------------------------#
# Hackstack Search
# --------------------------------------#
HAYSTACK_SITECONF = 'search'
HAYSTACK_SEARCH_ENGINE = 'xapian'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
HAYSTACK_XAPIAN_PATH = os.path.join(PROJECT_ROOT,'index')
HAYSTACK_INCLUDED_APPS = ('article','directory','event','photoset','job','page','news','resume','story')

#---------------------------------------------------------------
# payment gateway settings - LOGIN and KEY need to be moved to local_urls.py later
#---------------------------------------------------------------
#AUTHNET_POST_URL = "https://secure.authorize.net/gateway/transact.dll"
AUTHNET_POST_URL = "https://test.authorize.net/gateway/transact.dll"
# the AUTHNET_LOGIN and AUTHNET_KEY are specified in local_settings
AUTHNET_LOGIN = ""
AUTHNET_KEY = ""
MERCHANT_LOGIN = ""
MERCHANT_TXN_KEY = ""

#-------------------------------------------------------------------#
# Maximum number of rss items to display on the main rss
#-------------------------------------------------------------------#
MAX_RSS_ITEMS = 100

# --------------------------------------#
# CAPTCHA SETTINGS
# --------------------------------------#
CAPTCHA_FONT_SIZE = 50
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'

# Django Messaging system
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Fomrs upload path
FORMS_BUILDER_UPLOAD_ROOT = MEDIA_ROOT

# local settings for development
try:
    from local_settings import *
except ImportError:
    pass


#THIS MUST BE AT THE END!
#Plugin configuration
DEFAULT_INSTALLED_APPS = INSTALLED_APPS
import pluginmanager
INSTALLED_APPS = pluginmanager.plugin_apps(INSTALLED_APPS)
# add the plugins to the sys path - GJQ 10/12/2010
PLUGINS_PATH = os.path.join(PROJECT_ROOT, 'plugins')
sys.path.insert(0, PLUGINS_PATH)