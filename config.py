class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'F\x03Dk\x1f@\xaa_5{\xf5m\xf2\x99\x9e\x1c\n\xe7{\xfb\x8aQ\xdae'


class ProductionConfig(Config):
    SQLALCHEMY_BINDS = {
        'term':        'mysqldb://username:password@localhost/term',
        'payment':     'mysqldb://username:password@localhost/payment',
        'mobispot':    'mysqldb://username:password@localhost/mobispot'
    }
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_BINDS = {
        'term':        'mysqldb://root:gjevebwtyf@localhost/term',
        'payment':     'mysqldb://root:gjevebwtyf@localhost/payment',
        'mobispot':    'mysqldb://root:gjevebwtyf@localhost/mobispot'
    }
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
