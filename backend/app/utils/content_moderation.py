"""
Content Moderation System - Task 1.2.5
=====================================

Comprehensive content moderation for AI responses and user-generated content.
Implements multiple layers of content filtering, safety scoring, and policy enforcement.
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ModerationLevel(Enum):
    """Content moderation levels"""
    PERMISSIVE = "permissive"    # Basic filtering only
    STANDARD = "standard"        # Standard community guidelines
    STRICT = "strict"           # Strict professional environment
    ENTERPRISE = "enterprise"   # Enterprise-grade compliance

class ContentCategory(Enum):
    """Content categories for moderation"""
    SAFE = "safe"
    POTENTIALLY_HARMFUL = "potentially_harmful"
    HARMFUL = "harmful"
    BLOCKED = "blocked"

class ViolationType(Enum):
    """Types of content violations"""
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    VIOLENCE = "violence"
    ADULT_CONTENT = "adult_content"
    SPAM = "spam"
    MISINFORMATION = "misinformation"
    PRIVACY_VIOLATION = "privacy_violation"
    COPYRIGHT = "copyright"
    MALICIOUS_CODE = "malicious_code"
    PHISHING = "phishing"
    FINANCIAL_FRAUD = "financial_fraud"
    INAPPROPRIATE_LANGUAGE = "inappropriate_language"

@dataclass
class ModerationResult:
    """Result of content moderation"""
    original_content: str
    moderated_content: str
    is_safe: bool
    category: ContentCategory
    violations: List[ViolationType]
    confidence_score: float  # 0-100
    explanation: str
    suggested_action: str
    metadata: Dict[str, Any]

class ContentModerator:
    """Advanced content moderation system for AI responses and user content"""
    
    def __init__(self):
        self.moderation_patterns = self._load_moderation_patterns()
        self.content_filters = self._initialize_content_filters()
        self.policy_rules = self._load_policy_rules()
        
    def _load_moderation_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Load and compile moderation patterns"""
        patterns = {
            ViolationType.HATE_SPEECH.value: [
                re.compile(r'\b(hate|despise|loathe)\s+(all|every|everyone|everybody)\s*\w*', re.IGNORECASE),
                re.compile(r'\b(kill|destroy|eliminate)\s+(all|every|everyone|everybody)\s*\w*', re.IGNORECASE),
                re.compile(r'\b(racial|ethnic|religious)\s+(slur|epithet)', re.IGNORECASE),
                re.compile(r'\b(inferior|superior)\s+(race|ethnicity)', re.IGNORECASE),
                re.compile(r'\bhate\s+everyone\b', re.IGNORECASE),
            ],
            
            ViolationType.HARASSMENT.value: [
                re.compile(r'\b(stalking|threatening|intimidating)', re.IGNORECASE),
                re.compile(r'\b(doxx|dox|personal\s+info)', re.IGNORECASE),
                re.compile(r'\b(expose|reveal)\s+(address|phone|email)', re.IGNORECASE),
                re.compile(r'\b(harass|bully|intimidate)\s+someone', re.IGNORECASE),
            ],
            
            ViolationType.VIOLENCE.value: [
                re.compile(r'\b(bomb|explosive|attack)\s+(instructions|guide|how\s+to|making)', re.IGNORECASE),
                re.compile(r'\b(how\s+to\s+)?(kill|murder|harm)\s+(someone|people)', re.IGNORECASE),
                re.compile(r'\b(weapon|gun|knife)\s+(making|creation|instructions)', re.IGNORECASE),
                re.compile(r'\b(violence|assault|battery)\s+(guide|instructions)', re.IGNORECASE),
                re.compile(r'\b(detailed\s+instructions).*\b(bomb|attack|kill)', re.IGNORECASE),
                re.compile(r'\b(make\s+a\s+bomb|build\s+explosives)', re.IGNORECASE),
            ],
            
            ViolationType.ADULT_CONTENT.value: [
                re.compile(r'\b(explicit|graphic)\s+(sexual|adult)\s+content', re.IGNORECASE),
                re.compile(r'\b(pornographic|erotic)\s+(material|content)', re.IGNORECASE),
                re.compile(r'\b(sexual|intimate)\s+(images|photos|videos)', re.IGNORECASE),
            ],
            
            ViolationType.SPAM.value: [
                re.compile(r'\b(click\s+here|visit\s+now)\b.*\b(urgent|limited\s+time)', re.IGNORECASE),
                re.compile(r'\b(make\s+money|earn\s+\$|get\s+rich)\s+(fast|quick)', re.IGNORECASE),
                re.compile(r'\b(free\s+money|cash\s+prize|you\s+won)', re.IGNORECASE),
                re.compile(r'\b(act\s+now|call\s+immediately)', re.IGNORECASE),
            ],
            
            ViolationType.MISINFORMATION.value: [
                re.compile(r'\b(covid|vaccine)\s+(conspiracy|hoax|fake)', re.IGNORECASE),
                re.compile(r'\b(election|voting)\s+(fraud|rigged|stolen)', re.IGNORECASE),
                re.compile(r'\b(government|media)\s+(lies|coverup|conspiracy)', re.IGNORECASE),
                re.compile(r'\b(proven\s+fact|scientists\s+confirm)\s+.*\b(but\s+they)', re.IGNORECASE),
            ],
            
            ViolationType.MALICIOUS_CODE.value: [
                re.compile(r'\b(malware|virus|trojan)\s+(code|script)', re.IGNORECASE),
                re.compile(r'\b(keylogger|backdoor|rootkit)', re.IGNORECASE),
                re.compile(r'\b(exploit|vulnerability)\s+(code|script)', re.IGNORECASE),
                re.compile(r'\b(sql\s+injection|xss|cross\s+site)', re.IGNORECASE),
            ],
            
            ViolationType.PHISHING.value: [
                re.compile(r'\b(verify\s+account|update\s+payment)', re.IGNORECASE),
                re.compile(r'\b(suspended\s+account|immediate\s+action)', re.IGNORECASE),
                re.compile(r'\b(click\s+link|verify\s+identity)', re.IGNORECASE),
                re.compile(r'\b(paypal|amazon|microsoft)\s+(security|verification)', re.IGNORECASE),
            ],
            
            ViolationType.FINANCIAL_FRAUD.value: [
                re.compile(r'\b(ponzi|pyramid)\s+(scheme|scam)', re.IGNORECASE),
                re.compile(r'\b(get\s+rich|easy\s+money|guaranteed\s+profit)', re.IGNORECASE),
                re.compile(r'\b(investment|trading)\s+(secret|guaranteed)', re.IGNORECASE),
                re.compile(r'\b(cryptocurrency|crypto)\s+(scam|fraud)', re.IGNORECASE),
            ],
            
            ViolationType.INAPPROPRIATE_LANGUAGE.value: [
                re.compile(r'\b(f\*{2,}k|s\*{2,}t|d\*{2,}n)\b', re.IGNORECASE),
                re.compile(r'\b(profanity|vulgar|offensive)\s+(language|words)', re.IGNORECASE),
            ],
        }
        
        return patterns
    
    def _initialize_content_filters(self) -> Dict[str, Any]:
        """Initialize content filtering rules"""
        return {
            ModerationLevel.PERMISSIVE.value: {
                "blocked_violations": [
                    ViolationType.VIOLENCE,
                    ViolationType.HATE_SPEECH,
                    ViolationType.MALICIOUS_CODE,
                    ViolationType.PHISHING,
                    ViolationType.FINANCIAL_FRAUD
                ],
                "warning_violations": [
                    ViolationType.ADULT_CONTENT,
                    ViolationType.SPAM,
                    ViolationType.MISINFORMATION
                ],
                "confidence_threshold": 80
            },
            
            ModerationLevel.STANDARD.value: {
                "blocked_violations": [
                    ViolationType.VIOLENCE,
                    ViolationType.HATE_SPEECH,
                    ViolationType.HARASSMENT,
                    ViolationType.ADULT_CONTENT,
                    ViolationType.MALICIOUS_CODE,
                    ViolationType.PHISHING,
                    ViolationType.FINANCIAL_FRAUD
                ],
                "warning_violations": [
                    ViolationType.SPAM,
                    ViolationType.MISINFORMATION,
                    ViolationType.INAPPROPRIATE_LANGUAGE
                ],
                "confidence_threshold": 70
            },
            
            ModerationLevel.STRICT.value: {
                "blocked_violations": [
                    ViolationType.VIOLENCE,
                    ViolationType.HATE_SPEECH,
                    ViolationType.HARASSMENT,
                    ViolationType.ADULT_CONTENT,
                    ViolationType.SPAM,
                    ViolationType.MISINFORMATION,
                    ViolationType.MALICIOUS_CODE,
                    ViolationType.PHISHING,
                    ViolationType.FINANCIAL_FRAUD,
                    ViolationType.INAPPROPRIATE_LANGUAGE
                ],
                "warning_violations": [
                    ViolationType.PRIVACY_VIOLATION,
                    ViolationType.COPYRIGHT
                ],
                "confidence_threshold": 60
            },
            
            ModerationLevel.ENTERPRISE.value: {
                "blocked_violations": list(ViolationType),
                "warning_violations": [],
                "confidence_threshold": 50
            }
        }
    
    def _load_policy_rules(self) -> Dict[str, Any]:
        """Load content policy rules"""
        return {
            "ai_response_filtering": {
                "max_content_length": 10000,
                "required_disclaimers": [
                    "medical advice",
                    "legal advice", 
                    "financial advice",
                    "professional advice"
                ],
                "blocked_topics": [
                    "illegal activities",
                    "harmful instructions",
                    "personal attacks"
                ]
            },
            
            "user_content_filtering": {
                "max_content_length": 5000,
                "rate_limit_violations": True,
                "escalation_thresholds": {
                    "warning": 3,
                    "temporary_restriction": 5,
                    "permanent_ban": 10
                }
            }
        }
    
    def moderate_content(
        self, 
        content: str, 
        content_type: str = "ai_response",
        moderation_level: ModerationLevel = ModerationLevel.STANDARD,
        user_context: Optional[Dict[str, Any]] = None
    ) -> ModerationResult:
        """
        Moderate content using comprehensive filtering system
        
        Args:
            content: Content to moderate
            content_type: Type of content (ai_response, user_message, etc.)
            moderation_level: Level of moderation to apply
            user_context: Additional context about the user/session
            
        Returns:
            ModerationResult with moderation decision and processed content
        """
        
        if not content or not content.strip():
            return ModerationResult(
                original_content=content,
                moderated_content=content,
                is_safe=True,
                category=ContentCategory.SAFE,
                violations=[],
                confidence_score=100.0,
                explanation="Empty or whitespace-only content",
                suggested_action="allow",
                metadata={}
            )
        
        # Step 1: Detect violations
        violations, confidence_scores = self._detect_violations(content)
        
        # Step 2: Calculate overall confidence
        overall_confidence = max(confidence_scores) if confidence_scores else 0.0
        
        # Step 3: Determine category and action based on moderation level
        filter_rules = self.content_filters[moderation_level.value]
        
        blocked_violations = set(filter_rules["blocked_violations"])
        warning_violations = set(filter_rules["warning_violations"])
        confidence_threshold = filter_rules["confidence_threshold"]
        
        # Check if any detected violations should block content
        blocking_violations = [v for v in violations if v in blocked_violations]
        warning_only_violations = [v for v in violations if v in warning_violations and v not in blocked_violations]
        
        # Step 4: Determine content category
        if blocking_violations and overall_confidence >= confidence_threshold:
            category = ContentCategory.BLOCKED
            is_safe = False
            suggested_action = "block"
        elif warning_only_violations and overall_confidence >= confidence_threshold:
            category = ContentCategory.POTENTIALLY_HARMFUL
            is_safe = True  # Allow with warning
            suggested_action = "warn"
        elif violations and overall_confidence < confidence_threshold:
            category = ContentCategory.POTENTIALLY_HARMFUL
            is_safe = True  # Low confidence, allow but monitor
            suggested_action = "monitor"
        else:
            category = ContentCategory.SAFE
            is_safe = True
            suggested_action = "allow"
        
        # Step 5: Generate moderated content
        moderated_content = self._apply_content_filtering(
            content, violations, category, moderation_level
        )
        
        # Step 6: Generate explanation
        explanation = self._generate_explanation(violations, confidence_scores, category)
        
        # Step 7: Collect metadata
        metadata = {
            "moderation_level": moderation_level.value,
            "content_type": content_type,
            "processing_timestamp": datetime.now().isoformat(),
            "violation_details": {v.value: confidence_scores[i] for i, v in enumerate(violations)},
            "user_context": user_context or {},
            "filter_version": "1.0.0"
        }
        
        return ModerationResult(
            original_content=content,
            moderated_content=moderated_content,
            is_safe=is_safe,
            category=category,
            violations=violations,
            confidence_score=overall_confidence,
            explanation=explanation,
            suggested_action=suggested_action,
            metadata=metadata
        )
    
    def _detect_violations(self, content: str) -> Tuple[List[ViolationType], List[float]]:
        """Detect content violations and confidence scores"""
        violations = []
        confidence_scores = []
        
        content_lower = content.lower()
        
        for violation_type, patterns in self.moderation_patterns.items():
            violation_enum = ViolationType(violation_type)
            max_confidence = 0.0
            
            for pattern in patterns:
                matches = pattern.findall(content)
                if matches:
                    # Calculate confidence based on pattern specificity and match count
                    base_confidence = 60.0  # Base confidence for pattern match
                    match_bonus = min(len(matches) * 10, 30)  # Bonus for multiple matches
                    pattern_specificity = len(pattern.pattern) / 50  # More specific patterns get higher confidence
                    
                    confidence = min(base_confidence + match_bonus + (pattern_specificity * 10), 95.0)
                    max_confidence = max(max_confidence, confidence)
            
            if max_confidence > 0:
                violations.append(violation_enum)
                confidence_scores.append(max_confidence)
        
        # Additional contextual analysis
        self._analyze_context_violations(content, violations, confidence_scores)
        
        return violations, confidence_scores
    
    def _analyze_context_violations(self, content: str, violations: List[ViolationType], confidence_scores: List[float]):
        """Analyze contextual violations that require more complex logic"""
        
        # Check for potential misinformation patterns
        misinformation_indicators = [
            "scientists don't want you to know",
            "big pharma conspiracy",
            "mainstream media lies",
            "government coverup",
            "proven fact that they hide"
        ]
        
        for indicator in misinformation_indicators:
            if indicator.lower() in content.lower():
                if ViolationType.MISINFORMATION not in violations:
                    violations.append(ViolationType.MISINFORMATION)
                    confidence_scores.append(65.0)
                break
        
        # Check for sophisticated spam patterns
        spam_indicators = [
            ("urgent", "limited time", "act now"),
            ("guaranteed", "100%", "risk-free"),
            ("earn money", "work from home", "no experience"),
        ]
        
        for indicator_group in spam_indicators:
            if all(indicator.lower() in content.lower() for indicator in indicator_group):
                if ViolationType.SPAM not in violations:
                    violations.append(ViolationType.SPAM)
                    confidence_scores.append(70.0)
                break
        
        # Check for privacy violations (PII exposure attempts)
        pii_patterns = [
            r'\b(social security|ssn)\s+number\b',
            r'\b(credit card|bank account)\s+number\b',
            r'\b(driver\'s license|passport)\s+number\b'
        ]
        
        for pattern in pii_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                if ViolationType.PRIVACY_VIOLATION not in violations:
                    violations.append(ViolationType.PRIVACY_VIOLATION)
                    confidence_scores.append(80.0)
                break
    
    def _apply_content_filtering(
        self, 
        content: str, 
        violations: List[ViolationType], 
        category: ContentCategory,
        moderation_level: ModerationLevel
    ) -> str:
        """Apply content filtering based on violations and category"""
        
        if category == ContentCategory.BLOCKED:
            return self._generate_blocked_content_message(violations)
        
        if category == ContentCategory.POTENTIALLY_HARMFUL:
            return self._add_content_warnings(content, violations)
        
        # For safe content, apply minimal filtering
        return self._apply_basic_filtering(content)
    
    def _generate_blocked_content_message(self, violations: List[ViolationType]) -> str:
        """Generate message for blocked content"""
        
        primary_violation = violations[0] if violations else ViolationType.INAPPROPRIATE_LANGUAGE
        
        messages = {
            ViolationType.HATE_SPEECH: "This content has been blocked due to hate speech policy violations. CapeControl promotes respectful communication.",
            ViolationType.HARASSMENT: "This content has been blocked due to harassment policy violations. Please engage respectfully with others.",
            ViolationType.VIOLENCE: "This content has been blocked due to violent content policy violations. Safety is our priority.",
            ViolationType.ADULT_CONTENT: "This content has been blocked due to adult content policy violations. Please keep discussions professional.",
            ViolationType.MALICIOUS_CODE: "This content has been blocked due to security policy violations. Malicious code is not permitted.",
            ViolationType.PHISHING: "This content has been blocked due to phishing detection. Protect yourself and others from scams.",
            ViolationType.FINANCIAL_FRAUD: "This content has been blocked due to financial fraud detection. Investment advice should come from licensed professionals.",
        }
        
        return messages.get(
            primary_violation, 
            "This content has been blocked due to community guideline violations. Please review our content policy."
        )
    
    def _add_content_warnings(self, content: str, violations: List[ViolationType]) -> str:
        """Add warnings to potentially harmful content"""
        
        warnings = []
        
        if ViolationType.MISINFORMATION in violations:
            warnings.append("⚠️ **Content Warning**: This information should be verified with reliable sources.")
        
        if ViolationType.ADULT_CONTENT in violations:
            warnings.append("⚠️ **Content Warning**: This content may not be suitable for all audiences.")
        
        if ViolationType.SPAM in violations:
            warnings.append("⚠️ **Content Warning**: This content contains promotional elements. Exercise caution.")
        
        if ViolationType.INAPPROPRIATE_LANGUAGE in violations:
            warnings.append("⚠️ **Language Warning**: This content contains language that some may find inappropriate.")
        
        if warnings:
            warning_text = "\n".join(warnings)
            return f"{warning_text}\n\n{content}"
        
        return content
    
    def _apply_basic_filtering(self, content: str) -> str:
        """Apply basic filtering to safe content"""
        
        # Replace obvious profanity with asterisks
        profanity_patterns = [
            (r'\bf\*{2,}k\b', 'f***'),
            (r'\bs\*{2,}t\b', 's***'),
            (r'\bd\*{2,}n\b', 'd***'),
        ]
        
        filtered_content = content
        for pattern, replacement in profanity_patterns:
            filtered_content = re.sub(pattern, replacement, filtered_content, flags=re.IGNORECASE)
        
        return filtered_content
    
    def _generate_explanation(
        self, 
        violations: List[ViolationType], 
        confidence_scores: List[float],
        category: ContentCategory
    ) -> str:
        """Generate human-readable explanation of moderation decision"""
        
        if not violations:
            return "Content passed all moderation checks and is considered safe."
        
        if category == ContentCategory.BLOCKED:
            primary_violation = violations[0]
            primary_confidence = confidence_scores[0] if confidence_scores else 0
            return f"Content blocked due to {primary_violation.value.replace('_', ' ')} violation (confidence: {primary_confidence:.1f}%)."
        
        if category == ContentCategory.POTENTIALLY_HARMFUL:
            violation_list = [v.value.replace('_', ' ') for v in violations]
            return f"Content flagged for potential policy concerns: {', '.join(violation_list)}. Warnings added."
        
        return "Content reviewed and approved with minor filtering applied."
    
    def moderate_ai_response(
        self, 
        ai_response: str, 
        user_context: Optional[Dict[str, Any]] = None,
        moderation_level: ModerationLevel = ModerationLevel.STANDARD
    ) -> ModerationResult:
        """Moderate AI-generated response content"""
        
        # Add AI-specific context
        ai_context = {
            "content_type": "ai_response",
            "requires_disclaimers": self._check_disclaimer_requirements(ai_response),
            **(user_context or {})
        }
        
        result = self.moderate_content(
            ai_response, 
            content_type="ai_response",
            moderation_level=moderation_level,
            user_context=ai_context
        )
        
        # For AI responses, be more lenient with financial content - add disclaimers instead of blocking
        if not result.is_safe and ViolationType.FINANCIAL_FRAUD in result.violations:
            # Remove financial fraud from violations for AI responses and add disclaimer instead
            result.violations = [v for v in result.violations if v != ViolationType.FINANCIAL_FRAUD]
            if not result.violations:  # If only financial fraud was the issue
                result.is_safe = True
                result.category = ContentCategory.SAFE
                result.moderated_content = ai_response  # Use original content
                ai_context["requires_disclaimers"].append("financial")
        
        # Add AI-specific post-processing
        if result.is_safe and ai_context["requires_disclaimers"]:
            result.moderated_content = self._add_ai_disclaimers(result.moderated_content, ai_context["requires_disclaimers"])
        
        return result
    
    def _check_disclaimer_requirements(self, content: str) -> List[str]:
        """Check if AI response requires disclaimers"""
        required_disclaimers = []
        content_lower = content.lower()
        
        disclaimer_patterns = {
            "medical": [r'\b(diagnos|treatment|medication|symptom|disease|illness)\b'],
            "legal": [r'\b(lawsuit|legal|court|attorney|law|regulation)\b'],
            "financial": [r'\b(investment|trading|stock|crypto|financial|money|profit)\b'],
            "professional": [r'\b(career|job|professional|business|advice)\b']
        }
        
        for disclaimer_type, patterns in disclaimer_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    required_disclaimers.append(disclaimer_type)
                    break
        
        return required_disclaimers
    
    def _add_ai_disclaimers(self, content: str, disclaimer_types: List[str]) -> str:
        """Add appropriate disclaimers to AI content"""
        
        disclaimers = {
            "medical": "\n\n*Disclaimer: This information is for educational purposes only and is not medical advice. Consult a healthcare professional for medical concerns.*",
            "legal": "\n\n*Disclaimer: This information is for educational purposes only and is not legal advice. Consult a qualified attorney for legal matters.*",
            "financial": "\n\n*Disclaimer: This information is for educational purposes only and is not financial advice. Consult a licensed financial advisor before making investment decisions.*",
            "professional": "\n\n*Disclaimer: This information is general guidance only. Professional situations vary, and specific advice should be sought from qualified professionals.*"
        }
        
        disclaimer_text = ""
        for disclaimer_type in disclaimer_types:
            if disclaimer_type in disclaimers:
                disclaimer_text += disclaimers[disclaimer_type]
        
        return content + disclaimer_text
    
    def get_moderation_stats(self, timeframe: str = "24h") -> Dict[str, Any]:
        """Get moderation statistics for monitoring"""
        # This would typically connect to a database to get real stats
        # For now, return example structure
        return {
            "timeframe": timeframe,
            "total_content_processed": 0,
            "blocked_content": 0,
            "warned_content": 0,
            "safe_content": 0,
            "top_violations": [],
            "average_confidence": 0.0,
            "processing_time_ms": 0.0
        }

# Default content moderator instance
content_moderator = ContentModerator()

# Convenience functions for common use cases
def moderate_ai_response(
    response: str, 
    user_context: Optional[Dict[str, Any]] = None,
    level: ModerationLevel = ModerationLevel.STANDARD
) -> ModerationResult:
    """Moderate AI response with standard settings"""
    return content_moderator.moderate_ai_response(response, user_context, level)

def moderate_user_content(
    content: str,
    content_type: str = "user_message", 
    level: ModerationLevel = ModerationLevel.STANDARD
) -> ModerationResult:
    """Moderate user-generated content"""
    return content_moderator.moderate_content(content, content_type, level)

def is_content_safe(content: str, level: ModerationLevel = ModerationLevel.STANDARD) -> bool:
    """Quick safety check for content"""
    result = content_moderator.moderate_content(content, moderation_level=level)
    return result.is_safe
