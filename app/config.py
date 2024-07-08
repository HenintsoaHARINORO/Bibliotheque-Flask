# config.py

import os

UPLOAD_FOLDER = '/Users/henintsoa/PycharmProjects/BibliothèqueFlask/uploads'
MAX_CONTENT_LENGTH = 30 * 1024 * 1024  # 30MB
SECRET_KEY = 'your_secret_key_here'
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:ADMIN123@localhost/postgres'

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = 'haikaroka4@gmail.com'
MAIL_PASSWORD = 'egzu rtef ncti stxl'
MAIL_USE_TLS = True
MAIL_USE_SSL = False
# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
