"""
Output Guardrails for MathGPT
Validates agent responses for mathematical correctness, educational appropriateness, and quality.
"""

import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class OutputGuardrailResult(BaseModel):
    """Result of output guardrail validation."""
    is_valid: bool
    quality_score: float = Field(ge=0.0, le=1.0)
    is_mathematically_sound: bool = True
    is_educational: bool = True
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class OutputGuardrail:
    """Guardrail for validating agent output."""
    
    def __init__(self):
        # Mathematical correctness indicators
        self.positive_indicators = [
            'theorem', 'proof', 'formula', 'equation', 'solution', 'solve',
            'step', 'method', 'approach', 'calculation', 'result'
        ]
        
        # Negative indicators (inappropriate content)
        self.negative_indicators = [
            'hate', 'violence', 'illegal', 'harmful', 'dangerous'
        ]
        
        # Educational tone indicators
        self.educational_indicators = [
            'explain', 'understand', 'concept', 'example', 'illustrate',
            'demonstrate', 'show', 'note', 'remember', 'important'
        ]
        
    def validate(self, agent_output: str, query: str = "") -> OutputGuardrailResult:
        """
        Validate agent output for quality and appropriateness.
        
        Args:
            agent_output: Agent response string
            query: Original user query (for context)
            
        Returns:
            OutputGuardrailResult with validation status and quality metrics
        """
        if not agent_output or not isinstance(agent_output, str):
            return OutputGuardrailResult(
                is_valid=False,
                quality_score=0.0,
                warnings=["Empty or invalid output provided"]
            )
        
        warnings = []
        suggestions = []
        quality_scores = []
        
        # Length check
        if len(agent_output) < 50:
            warnings.append("Response is very short - may lack detail")
            quality_scores.append(0.3)
        elif len(agent_output) > 5000:
            warnings.append("Response is very long - may need summarization")
            quality_scores.append(0.9)
        else:
            quality_scores.append(1.0)
        
        # Check for mathematical content
        is_mathematically_sound = self._check_mathematical_soundness(agent_output)
        if not is_mathematically_sound:
            warnings.append("Response may lack mathematical rigor")
            quality_scores.append(0.5)
        else:
            quality_scores.append(1.0)
        
        # Check educational appropriateness
        is_educational = self._check_educational_tone(agent_output)
        if not is_educational:
            warnings.append("Response may not be educational in tone")
            quality_scores.append(0.7)
        else:
            quality_scores.append(1.0)
        
        # Check for negative indicators
        output_lower = agent_output.lower()
        has_negative = any(indicator in output_lower for indicator in self.negative_indicators)
        if has_negative:
            warnings.append("Potentially inappropriate content detected")
            quality_scores.append(0.2)
        
        # Check for LaTeX/formatting (good indicator)
        has_latex = bool(re.search(r'\$.*?\$|\\[a-zA-Z]+', agent_output))
        if has_latex:
            quality_scores.append(1.0)
        else:
            # Not necessarily bad, but suggestion
            suggestions.append("Consider adding LaTeX formatting for mathematical expressions")
            quality_scores.append(0.8)
        
        # Check structure (headings, sections)
        has_structure = bool(re.search(r'#+\s+|##\s+', agent_output))
        if has_structure:
            quality_scores.append(1.0)
        else:
            suggestions.append("Consider adding section headers for better organization")
            quality_scores.append(0.9)
        
        # Calculate average quality score
        quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Overall validation
        is_valid = (
            quality_score >= 0.5 and
            is_mathematically_sound and
            is_educational and
            not has_negative
        )
        
        return OutputGuardrailResult(
            is_valid=is_valid,
            quality_score=quality_score,
            is_mathematically_sound=is_mathematically_sound,
            is_educational=is_educational,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _check_mathematical_soundness(self, output: str) -> bool:
        """Check if output appears mathematically sound."""
        output_lower = output.lower()
        
        # Should contain mathematical terms or symbols
        has_positive = any(indicator in output_lower for indicator in self.positive_indicators)
        has_math_symbols = bool(re.search(r'[\+\-\*/=√∫∑∏∂Δπ∞≤≥≠]', output))
        has_latex = bool(re.search(r'\$.*?\$', output))
        has_numbers = bool(re.search(r'\d+', output))
        
        return has_positive or has_math_symbols or has_latex or has_numbers
    
    def _check_educational_tone(self, output: str) -> bool:
        """Check if output has educational tone."""
        output_lower = output.lower()
        has_educational = any(indicator in output_lower for indicator in self.educational_indicators)
        
        # Should not be too casual or inappropriate
        casual_terms = ['dude', 'bro', 'lol', 'wtf', 'omg']
        is_casual = any(term in output_lower for term in casual_terms)
        
        return has_educational and not is_casual
    
    def check_response_completeness(self, output: str, query: str) -> bool:
        """
        Check if response addresses the query.
        
        Args:
            output: Agent response
            query: Original user query
            
        Returns:
            True if response seems to address the query
        """
        if not query:
            return True  # Can't check without query
        
        # Extract key terms from query
        query_terms = set(re.findall(r'\b\w{4,}\b', query.lower()))
        output_lower = output.lower()
        
        # Check if at least some query terms appear in output
        matching_terms = sum(1 for term in query_terms if term in output_lower)
        coverage = matching_terms / len(query_terms) if query_terms else 1.0
        
        return coverage >= 0.3  # At least 30% of query terms should appear


def create_output_guardrail() -> OutputGuardrail:
    """Factory function to create an output guardrail instance."""
    return OutputGuardrail()

