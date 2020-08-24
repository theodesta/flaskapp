import os, json

class Config(object):
    DEBUG = False
    TESTING = False
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    APP_ENV = os.getenv('ENVIRONMENT')
    SEC_KEY = 'U2FsdGVkX1+d+5iG'

class ProductionConfig(Config):
    print("******" + str(os.getenv('ENVIRONMENT')))
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SEC_KEY = "thisisthedevseckey"
    APP_ENV = os.getenv('ENVIRONMENT')

    if APP_ENV == 'cloud' or APP_ENV == 'container':
        print("===========================")
        DB_CREDS = json.loads(os.getenv('VCAP_SERVICES'))['aws-rds'][0]['credentials']

    else:
        DB_CREDS={
            'host': 'localhost',
            'db_name': 'lookup_tables',
            'username': 'postgres',
            'password': 'postgrespasswordtdes',
            'port': '5432'
        }

class TestingConfig(Config):
    print("~~~~~~~~~~~~~~~~~~~~~~~~" + str(os.getenv('ENVIRONMENT')))
    TESTING = True