from environs import Env

env = Env()
env.read_env(".env")


class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{env.str('DB_USERNAME')}:{env.str('DB_PASSWORD')}"
        f"@{env.str('DB_HOST')}:{env.int('DB_PORT')}/{env.str('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = env.str("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_REFRESH_TOKEN_EXPIRES = 86400

    TWILLIO_ACCOUNT_SID = env.str("TWILLIO_ACCOUNT_SID")
    TWILLIO_AUTH_TOKEN = env.str("TWILLIO_AUTH_TOKEN")
    TWILLIO_PHONE_NUMBER = env.str("TWILLIO_PHONE_NUMBER")

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = env.str("MAIL_USERNAME")
    MAIL_DEFAULT_SENDER = env.str("MAIL_USERNAME")
    MAIL_PASSWORD = env.str("MAIL_PASSWORD")

    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    CELERY_TIMEZONE = "UTC"
