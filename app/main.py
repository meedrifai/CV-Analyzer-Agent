from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from app.services.pdf_extractor import PDFExtractor
from app.services.email_service import EmailService
from app.services.webhook_handler import WebhookHandler
from app.models.cv_classifier import CVClassifier
from app.utils.logger import setup_logging

# Configuration des logs
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="CV Classifier API", version="1.0.0")

# Initialisation des services
pdf_extractor = PDFExtractor()
email_service = EmailService()
webhook_handler = WebhookHandler()
cv_classifier = CVClassifier()

@app.post("/webhook/cv")
async def process_cv_webhook(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Point d'entrée pour le webhook de traitement des CV
    """
    try:
        # Vérifier que c'est un PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")
        
        # Sauvegarder le fichier
        file_path = await webhook_handler.save_uploaded_file(file)
        if not file_path:
            raise HTTPException(status_code=400, detail="Erreur lors de la sauvegarde du fichier")
        
        # Traiter en arrière-plan
        background_tasks.add_task(process_cv_pipeline, file_path)
        
        return JSONResponse(
            status_code=200,
            content={"message": "CV reçu avec succès, traitement en cours"}
        )
        
    except Exception as e:
        logger.error(f"Erreur dans le webhook : {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.post("/test/classify")
async def test_classify_cv(file: UploadFile = File(...)):
    """
    Endpoint de test pour classifier un CV sans envoi d'email
    """
    try:
        # Sauvegarder temporairement
        file_path = await webhook_handler.save_uploaded_file(file)
        if not file_path:
            raise HTTPException(status_code=400, detail="Erreur lors de la sauvegarde")
        
        # Extraire le texte
        cv_text = pdf_extractor.extract_text_from_pdf(file_path)
        if not cv_text:
            webhook_handler.cleanup_file(file_path)
            raise HTTPException(status_code=400, detail="Impossible d'extraire le texte du PDF")
        
        # Classifier
        domain = cv_classifier.classify_cv(cv_text)
        
        # Nettoyer
        webhook_handler.cleanup_file(file_path)
        
        return JSONResponse(content={
            "domain": domain,
            "text_length": len(cv_text),
            "preview": cv_text[:200] + "..." if len(cv_text) > 200 else cv_text
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du test : {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_cv_pipeline(file_path: str):
    """
    Pipeline complet de traitement du CV
    """
    try:
        logger.info(f"Début du traitement du CV : {file_path}")
        
        # 1. Vérifier que le PDF est valide
        if not pdf_extractor.is_valid_pdf(file_path):
            print("1 === PDF VALID ===")
            logger.error("PDF invalide")
            return
        
        # 2. Extraire le texte
        cv_text = pdf_extractor.extract_text_from_pdf(file_path)
        if not cv_text:
            logger.error("Impossible d'extraire le texte")
            return
        print("2 === PDF EXTRACTED ===")
        
        # 3. Classifier le CV
        domain = cv_classifier.classify_cv(cv_text)
        if not domain:
            logger.error("Impossible de classifier le CV")
            return
        print("3 === PDF CLASSIFIED ===")
        
        # 4. Envoyer l'email
        success = email_service.send_cv_notification(domain, file_path)
        
        if success:
            logger.info(f"Pipeline terminé avec succès - Domaine : {domain}")
            print("4 === EMAIL SENT ===")
        else:
            logger.error("Échec de l'envoi de l'email")
    
    except Exception as e:
        logger.error(f"Erreur dans le pipeline : {e}")
    
    finally:
        # Nettoyer le fichier temporaire
        webhook_handler.cleanup_file(file_path)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "CV Classifier API is running"}

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )