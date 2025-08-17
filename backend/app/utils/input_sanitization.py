"""
Task 1.2.4 - Input Sanitization Enhancement
==========================================

Enhanced input sanitization and validation system for LocalStorm v3.0.0.
Provides comprehensive sanitization for AI prompts, user inputs, and API data.

Features:
- AI prompt injection protection
- XSS/HTML sanitization
- SQL injection prevention
- Content filtering and validation
- Input length and format validation
- Special character handling
- PII detection and redaction
"""

import re
import html
import json
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class SanitizationLevel(Enum):
    """Sanitization levels for different input types"""
    BASIC = "basic"          # Basic HTML escape, trim whitespace
    STRICT = "strict"        # Remove all HTML, strict filtering
    AI_PROMPT = "ai_prompt"  # AI-specific sanitization with prompt injection protection
    USER_DATA = "user_data"  # User profile data sanitization
    SEARCH = "search"        # Search query sanitization

class InputSanitizer:
    """
    Comprehensive input sanitization system with configurable levels
    """
    
    # Dangerous patterns that could indicate attacks
    PROMPT_INJECTION_PATTERNS = [
        r'ignore\s+all\s+previous\s+instructions',
        r'you\s+are\s+now\s+(dan|do\s+anything\s+now)',
        r'system:\s*override',
        r'\\n\\nhuman:\s*ignore',
        r'forget\s+everything\s+above',
        r'disregard\s+all\s+prior',
        r'act\s+as\s+if\s+you\s+are',
        r'pretend\s+to\s+be',
        r'roleplay\s+as',
        r'simulate\s+being',
        r'developer\s+mode',
        r'jailbreak',
        r'unrestricted\s+ai',
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
        r'<style[^>]*>.*?</style>',
        r'expression\s*\(',
        r'url\s*\(',
        r'@import',
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"';\s*(drop|delete|insert|update|create|alter|exec|execute)",
        r"union\s+select",
        r"1\s*=\s*1",
        r"or\s+1\s*=\s*1",
        r"and\s+1\s*=\s*1",
        r"';--",
        r"'/*",
        r"xp_",
        r"sp_",
    ]
    
    # PII patterns
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    }
    
    def __init__(self):
        self.max_lengths = {
            'ai_prompt': 8000,
            'user_name': 100,
            'email': 254,
            'general_text': 1000,
            'description': 2000,
            'search_query': 500,
        }
        
    def sanitize_input(
        self, 
        text: str, 
        level: SanitizationLevel = SanitizationLevel.BASIC,
        field_type: str = "general_text",
        preserve_formatting: bool = False
    ) -> Dict[str, Any]:
        """
        Main sanitization method with comprehensive cleaning
        
        Args:
            text: Input text to sanitize
            level: Sanitization level
            field_type: Type of field for length validation
            preserve_formatting: Whether to preserve basic formatting
            
        Returns:
            Dict with sanitized text and metadata
        """
        if not text or not isinstance(text, (str, int, float)):
            return {
                "sanitized": "",
                "original_length": 0,
                "sanitized_length": 0,
                "threats_detected": [],
                "pii_found": [],
                "is_safe": True
            }
            
        original_text = str(text)
        original_length = len(original_text)
        threats_detected = []
        pii_found = []
        
        # Start with basic cleaning
        sanitized = original_text.strip()
        
        # 1. Length validation
        max_length = self.max_lengths.get(field_type, 1000)
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            threats_detected.append(f"input_too_long_{original_length}_chars")
            
        # 2. Check for threats based on level
        if level == SanitizationLevel.AI_PROMPT:
            sanitized, ai_threats = self._sanitize_ai_prompt(sanitized)
            threats_detected.extend(ai_threats)
            
        elif level == SanitizationLevel.STRICT:
            sanitized, strict_threats = self._sanitize_strict(sanitized)
            threats_detected.extend(strict_threats)
            
        elif level == SanitizationLevel.USER_DATA:
            sanitized, user_threats = self._sanitize_user_data(sanitized)
            threats_detected.extend(user_threats)
            
        elif level == SanitizationLevel.SEARCH:
            sanitized, search_threats = self._sanitize_search_query(sanitized)
            threats_detected.extend(search_threats)
            
        # 3. Universal threat detection (run after level-specific sanitization)
        universal_threats = self._check_universal_threats(original_text)  # Check original text for threats
        threats_detected.extend(universal_threats)
        
        # 4. PII detection and redaction
        if level in [SanitizationLevel.AI_PROMPT, SanitizationLevel.STRICT]:
            sanitized, pii_found = self._detect_and_redact_pii(sanitized)
            
        # 5. Final HTML escape if not preserving formatting
        if not preserve_formatting:
            sanitized = html.escape(sanitized)
            
        # 6. Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        is_safe = len(threats_detected) == 0
        
        return {
            "sanitized": sanitized,
            "original_length": original_length,
            "sanitized_length": len(sanitized),
            "threats_detected": threats_detected,
            "pii_found": pii_found,
            "is_safe": is_safe,
            "sanitization_level": level.value,
            "field_type": field_type
        }
    
    def _sanitize_ai_prompt(self, text: str) -> Tuple[str, List[str]]:
        """Sanitize AI prompts with prompt injection protection"""
        threats = []
        sanitized = text
        
        # Check for prompt injection patterns
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                threats.append(f"prompt_injection_{pattern[:20]}")
                # Replace with safe alternative
                sanitized = re.sub(pattern, "[FILTERED]", sanitized, flags=re.IGNORECASE)
                
        # Remove system-level commands
        system_commands = [
            r'\\n\\n(system|human|assistant):\s*',
            r'```[^`]*```',  # Remove code blocks
            r'<\|.*?\|>',    # Remove special tokens
        ]
        
        for pattern in system_commands:
            if re.search(pattern, sanitized, re.IGNORECASE):
                threats.append(f"system_command_{pattern[:20]}")
                sanitized = re.sub(pattern, " ", sanitized, flags=re.IGNORECASE)
                
        # Limit special characters that could break context
        if sanitized.count('\n') > 10:
            threats.append("excessive_newlines")
            sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
            
        return sanitized, threats
    
    def _sanitize_strict(self, text: str) -> Tuple[str, List[str]]:
        """Strict sanitization removing all HTML and scripts"""
        threats = []
        sanitized = text
        
        # Remove dangerous XSS patterns first
        xss_patterns = [
            r'javascript:\s*[^;]*',
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'on\w+\s*=\s*["\'][^"\']*["\']',
            r'on\w+\s*=\s*[^>\s]+',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE | re.DOTALL):
                threats.append(f"xss_pattern_removed")
                sanitized = re.sub(pattern, '[XSS_REMOVED]', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove all HTML tags
        html_pattern = r'<[^>]+>'
        if re.search(html_pattern, sanitized):
            threats.append("html_tags_found")
            sanitized = re.sub(html_pattern, '', sanitized)
            
        # Remove URLs for strict mode
        url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|ftp://[^\s<>"\']+'
        if re.search(url_pattern, sanitized, re.IGNORECASE):
            threats.append("urls_found")
            sanitized = re.sub(url_pattern, '[URL_REMOVED]', sanitized, flags=re.IGNORECASE)
            
        return sanitized, threats
    
    def _sanitize_user_data(self, text: str) -> Tuple[str, List[str]]:
        """Sanitize user profile data"""
        threats = []
        sanitized = text
        
        # Allow basic formatting but remove dangerous elements
        dangerous_html = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
        ]
        
        for pattern in dangerous_html:
            if re.search(pattern, sanitized, re.IGNORECASE | re.DOTALL):
                threats.append(f"dangerous_html_{pattern[:20]}")
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
                
        return sanitized, threats
    
    def _sanitize_search_query(self, text: str) -> Tuple[str, List[str]]:
        """Sanitize search queries"""
        threats = []
        sanitized = text
        
        # Remove search operators that could be misused
        dangerous_operators = [
            r'site:\s*[^\s]+',
            r'filetype:\s*[^\s]+',
            r'inurl:\s*[^\s]+',
            r'intext:\s*[^\s]+',
        ]
        
        for pattern in dangerous_operators:
            if re.search(pattern, sanitized, re.IGNORECASE):
                threats.append(f"search_operator_{pattern[:20]}")
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
                
        return sanitized, threats
    
    def _check_universal_threats(self, text: str) -> List[str]:
        """Check for universal security threats"""
        threats = []
        
        # XSS patterns
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                threats.append(f"xss_{pattern[:20]}")
                
        # SQL injection patterns
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                threats.append(f"sql_injection_{pattern[:20]}")
                
        # Check for null bytes and control characters
        if '\x00' in text or any(ord(c) < 32 and c not in '\n\r\t' for c in text):
            threats.append("control_characters")
            
        # Check for excessive repetition (potential DoS)
        if len(set(text)) < len(text) / 10 and len(text) > 100:
            threats.append("excessive_repetition")
            
        return threats
    
    def _detect_and_redact_pii(self, text: str) -> Tuple[str, List[str]]:
        """Detect and redact PII from text"""
        pii_found = []
        sanitized = text
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, sanitized, re.IGNORECASE)
            if matches:
                pii_found.extend([f"{pii_type}_{len(matches)}_instances"])
                # Redact PII
                sanitized = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', sanitized, flags=re.IGNORECASE)
                
        return sanitized, pii_found
    
    def validate_ai_prompt(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Specialized validation for AI prompts with enhanced security
        
        Args:
            prompt: The AI prompt to validate
            context: Additional context for validation
            
        Returns:
            Validation result with sanitized prompt and security analysis
        """
        # Sanitize the prompt
        result = self.sanitize_input(
            prompt, 
            level=SanitizationLevel.AI_PROMPT,
            field_type="ai_prompt",
            preserve_formatting=False
        )
        
        # Additional AI-specific validations
        additional_checks = []
        
        # Check prompt complexity (potential for abuse)
        word_count = len(result["sanitized"].split())
        if word_count > 1000:
            additional_checks.append("prompt_too_complex")
            
        # Check for role-playing attempts
        roleplay_indicators = [
            "pretend", "act as", "roleplay", "simulate", "imagine you are",
            "you are now", "switch to", "become", "transform into"
        ]
        
        for indicator in roleplay_indicators:
            if indicator.lower() in result["sanitized"].lower():
                additional_checks.append(f"roleplay_attempt_{indicator}")
                
        # Check context data if provided
        context_threats = []
        if context:
            for key, value in context.items():
                if isinstance(value, str):
                    context_result = self.sanitize_input(
                        value, 
                        level=SanitizationLevel.BASIC,
                        field_type="general_text"
                    )
                    if not context_result["is_safe"]:
                        context_threats.extend([f"context_{key}_{threat}" for threat in context_result["threats_detected"]])
        
        # Calculate overall safety score
        total_threats = len(result["threats_detected"]) + len(additional_checks) + len(context_threats)
        safety_score = max(0, 100 - (total_threats * 10))
        
        return {
            **result,
            "additional_checks": additional_checks,
            "context_threats": context_threats,
            "safety_score": safety_score,
            "is_ai_safe": total_threats == 0,
            "validation_timestamp": datetime.now().isoformat()
        }

# Global sanitizer instance
input_sanitizer = InputSanitizer()

def sanitize_text(
    text: str, 
    level: str = "basic",
    field_type: str = "general_text",
    preserve_formatting: bool = False
) -> Dict[str, Any]:
    """
    Convenience function for text sanitization
    
    Args:
        text: Text to sanitize
        level: Sanitization level (basic, strict, ai_prompt, user_data, search)
        field_type: Field type for validation
        preserve_formatting: Whether to preserve formatting
        
    Returns:
        Sanitization result dictionary
    """
    sanitization_level = SanitizationLevel(level)
    return input_sanitizer.sanitize_input(
        text, 
        level=sanitization_level,
        field_type=field_type,
        preserve_formatting=preserve_formatting
    )

def validate_ai_prompt(prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convenience function for AI prompt validation
    
    Args:
        prompt: AI prompt to validate
        context: Optional context data
        
    Returns:
        Validation result with security analysis
    """
    return input_sanitizer.validate_ai_prompt(prompt, context)
