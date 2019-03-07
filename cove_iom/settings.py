import sys
if "pytest" not in sys.modules:
    # Check that we can import defusedexpat, as this will protect us against
    # some XML attacks in xmltodict
    # Needs a noqa comment as we don't actually use it here
    import defusedexpat  # noqa: F401

# Needs a noqa comment to come after the above import
from cove import settings  # noqa: E408

PIWIK = settings.PIWIK
GOOGLE_ANALYTICS_ID = settings.GOOGLE_ANALYTICS_ID
MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL
DEALER_TYPE = settings.DEALER_TYPE
SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG
ALLOWED_HOSTS = settings.ALLOWED_HOSTS
MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES
ROOT_URLCONF = settings.ROOT_URLCONF
TEMPLATES = settings.TEMPLATES
WSGI_APPLICATION = settings.WSGI_APPLICATION
DATABASES = settings.DATABASES
LANGUAGE_CODE = settings.LANGUAGE_CODE
TIME_ZONE = settings.TIME_ZONE
USE_I18N = settings.USE_I18N
USE_L10N = settings.USE_L10N
USE_TZ = settings.USE_TZ
STATIC_URL = settings.STATIC_URL
STATIC_ROOT = settings.STATIC_ROOT
LANGUAGES = settings.LANGUAGES
LOCALE_PATHS = settings.LOCALE_PATHS
LOGGING = settings.LOGGING

if getattr(settings, 'RAVEN_CONFIG', None):
    RAVEN_CONFIG = settings.RAVEN_CONFIG

INSTALLED_APPS = settings.INSTALLED_APPS + ('cove_iom', )
WSGI_APPLICATION = 'cove_iom.wsgi.application'
ROOT_URLCONF = 'cove_iom.urls'
COVE_CONFIG = {
    'app_name': 'cove_iom',
    'app_base_template': 'cove_iom/base.html',
    'app_verbose_name': 'IATI CoVE IOM',
    'app_strapline': 'Convert, Validate, Explore IATI Data',
    'core_schema': {'activity': 'iati-activities-schema.xsd', 'organisation': 'iati-organisations-schema.xsd'},
    'supplementary_schema': {'common': 'iati-common.xsd', 'xml': 'xml.xsd'},
    'schema_host': 'https://raw.githubusercontent.com/IATI/IATI-Schemas/',
    'schema_version': '2.03',
    'schema_directory': 'iati_schemas',
    'root_list_path': 'iati-activity',
    'root_id': None,
    'id_name': 'iati-identifier',
    'convert_titles': False,
    'input_methods': ['upload', 'url', 'text'],
    'support_email': None,
    'xml_comment': 'Data generated by IATI CoVE. Built by Open Data Services Co-operative: http://iati.cove.opendataservices.coop/',
    'hashcomments': True
}

PROJECT_TYPE_MAPPING = {
    'RE': 72010, 'OP': 72010, 'RX': 72010, 'RA': 93010, 'DP': 72010,
    'EP': 74020, 'CC': 72050, 'DX': 72050, 'SN': 72010, 'CS': 16050,
    'FC': 15240, 'DS': 73010, 'DR': 74020, 'PB': 15220, 'PE': 15220,
    'OC': 15151, 'EM': 15151, 'EA': 15151, 'MH': 12220, 'MA': 12220,
    'MP': 72010, 'CE': 16020, 'RQ': 16020, 'RM': 24010, 'NC': '',
    'RT': 99810, 'CT': 15160, 'TC': 15136, 'IB': 15136, 'LM': 16020,
    'FM': 11230, 'IV': 15136, 'PO': 15190, 'PR': 15190, 'PM': 15190,
    'RP': 15160, 'HA': 15160, 'LP': 15130, 'SS': 91010, 'SM': 72010,
    'IM': 15190, 'MI': 91010, 'MJ': 91010, 'MK': 91010, 'ML': 91010,
    'OS': 91010, 'DM': 91010, 'AD': 91010
}

# Multi line support for budget line & expense line
MULTI_LINE_SUPPORT = True

try:
    from .local_settings import *
except ImportError:
    pass
