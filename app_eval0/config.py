import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'Team_Paiya'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # OpenAI API KEY
    MAIL_SERVER = 'smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') # MAIL_USERNAME
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') #MAIL_PASSWORD
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
