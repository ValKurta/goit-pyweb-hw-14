import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    CLOUDINARY_CLOUD_NAME = cloud_name
    CLOUDINARY_API_KEY = 12345678
    CLOUDINARY_API_SECRET = api_secret

settings = Settings()
