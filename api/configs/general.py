class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'F\x03Dk\x1f@\xaa_5{\xf5m\xf2\x99\x9e\x1c\n\xe7{\xfb\x8aQ\xdae'
    CACHE_TYPE = 'filesystem'
    CACHE_DIR = '/tmp/api'
    CACHE_DEFAULT_TIMEOUT = 50
    CACHE_THRESHOLD = 2048


class ProductionConfig(Config):
    SQLALCHEMY_BINDS = {
        'term': 'mysql://username:password@localhost/term',
        'payment': 'mysql://username:password@localhost/payment',
        'mobispot': 'mysql://username:password@localhost/mobispot'
    }
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_BINDS = {
        'term': 'mysql://root:gjevebwtyf@localhost/term',
        'payment': 'mysql://root:gjevebwtyf@localhost/payment',
        'mobispot': 'mysql://root:gjevebwtyf@localhost/mobispot'
    }
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
