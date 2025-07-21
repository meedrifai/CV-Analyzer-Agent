import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # OpenRouter
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
    
    # Email
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    email_user: str = os.getenv("EMAIL_USER", "")
    email_password: str = os.getenv("EMAIL_PASSWORD", "")
    email_from: str = os.getenv("EMAIL_FROM", "")
    
    # Recipients
    email_it: str = os.getenv("EMAIL_IT", "rifaii.mohameed@gmail.com")
    email_rh: str = os.getenv("EMAIL_RH", "meedschool@gmail.com")
    email_multimedia: str = os.getenv("EMAIL_MULTIMEDIA", "simorifai181@gmail.com")
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Upload
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))

settings = Settings()