import PyPDF2
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PDFExtractor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Optional[str]:
        """
        Extrait le texte d'un fichier PDF
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                if not text.strip():
                    logger.warning(f"Aucun texte extrait du fichier {file_path}")
                    return None
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du PDF {file_path}: {e}")
            return None
    
    @staticmethod
    def is_valid_pdf(file_path: str) -> bool:
        """
        Vérifie si le fichier est un PDF valide
        """
        try:
            with open(file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
            return True
        except Exception:
            return False    