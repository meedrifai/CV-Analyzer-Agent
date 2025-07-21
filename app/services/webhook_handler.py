from fastapi import UploadFile
import aiofiles
import os
import uuid
from typing import Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class WebhookHandler:
    def __init__(self):
        self.upload_dir = settings.upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_uploaded_file(self, file: UploadFile) -> Optional[str]:
        """
        Sauvegarde le fichier uploadé et retourne le chemin
        """
        try:
            # Vérifier la taille du fichier
            if file.size > settings.max_file_size:
                logger.error(f"Fichier trop volumineux : {file.size} bytes")
                return None
            
            # Générer un nom unique
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Sauvegarder le fichier
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            logger.info(f"Fichier sauvegardé : {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier : {e}")
            return None
    
    def cleanup_file(self, file_path: str):
        """
        Supprime le fichier temporaire
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Fichier temporaire supprimé : {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier : {e}")