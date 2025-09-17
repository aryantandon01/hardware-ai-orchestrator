"""
Hardware Complexity Scoring Algorithm
Evaluates queries on 6 technical complexity factors, produces 0.0-1.0 scores
"""
from typing import Dict, List
import re
from ..config.complexity_weights import COMPLEXITY_FACTORS

class HardwareComplexityScorer:
    def __init__(self):
        self.factors = COMPLEXITY_FACTORS
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for each complexity factor"""
        self.patterns = {}
        
        # Technical keywords density pattern
        tech_keywords = self.factors["technical_keywords_density"]["high_complexity_keywords"]
        self.patterns["technical"] = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in tech_keywords) + r')\b', 
            re.IGNORECASE
        )
        
        # Design constraints pattern
        constraint_keywords = self.factors["design_constraint_count"]["constraint_keywords"]
        self.patterns["constraints"] = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in constraint_keywords) + r')\b',
            re.IGNORECASE
        )
        
        # Calculation complexity pattern
        calc_keywords = self.factors["calculation_complexity"]["calculation_keywords"]
        self.patterns["calculations"] = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in calc_keywords) + r')\b',
            re.IGNORECASE
        )
        
        # Standards involvement pattern
        standards_keywords = self.factors["standards_involvement"]["standards_keywords"]
        self.patterns["standards"] = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in standards_keywords) + r')\b',
            re.IGNORECASE
        )
        
        # Multi-domain integration pattern
        integration_keywords = self.factors["multi_domain_integration"]["integration_keywords"]
        self.patterns["integration"] = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in integration_keywords) + r')\b',
            re.IGNORECASE
        )
    
    def calculate_complexity(self, query: str, domain: str = None, intent: str = None) -> Dict[str, float]:
        """
        Calculate complexity score based on 6 factors
        Returns detailed breakdown and final score
        """
        query_lower = query.lower()
        factor_scores = {}
        
        # 1. Technical Keywords Density (25% weight)
        tech_matches = len(self.patterns["technical"].findall(query))
        tech_density = min(tech_matches * 0.2, 1.0)
        factor_scores["technical_keywords_density"] = tech_density
        
        # 2. Design Constraint Count (20% weight)
        constraint_matches = len(self.patterns["constraints"].findall(query))
        constraint_score = min(constraint_matches * 0.25, 1.0)
        factor_scores["design_constraint_count"] = constraint_score
        
        # 3. Domain Specificity (20% weight)
        high_spec_domains = self.factors["domain_specificity"]["high_specificity_domains"]
        if domain in high_spec_domains:
            domain_score = 0.8
        elif domain:
            domain_score = 0.5
        else:
            domain_score = 0.3
        factor_scores["domain_specificity"] = domain_score
        
        # 4. Calculation Complexity (15% weight)
        calc_matches = len(self.patterns["calculations"].findall(query))
        calc_score = min(calc_matches * 0.3, 1.0)
        factor_scores["calculation_complexity"] = calc_score
        
        # 5. Standards Involvement (15% weight)
        standards_matches = len(self.patterns["standards"].findall(query))
        standards_score = min(standards_matches * 0.4, 1.0)
        factor_scores["standards_involvement"] = standards_score
        
        # 6. Multi-Domain Integration (5% weight)
        integration_matches = len(self.patterns["integration"].findall(query))
        integration_score = min(integration_matches * 0.5, 1.0)
        factor_scores["multi_domain_integration"] = integration_score
        
        # Calculate weighted final score
        final_score = 0.0
        for factor, score in factor_scores.items():
            weight = self.factors[factor]["weight"]
            final_score += score * weight
        
        # Add query length complexity (longer queries often more complex)
        word_count = len(query.split())
        length_bonus = min(word_count / 50, 0.1)  # Max 0.1 bonus
        final_score += length_bonus
        
        # Ensure score is between 0.0 and 1.0
        final_score = max(0.0, min(final_score, 1.0))
        
        return {
            "factor_scores": factor_scores,
            "final_score": final_score,
            "word_count": word_count,
            "length_bonus": length_bonus
        }
