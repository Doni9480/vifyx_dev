"""
Django settings for blog project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path
from blog.utils import my_custom_upload_to_func
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-hqu-11onn^q7+kr(vgxm@)zo!5&*9+%p+lmx#c*t&shlfev07='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEV_DB = False
ALLOWED_HOSTS = ['*']
APPEND_SLASH = True

# Application definition

INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'mptt',
    'drf_yasg',
    'rest_framework',
    'django_summernote',
    'django_cleanup.apps.CleanupConfig',
    'django_apscheduler',
    'storages',
    # 'corsheaders',
    'guardian',

    'configs',
    'users',
    'surveys',
    'posts',
    'custom_tests',
    'quests',
    'comments',
    'blogs',
    'notifications',
    'campaign',
    'referrals',
    'periodic_bonuses',
    'albums',
    'contests',
    'transactions',
]

MPTT_ADMIN_LEVEL_INDENT = 20

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # custom authentication
    'users.api.middlewares.AuthTokenMiddleware',
    # check a admin
    'blog.middlewares.AdminCheckMiddleware',
    # local timezone
    'blog.middlewares.TimezoneMiddleware',
    # for no authentication users
    'blog.middlewares.LanguageMiddleware',
    # notifications
    'blog.middlewares.NotificationsMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'blog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'blog.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 5
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # this is default
    'guardian.backends.ObjectPermissionBackend',
)

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
if DEV_DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'blog',
            'USER': 'user_blog',
            'PASSWORD': 'jfjsdDJUIA',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_SIGNATURE_VERSION = os.getenv('AWS_S3_SIGNATURE_VERSION', default='s3v4')
AWS_S3_USE_SSL = int(os.getenv('AWS_S3_USE_SSL', default=1))
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
USE_S3 = int(os.getenv('USE_S3', default=0))

if USE_S3:
    MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    MEDIA_URL = 'media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

EMAIL_FROM = "support@blog.com"
EMAIL_HOST = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_PORT = "25"
EMAIL_USE_TLS = True

GOOGLE_RECAPTCHA_PRIVATE_KEY = '6LfF49kpAAAAAIoI3hjKBld9lTTx2Q-UoleOQmPG'
GOOGLE_RECAPTCHA_PUBLIC_KEY = '6LfF49kpAAAAAFiEh0fNdLdOJHvlIWa5_PyqbslK'

SUMMERNOTE_CONFIG = {
    'attachment_upload_to': my_custom_upload_to_func,

    'summernote': {
        'width': '100%',
    }
}

UNFOLD = {
    # "SITE_TITLE": None,
    # "SITE_HEADER": None,
    # "SITE_URL": "/",
    # # "SITE_ICON": lambda request: static("icon.svg"),  # both modes, optimise for 32px height
    # "SITE_ICON": {
    #     "light": lambda request: static("icon-light.svg"),  # light mode
    #     "dark": lambda request: static("icon-dark.svg"),  # dark mode
    # },
    # # "SITE_LOGO": lambda request: static("logo.svg"),  # both modes, optimise for 32px height
    # "SITE_LOGO": {
    #     "light": lambda request: static("logo-light.svg"),  # light mode
    #     "dark": lambda request: static("logo-dark.svg"),  # dark mode
    # },
    # "SITE_SYMBOL": "speed",  # symbol from icon set
    # "SITE_FAVICONS": [
    #     {
    #         "rel": "icon",
    #         "sizes": "32x32",
    #         "type": "image/svg+xml",
    #         "href": lambda request: static("favicon.svg"),
    #     },
    # ],
    "SHOW_HISTORY": True, # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True, # show/hide "View on site" button, default: True
    # "ENVIRONMENT": "sample_app.environment_callback",
    # "DASHBOARD_CALLBACK": "sample_app.dashboard_callback",
    # "THEME": "dark", # Force theme: "dark" or "light". Will disable theme switcher
    # "LOGIN": {
    #     "image": lambda request: static("sample/login-bg.jpg"),
    #     "redirect_after": lambda request: reverse_lazy("admin:APP_MODEL_changelist"),
    # },
    # "STYLES": [
    #     lambda request: static("css/style.css"),
    # ],
    # "SCRIPTS": [
    #     lambda request: static("js/script.js"),
    # ],
    # "COLORS": {
    #     "primary": {
    #         "50": "250 245 255",
    #         "100": "243 232 255",
    #         "200": "233 213 255",
    #         "300": "216 180 254",
    #         "400": "192 132 252",
    #         "500": "168 85 247",
    #         "600": "147 51 234",
    #         "700": "126 34 206",
    #         "800": "107 33 168",
    #         "900": "88 28 135",
    #         "950": "59 7 100",
    #     },
    # },
    # "EXTENSIONS": {
    #     "modeltranslation": {
    #         "flags": {
    #             "en": "🇬🇧",
    #             "fr": "🇫🇷",
    #             "nl": "🇧🇪",
    #         },
    #     },
    # },
    "SIDEBAR": {
        "show_search": False,  # Search in applications and models names
        "show_all_applications": True,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("Config"),
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Site Configuration"),
                        "icon": "tune",
                        "link": reverse_lazy("admin:configs_siteconfiguration_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    }
                ]
            },
            {
                "title": _("Transactions"),
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Transactions"),
                        "icon": "contract",
                        "link": reverse_lazy("admin:transactions_transactions_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    }
                ]
            },
            {
                "title": _("Campaign"),
                "icon": "campaign",
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Campaigns"),
                        "icon": "campaign",
                        "link": reverse_lazy("admin:campaign_campaign_changelist"),
                    },
                    {
                        "title": _("Tasks"),
                        "icon": "task",
                        "link": reverse_lazy("admin:campaign_task_changelist"),
                    },
                    {
                        "title": _("User task checkings"),
                        "icon": "check",
                        "link": reverse_lazy("admin:campaign_usertaskchecking_changelist"),
                    }
                ]
            },
            {
                "title": _("Blogs"),
                "icon": "rss_feed",
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Blogs"),
                        "icon": "rss_feed",
                        "link": reverse_lazy("admin:blogs_blog_changelist"),
                    },
                ],
            },
            {
                "title": _("Posts"),
                "icon": "post",
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Posts"),
                        "icon": "post",
                        "link": reverse_lazy("admin:posts_post_changelist"),
                    },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:posts_category_changelist"),
                    },
                    {
                        "title": _("Subcategories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:posts_subcategory_changelist"),
                    },
                    {
                        "title": _("Tags"),
                        "icon": "label",
                        "link": reverse_lazy("admin:posts_posttag_changelist"),
                    },
                ],
            },
            {
                "title": _("Quests"),
                "icon": "material-symbols-outlined",
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Quests"),
                        "icon": "post",
                        "link": reverse_lazy("admin:quests_quest_changelist"),
                    },
                    {
                        "title": _("Questions"),
                        "icon": "label",
                        "link": reverse_lazy("admin:quests_questionquest_changelist"),
                    },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:quests_category_changelist"),
                    },
                    {
                        "title": _("Subcategories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:quests_subcategory_changelist"),
                    },
                    {
                        "title": _("views"),
                        "icon": "visibility",
                        "link": reverse_lazy("admin:quests_questview_changelist"),
                    },
                ],
            },
            {
                "title": _("Tests"),
                "icon": "assessment",
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Tests"),
                        "icon": "assessment",
                        "link": reverse_lazy("admin:custom_tests_test_changelist"),
                    },
                    {
                        "title": _("Questions"),
                        "icon": "question_answer",
                        "link": reverse_lazy("admin:custom_tests_question_changelist"),
                    },
                    {
                        "title": _("Question answers"),
                        "icon": "chat",
                        "link": reverse_lazy("admin:custom_tests_questionanswer_changelist"),
                    },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:custom_tests_category_changelist"),
                    },
                    {
                        "title": _("Subcategories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:custom_tests_subcategory_changelist"),
                    },
                ]
            },
            {
                "title": _("Albums"),
                "icon": "assessment",
                "icon": "settings",
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Albums"),
                        "icon": "assessment",
                        "link": reverse_lazy("admin:albums_album_changelist"),
                    },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:albums_category_changelist"),
                    },
                    {
                        "title": _("Subcategories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:albums_subcategory_changelist"),
                    },
                ]
            },
            {
                "title": _("Comments"),
                "icon": "comment",
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Comments"),
                        "icon": "comment",
                        "link": reverse_lazy("admin:comments_comment_changelist"),
                    },
                    {
                        "title": _("Answers"),
                        "icon": "chat",
                        "link": reverse_lazy("admin:comments_answer_changelist"),
                    },
                ],
            },
            {
                "title": _("Authentication and Authorization"),
                "icon": "settings",
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Groups"),
                        "icon": "group",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Users"),
                        "icon": "account_circle",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                    {
                        "title": _("Percents"),
                        "icon": "percent",
                        "link": reverse_lazy("admin:users_percent_changelist"),
                    },
                    {
                        "title": _("Tokens"),
                        "icon": "lock",
                        "link": reverse_lazy("admin:users_token_changelist"),
                    },
                    {
                        "title": _("Total scores"),
                        "icon": "paid",
                        "link": reverse_lazy("admin:users_totalscore_changelist"),
                    },
                ],
            },
            {
                "title": _("Contests"),
                "icon": "assessment",
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Contests"),
                        "icon": "assessment",
                        "link": reverse_lazy("admin:contests_contest_changelist"),
                    },
                    {
                        "title": _("Album prize"),
                        "icon": "assessment",
                        "link": reverse_lazy("admin:contests_prizealbumelement_changelist"),
                    },
                    {
                        "title": _("Quest prize"),
                        "icon": "assessment",
                        "link": reverse_lazy("admin:contests_prizequestelement_changelist"),
                    },
                    {
                        "title": _("Post prize"),
                        "icon": "assessment",
                        "link": reverse_lazy("admin:contests_prizepostelement_changelist"),
                    },
                ]
            },
            {
                "title": _("Notifications"),
                "icon": "assessment",
                "separator": True,
                "collapsible": True,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Notifications"),
                        "icon": "assessment",
                        "link": reverse_lazy("admin:notifications_notification_changelist"),
                    },
                    {
                        "title": _("System texts"),
                        "icon": "assessment",
                        "link": reverse_lazy("admin:notifications_systemtext_changelist"),
                    },
                ]
            }
        ],
    },
    # "TABS": [
    #     {
    #         "models": [
    #             "app_label.model_name_in_lowercase",
    #         ],
    #         "items": [
    #             {
    #                 "title": _("Your custom title"),
    #                 "link": reverse_lazy("admin:app_label_model_name_changelist"),
    #                 "permission": "sample_app.permission_callback",
    #             },
    #         ],
    #     },
    # ],
}
ADMIN_MENU = [
    # {
    #     "label": "Главная",
    #     "icon": "home",  # Вы можете указать иконку для раздела
    #     "models": [
    #         "app_name.ModelName1",
    #         "app_name.ModelName2",
    #     ]
    # },
    {
        "label": "Пользователи",
        "icon": "users",
        "models": [
            "auth.User",
            "auth.Group",
            "app_name.ModelName3",
        ]
    },
    # {
    #     "label": "Настройки",
    #     "icon": "settings",
    #     "models": [
    #         "app_name.ModelName4",
    #         "app_name.ModelName5",
    #     ]
    # },
]

# CORS_ALLOWED_ORIGINS = ["http://localhost:8080", "http://127.0.0.1:8080", "https://d991-185-138-186-34.ngrok-free.app"]

# CORS_ORIGIN_WHITELIST = (
#     'https://d991-185-138-186-34.ngrok-free.app',
#     # 'localhost:8080',
#     # 'localhost:8081',
#     # 'localhost',
#     # 'localhost:8888',
# )

# CSRF_TRUSTED_ORIGINS = ['http://localhost:8080', 'https://d991-185-138-186-34.ngrok-free.app']

# CORS_ALLOW_ALL_ORIGINS = True

# SECURE_SSL_REDIRECT = True  # Перенаправление всех HTTP-запросов на HTTPS
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Убедитесь, что Django знает, что находится за прокси, который использует HTTPS
# CSRF_COOKIE_SECURE = True  # Убедитесь, что CSRF куки используются только по HTTPS
# SESSION_COOKIE_SECURE = True  # Убедитесь, что сессионные куки используются только по HTTPS
