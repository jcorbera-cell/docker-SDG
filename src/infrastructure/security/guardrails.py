import re
from typing import Dict, Tuple, Optional
from enum import Enum

class SecurityLevel(Enum):
    """Niveles de seguridad para guardrails"""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"

class Guardrails:
    """Sistema de guardrails para detectar prompt injection y mantener el tema"""
    
    def __init__(self):
        # Patrones comunes de prompt injection/jailbreak
        self.injection_patterns = [
            r'ignore\s+(previous|all|above)',
            r'forget\s+(everything|all|previous)',
            r'you\s+are\s+(now|a)',
            r'act\s+as\s+(if|though)',
            r'pretend\s+to\s+be',
            r'roleplay',
            r'system\s+prompt',
            r'override',
            r'bypass',
            r'jailbreak',
            r'new\s+instructions',
            r'disregard',
            r'disobey',
        ]
        
        # Palabras clave que indican que la consulta está fuera del tema de datos
        self.off_topic_patterns = [
            r'write\s+(code|a\s+program|script)',
            r'create\s+(a\s+file|document)',
            r'delete\s+(file|system|everything)',
            r'format\s+(disk|c:|drive)',
            r'execute\s+(command|shell|terminal)',
            r'run\s+(program|executable|script)',
            r'hack|exploit|vulnerability',
            r'password|credential|secret',
        ]
        
        # Patrones de PII comunes
        self.pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{3}\.\d{2}\.\d{4}\b',  # SSN con puntos
            r'\b\d{16}\b',  # Tarjeta de crédito
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{3}-\d{4}\b',  # Teléfono US
            r'\b\(\d{3}\)\s?\d{3}-\d{4}\b',  # Teléfono US con paréntesis
        ]
    
    def validate_input(
        self, 
        user_input: str, 
        context: Optional[Dict] = None
    ) -> Tuple[SecurityLevel, str]:
        """
        Valida la entrada del usuario
        
        Returns:
            Tuple de (SecurityLevel, mensaje)
        """
        user_input_lower = user_input.lower()
        
        # Verificar prompt injection
        injection_score = self._check_injection(user_input_lower)
        if injection_score > 2:
            return (
                SecurityLevel.DANGEROUS,
                "Se detectó un posible intento de prompt injection. Por favor, mantén tus consultas relacionadas con los datos."
            )
        elif injection_score > 0:
            return (
                SecurityLevel.SUSPICIOUS,
                "Tu consulta contiene patrones inusuales. Asegúrate de que esté relacionada con los datos disponibles."
            )
        
        # Verificar si está fuera del tema
        off_topic_score = self._check_off_topic(user_input_lower)
        if off_topic_score > 1:
            return (
                SecurityLevel.SUSPICIOUS,
                "Tu consulta parece estar fuera del tema de análisis de datos. Por favor, enfócate en consultas sobre los datos disponibles."
            )
        
        return (SecurityLevel.SAFE, "")
    
    def _check_injection(self, text: str) -> int:
        """Verifica patrones de prompt injection"""
        score = 0
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 1
        return score
    
    def _check_off_topic(self, text: str) -> int:
        """Verifica si la consulta está fuera del tema"""
        score = 0
        for pattern in self.off_topic_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 1
        return score
    
    def mask_pii(self, text: str) -> str:
        """
        Enmascara datos PII en el texto
        
        Returns:
            Texto con PII enmascarado
        """
        masked_text = text
        
        # Enmascarar emails
        masked_text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL_MASKED]',
            masked_text
        )
        
        # Enmascarar SSN
        masked_text = re.sub(
            r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b',
            '[SSN_MASKED]',
            masked_text
        )
        
        # Enmascarar tarjetas de crédito
        masked_text = re.sub(
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            '[CARD_MASKED]',
            masked_text
        )
        
        # Enmascarar teléfonos
        masked_text = re.sub(
            r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            '[PHONE_MASKED]',
            masked_text
        )
        
        return masked_text
    
    def should_tokenize_pii(self, query: str) -> bool:
        """Determina si se debe tokenizar PII en la consulta"""
        # Verificar si la consulta contiene patrones que sugieren acceso a PII
        pii_keywords = ['email', 'phone', 'ssn', 'social security', 'credit card', 'personal']
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in pii_keywords)

