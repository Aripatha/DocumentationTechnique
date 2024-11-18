import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    MAIL_DEFAULT_SENDER='JospinBomo@teccart.com'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # OpenAI API KEY
    MAIL_SERVER = 'smtp.mailtrap.io'
    MAIL_PORT = 587
    MAIL_USERNAME = '00e6a449eebca0' # MAIL_USERNAME
    MAIL_PASSWORD = '17ba0cc043289c' #MAIL_PASSWORD
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
