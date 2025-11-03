"""
Input Guardrails for MathGPT
Validates and filters user input for privacy, content filtering, and mathematical relevance.
"""

import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class InputGuardrailResult(BaseModel):
    """Result of input guardrail validation."""
    is_valid: bool
    sanitized_input: str
    filtered_terms: List[str] = Field(default_factory=list)
    pii_detected: bool = False
    pii_types: List[str] = Field(default_factory=list)
    is_mathematical: bool = True
    warnings: List[str] = Field(default_factory=list)


class InputGuardrail:
    """Guardrail for validating and sanitizing user input."""
    
    def __init__(self):
        # Common PII patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        }
        
        # Inappropriate content patterns (basic - can be enhanced)
        self.inappropriate_patterns = [
            r'\b(hack|exploit|breach|attack|malware|virus)\b',
            r'\b(kill|murder|suicide|violence)\b',
        ]
        
        # Mathematical keywords (indicators of math-related queries)
        self.math_keywords = [
            'calculate', 'solve', 'prove', 'derive', 'integrate', 'differentiate',
            'equation', 'function', 'theorem', 'formula', 'graph', 'plot', 'matrix',
            'vector', 'limit', 'derivative', 'integral', 'summation', 'series',
            'algebra', 'calculus', 'geometry', 'trigonometry', 'statistics',
            'probability', 'linear', 'quadratic', 'polynomial', 'exponential',
            'logarithm', 'sine', 'cosine', 'tangent', 'fourier', 'transform'
        ]
        
    def validate(self, user_input: str) -> InputGuardrailResult:
        """
        Validate and sanitize user input.
        
        Args:
            user_input: Raw user input string
            
        Returns:
            InputGuardrailResult with validation status and sanitized input
        """
        if not user_input or not isinstance(user_input, str):
            return InputGuardrailResult(
                is_valid=False,
                sanitized_input="",
                warnings=["Empty or invalid input provided"]
            )
        
        sanitized = user_input.strip()
        filtered_terms = []
        pii_detected = False
        pii_types = []
        warnings = []
        
        # Check for PII
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, sanitized, re.IGNORECASE)
            if matches:
                pii_detected = True
                pii_types.append(pii_type)
                # Redact PII
                for match in matches:
                    sanitized = sanitized.replace(match, f"[{pii_type.upper()}_REDACTED]")
                    filtered_terms.append(match)
                warnings.append(f"Detected and redacted {pii_type}: {len(matches)} occurrence(s)")
        
        # Check for inappropriate content (basic filtering)
        for pattern in self.inappropriate_patterns:
            matches = re.findall(pattern, sanitized, re.IGNORECASE)
            if matches:
                warnings.append(f"Inappropriate content detected: {len(matches)} term(s)")
        
        # Check mathematical relevance
        is_mathematical = self._is_mathematical_query(sanitized)
        if not is_mathematical:
            warnings.append("Query may not be mathematical - please ensure it's math-related")
        
        # Additional validation: length check
        if len(sanitized) > 2000:
            warnings.append("Input is very long - truncating to 2000 characters")
            sanitized = sanitized[:2000]
        
        # SQL injection attempt detection (basic)
        sql_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', 'UNION', '--']
        input_upper = sanitized.upper()
        if any(keyword in input_upper for keyword in sql_keywords):
            warnings.append("Potential SQL injection attempt detected")
        
        # Final validation: if PII was detected, mark as potentially invalid
        is_valid = not pii_detected or len(warnings) == 1  # Allow with warning if only PII
        
        return InputGuardrailResult(
            is_valid=is_valid,
            sanitized_input=sanitized,
            filtered_terms=filtered_terms,
            pii_detected=pii_detected,
            pii_types=pii_types,
            is_mathematical=is_mathematical,
            warnings=warnings
        )
    
    def _is_mathematical_query(self, query: str) -> bool:
        """
        Check if query appears to be mathematical.
        
        Args:
            query: Input query string
            
        Returns:
            True if query appears mathematical
        """
        query_lower = query.lower()
        
        # Check for math keywords
        has_keywords = any(keyword in query_lower for keyword in self.math_keywords)
        
        # Check for mathematical symbols
        math_symbols = ['+', '-', '*', '/', '=', '√', '∫', '∑', '∏', '∂', 'Δ', 'π', '∞']
        has_symbols = any(symbol in query for symbol in math_symbols)
        
        # Check for LaTeX math notation
        has_latex = bool(re.search(r'\$.*?\$|\\[a-zA-Z]+', query))
        
        # Check for numbers or equations
        has_equations = bool(re.search(r'\d+[\s\+\-\*/=]+\d+|\(.*?\)', query))
        
        return has_keywords or has_symbols or has_latex or has_equations or len(query.split()) <= 5


def create_input_guardrail() -> InputGuardrail:
    """Factory function to create an input guardrail instance."""
    return InputGuardrail()

