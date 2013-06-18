class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'F\x03Dk\x1f@\xaa_5{\xf5m\xf2\x99\x9e\x1c\n\xe7{\xfb\x8aQ\xdae'


class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
