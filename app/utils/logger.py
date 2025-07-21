import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """
    Configure le système de logging
    """
    # Créer le dossier de logs
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler pour fichier avec rotation
    log_filename = os.path.join(log_dir, f"cv_classifier_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configuration du logger principal
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
    
    # Réduire le niveau de log pour certaines librairies
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)