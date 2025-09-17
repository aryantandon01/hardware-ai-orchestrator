"""
Hardware Query Intent Classification
Recognizes 12 distinct hardware engineering intent categories
"""
from typing import Dict, List, Tuple
import re
from ..config.intent_categories import INTENT_CATEGORIES

class HardwareIntentClassifier:
    def __init__(self):
        self.intent_categories = INTENT_CATEGORIES
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching"""
        self.patterns = {}
        for intent, config in self.intent_categories.items():
            # Create regex pattern from keywords
            keywords = config["keywords"]
            pattern = r'\b(' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
            self.patterns[intent] = re.compile(pattern, re.IGNORECASE)
    
    def classify_intent(self, query: str) -> Dict[str, float]:
        """
        Classify query intent across all 12 categories
        Returns confidence scores for each intent
        """
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, pattern in self.patterns.items():
            # Count keyword matches
            matches = pattern.findall(query)
            keyword_count = len(matches)
            
            # Calculate base score from keyword density
            base_score = min(keyword_count * 0.2, 1.0)
            
            # Boost score for complexity indicators
            complexity_indicators = self.intent_categories[intent]["complexity_indicators"]
            for indicator in complexity_indicators:
                if indicator in query_lower:
                    base_score += 0.1
            
            # Apply base complexity modifier
            base_complexity = self.intent_categories[intent]["base_complexity"]
            final_score = base_score * base_complexity
            
            intent_scores[intent] = min(final_score, 1.0)
        
        return intent_scores
    
    def get_primary_intent(self, query: str) -> Tuple[str, float]:
        """Get the highest-confidence intent classification"""
        intent_scores = self.classify_intent(query)
        
        if not intent_scores:
            return "educational_content", 0.3  # Default fallback
        
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        return primary_intent
    
    def get_intent_description(self, intent: str) -> str:
        """Get human-readable description of an intent category"""
        return self.intent_categories.get(intent, {}).get("description", "Unknown intent")
