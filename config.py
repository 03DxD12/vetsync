import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'vetsync-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///vetsync.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-jwt-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    VAPID_PUBLIC_KEY = os.getenv(
        'VAPID_PUBLIC_KEY',
        'BD9p1qDG9s8ff3E9K8QSjd1KCtzNf1wOj3mFJC60VwhTgQ0WmBoKI9BrLCMpQgo_fyFBVVWrJu6FVgqx4JbhtjA'
    )
    VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY', (
        '-----BEGIN PRIVATE KEY-----\n'
        'MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgtlD6aKe4UjqV0pRZ\n'
        'G/e0jvc0nrodnWeNoZcVAsjEb0mhRANCAAQ/adagxvbPH39xPSvEEo3dSgrczX9c\n'
        'Do95hSQutFcIU4ENFpgaCiPQaywjKUIKP38hQVVVqybuhVYKseCW4bYw\n'
        '-----END PRIVATE KEY-----'
    ))
    VAPID_CLAIMS = {'sub': 'mailto:admin@vetsync.com'}


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
