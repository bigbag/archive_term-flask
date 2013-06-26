class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'F\x03Dk\x1f@\xaa_5{\xf5m\xf2\x99\x9e\x1c\n\xe7{\xfb\x8aQ\xdae'
    CACHE_TYPE = 'simple'
    # CACHE_DIR = '/tmp/api'
    CACHE_DEFAULT_TIMEOUT = 50
    CACHE_THRESHOLD = 2048
    TZ = 'Europe/Moscow'
    UPLOAD_FOLDER = './arch'
    ALLOWED_EXTENSIONS = set(['xml'])
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class TermConfig(object):
    NTP_SERVER = 'pool.ntp.org'

    DOWNLOAD = True
    DOWNLOAD_IP = '5.9.50.180'
    DOWNLOAD_PORT = 4000
    DOWNLOAD_PROTO = 'https'
    DOWNLOAD_LINK_TYPE = 2

    UPLOAD = True
    UPLOAD_IP = '5.9.50.180'
    UPLOAD_PORT = 4000
    UPLOAD_PROTO = 'https'
    UPLOAD_LINK_TYPE = 2

    LOGGER = True
    LOGGER_IP = '80.90.125.219'
    LOGGER_PORT = 64141
    LOGGER_PROTO = 'https'
    LOGGER_LINK_TYPE = 2

    UPDATE = True
    UPDATE_IP = '80.90.125.219'
    UPDATE_PORT = 64141
    UPDATE_PROTO = 'https'
    UPDATE_LINK_TYPE = 2
    UPDATE_PERIOD = 1440


class ProductionConfig(Config):
    SQLALCHEMY_BINDS = {
        'term': 'mysql://username:password@localhost/term?charset=utf8',
        'payment': 'mysql://username:password@localhost/payment?charset=utf8',
        'mobispot': 'mysql://username:password@localhost/mobispot?charset=utf8'
    }
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = True


class DevelopmentConfig(Config):
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_BINDS = {
        'term': 'mysql://root:gjevebwtyf@localhost/term?charset=utf8',
        'payment': 'mysql://root:gjevebwtyf@localhost/payment?charset=utf8',
        'mobispot': 'mysql://root:gjevebwtyf@localhost/mobispot?charset=utf8'
    }
    DEBUG = True
    SQLALCHEMY_RECORD_QUERIES = True


class TestingConfig(Config):
    TESTING = True
