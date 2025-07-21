from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Optional, Dict, Any
import requests
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class OpenRouterLLM(LLM):
    """LLM personnalisé pour OpenRouter"""
    
    model_name: str = settings.openrouter_model
    api_key: str = settings.openrouter_api_key
    
    @property
    def _llm_type(self) -> str:
        return "openrouter"
    
    def _call(self, prompt: str, stop: Optional[list] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 100
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à OpenRouter: {e}")
            raise

class CVClassifier:
    def __init__(self):
        self.llm = OpenRouterLLM()
        self.prompt_template = PromptTemplate(
            input_variables=["cv_text"],
            template="""
Analysez ce CV et classifiez-le dans l'un de ces 3 domaines UNIQUEMENT :
- IT (Informatique, développement, technologie, programmation, data science, cybersécurité, etc.)
- RH (Ressources humaines, recrutement, formation, gestion du personnel, etc.)
- Multimédia (Design graphique, vidéo, audio, animation, marketing digital, communication visuelle, etc.)

CV à analyser :
{cv_text}

Répondez EXACTEMENT dans ce format : "Domaine : [IT/RH/Multimédia]"
Ne donnez aucune explication supplémentaire.

Réponse :"""
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def classify_cv(self, cv_text: str) -> Optional[str]:
        """
        Classifie un CV et retourne le domaine
        """
        try:
            # Limiter la taille du texte pour éviter les tokens excessifs
            if len(cv_text) > 3000:
                cv_text = cv_text[:3000] + "..."
            
            result = self.chain.run(cv_text=cv_text)
            
            # Nettoyer et extraire le domaine
            domain = self._extract_domain(result)
            logger.info(f"CV classifié comme : {domain}")
            return domain
            
        except Exception as e:
            logger.error(f"Erreur lors de la classification : {e}")
            return None
    
    def _extract_domain(self, llm_response: str) -> Optional[str]:
        """
        Extrait le domaine de la réponse du LLM
        """
        response_lower = llm_response.lower().strip()
        
        if "domaine : it" in response_lower or "domaine: it" in response_lower:
            return "IT"
        elif "domaine : rh" in response_lower or "domaine: rh" in response_lower:
            return "RH"
        elif "domaine : multimédia" in response_lower or "domaine: multimédia" in response_lower:
            return "Multimédia"
        else:
            # Fallback - chercher les mots clés directement
            if any(word in response_lower for word in ["it", "informatique", "développement", "programmation"]):
                return "IT"
            elif any(word in response_lower for word in ["rh", "ressources humaines", "recrutement"]):
                return "RH"
            elif any(word in response_lower for word in ["multimédia", "design", "graphique"]):
                return "Multimédia"
            
            logger.warning(f"Impossible d'extraire le domaine de : {llm_response}")
            return None