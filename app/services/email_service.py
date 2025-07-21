import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.email_user = settings.email_user
        self.email_password = settings.email_password
        self.email_from = settings.email_from
        
        # Mapping domaine -> email
        self.domain_emails = {
            "IT": settings.email_it,
            "RH": settings.email_rh,
            "Multimédia": settings.email_multimedia
        }
    
    def send_cv_notification(self, domain: str, cv_file_path: str, candidate_info: dict = None) -> bool:
        """
        Envoie un email de notification avec le CV en pièce jointe
        """
        try:
            recipient = self.domain_emails.get(domain)
            if not recipient:
                logger.error(f"Aucun destinataire trouvé pour le domaine : {domain}")
                return False
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = recipient
            msg['Subject'] = f"Nouveau CV reçu - Domaine {domain}"
            
            # Corps du message
            body = self._create_email_body(domain, candidate_info)
            msg.attach(MIMEText(body, 'html'))
            
            # Ajouter le CV en pièce jointe
            self._attach_cv_file(msg, cv_file_path)
            
            # Envoyer l'email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email envoyé avec succès à {recipient} pour le domaine {domain}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email : {e}")
            return False
    
    def _create_email_body(self, domain: str, candidate_info: dict = None) -> str:
        """
        Crée le corps de l'email
        """
        html = f"""
        <html>
        <body>
            <h2>Nouveau CV reçu - Domaine {domain}</h2>
            <p>Un nouveau CV a été soumis et automatiquement classifié dans votre domaine.</p>
            
            <h3>Détails :</h3>
            <ul>
                <li><strong>Domaine détecté :</strong> {domain}</li>
                <li><strong>Date de réception :</strong> {self._get_current_datetime()}</li>
        """
        
        if candidate_info:
            for key, value in candidate_info.items():
                html += f"<li><strong>{key} :</strong> {value}</li>"
        
        html += """
            </ul>
            
            <p>Le CV est joint à cet email.</p>
            
            <p>Cordialement,<br>
            Système de Classification Automatique</p>
        </body>
        </html>
        """
        
        return html
    
    def _attach_cv_file(self, msg: MIMEMultipart, file_path: str):
        """
        Attache le fichier CV au message
        """
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= CV_candidat.pdf'
            )
            msg.attach(part)
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la pièce jointe : {e}")
    
    def _get_current_datetime(self) -> str:
        """
        Retourne la date et heure actuelles
        """
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y à %H:%M")