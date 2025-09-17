"""
Retrieval Engine for Hardware AI Orchestrator
Orchestrates knowledge retrieval from multiple sources for RAG enhancement
"""
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

from .component_db import ComponentDatabase
from .standards_db import StandardsDatabase
from .vector_store import HardwareVectorStore
from .component_models import ComponentSpecification, ComponentCategory
from ..config.domain_definitions import HARDWARE_DOMAINS

logger = logging.getLogger(__name__)

@dataclass
class RetrievalContext:
    """Context information for knowledge retrieval"""
    query: str
    primary_intent: str
    primary_domain: str
    complexity_score: float
    user_expertise: str = "intermediate"
    project_constraints: Optional[Dict[str, Any]] = None

@dataclass
class KnowledgeResult:
    """Consolidated knowledge retrieval result"""
    components: List[Dict[str, Any]]
    standards: List[Dict[str, Any]]
    domain_context: Dict[str, Any]
    retrieval_summary: Dict[str, Any]

class HardwareRetrievalEngine:
    """Orchestrates knowledge retrieval for hardware engineering queries"""
    
    def __init__(self):
        # Initialize knowledge sources
        self.component_db = ComponentDatabase()
        self.standards_db = StandardsDatabase()
        
        # Initialize vector store if available
        try:
            self.vector_store = HardwareVectorStore()
            self.vector_store.populate_from_database(self.component_db)
            self.vector_search_available = True
            logger.info("Vector store initialized and populated")
        except ImportError as e:
            logger.warning(f"Vector store not available: {e}")
            self.vector_store = None
            self.vector_search_available = False
    
    def retrieve_knowledge(self, context: RetrievalContext) -> KnowledgeResult:
        """
        Main retrieval method - orchestrates all knowledge sources
        Returns consolidated knowledge relevant to the query
        """
        logger.info(f"Retrieving knowledge for intent: {context.primary_intent}, "
                   f"domain: {context.primary_domain}")
        
        # Retrieve components
        components = self._retrieve_components(context)
        
        # Retrieve standards and compliance info
        standards = self._retrieve_standards(context)
        
        # Get domain context
        domain_context = self._get_domain_context(context.primary_domain)
        
        # Create retrieval summary
        retrieval_summary = {
            "total_components": len(components),
            "total_standards": len(standards),
            "retrieval_methods": self._get_retrieval_methods_used(context),
            "confidence": self._calculate_retrieval_confidence(components, standards, context)
        }
        
        return KnowledgeResult(
            components=components,
            standards=standards,
            domain_context=domain_context,
            retrieval_summary=retrieval_summary
        )
    
    def _retrieve_components(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Retrieve relevant components using multiple strategies"""
        components = []
        
        # Strategy 1: Semantic search (if available)
        if self.vector_search_available and self.vector_store:
            semantic_results = self._semantic_component_search(context)
            components.extend(semantic_results)
        
        # Strategy 2: Intent-based retrieval
        intent_results = self._intent_based_component_retrieval(context)
        components.extend(intent_results)
        
        # Strategy 3: Domain-specific retrieval
        domain_results = self._domain_specific_component_retrieval(context)
        components.extend(domain_results)
        
        # Deduplicate and rank
        unique_components = self._deduplicate_components(components)
        ranked_components = self._rank_components(unique_components, context)
        
        return ranked_components[:10]  # Limit to top 10 for performance
    
    def _semantic_component_search(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Perform semantic search using vector store"""
        if not self.vector_store:
            return []
        
        # Apply domain-specific filters
        filters = {}
        if context.primary_domain != "general":
            # Map domains to categories where applicable
            domain_to_category = {
                "power_electronics": "power_management",
                "digital_design": "microcontroller",
                "embedded_hardware": "microcontroller"
            }
            if context.primary_domain in domain_to_category:
                filters["category"] = domain_to_category[context.primary_domain]
        
        # Add constraints based on intent
        constraints = self._extract_constraints_from_query(context.query)
        
        if constraints:
            results = self.vector_store.search_with_constraints(
                query=context.query,
                voltage_range=constraints.get("voltage_range"),
                temp_range=constraints.get("temp_range"),
                compliance_required=constraints.get("compliance"),
                n_results=8
            )
        else:
            results = self.vector_store.search_components(
                query=context.query,
                n_results=8,
                filters=filters
            )
        
        # Enhance results with full component data
        enhanced_results = []
        for result in results:
            component = self.component_db.get_component(result["component_id"])
            if component:
                enhanced_results.append({
                    "component": component.dict(),
                    "similarity_score": result["similarity_score"],
                    "retrieval_method": "semantic_search",
                    "relevance_factors": ["semantic_similarity", "domain_match"]
                })
        
        return enhanced_results
    
    def _intent_based_component_retrieval(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Retrieve components based on query intent"""
        results = []
        
        if context.primary_intent == "component_selection":
            # For component selection, focus on popular/recommended components
            categories = self._get_relevant_categories_for_query(context.query)
            for category in categories:
                components = self.component_db.search_by_category(category)
                for comp in components[:3]:  # Top 3 per category
                    results.append({
                        "component": comp.dict(),
                        "similarity_score": 0.7,  # Default score for intent-based
                        "retrieval_method": "intent_based",
                        "relevance_factors": ["category_match", "intent_alignment"]
                    })
        
        elif context.primary_intent == "compliance_checking":
            # Focus on components with relevant compliance standards
            compliance_filters = self._extract_compliance_requirements(context.query)
            if compliance_filters:
                filtered_components = self.component_db.filter_components(
                    compliance=compliance_filters
                )
                for comp in filtered_components[:5]:
                    results.append({
                        "component": comp.dict(),
                        "similarity_score": 0.8,
                        "retrieval_method": "compliance_based",
                        "relevance_factors": ["compliance_match", "standards_alignment"]
                    })
        
        return results
    
    def _domain_specific_component_retrieval(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Retrieve components specific to hardware domain"""
        results = []
        
        if context.primary_domain == "automotive":
            # Focus on AEC-Q100 qualified components
            automotive_components = self.component_db.filter_components(
                compliance=["AEC-Q100"]
            )
            for comp in automotive_components[:4]:
                results.append({
                    "component": comp.dict(),
                    "similarity_score": 0.75,
                    "retrieval_method": "domain_specific",
                    "relevance_factors": ["automotive_qualified", "domain_expertise"]
                })
        
        elif context.primary_domain == "medical":
            # Focus on medical-grade components
            medical_components = self.component_db.filter_components(
                compliance=["IEC 60601"]
            )
            for comp in medical_components[:4]:
                results.append({
                    "component": comp.dict(),
                    "similarity_score": 0.75,
                    "retrieval_method": "domain_specific",
                    "relevance_factors": ["medical_qualified", "safety_compliance"]
                })
        
        return results
    
    def _retrieve_standards(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Retrieve relevant compliance standards and requirements"""
        standards = []
        
        # Get standards for the specific domain
        domain_standards = self.standards_db.get_standards_by_domain(context.primary_domain)
        
        for standard in domain_standards:
            standards.append({
                "standard": standard.dict(),
                "relevance_score": 0.9,
                "retrieval_method": "domain_based",
                "applicable_to": context.primary_domain
            })
        
        # Search for standards mentioned in query
        if any(keyword in context.query.lower() for keyword in ["aec-q100", "iso 26262", "iec 60601"]):
            query_standards = self.standards_db.search_requirements(context.query)
            for req in query_standards[:3]:
                # Find the parent standard for this requirement
                for std_id, standard in self.standards_db.standards.items():
                    if req in standard.requirements:
                        standards.append({
                            "standard": standard.dict(),
                            "specific_requirement": req.dict(),
                            "relevance_score": 0.95,
                            "retrieval_method": "query_based"
                        })
                        break
        
        return standards
    
    def _get_domain_context(self, domain: str) -> Dict[str, Any]:
        """Get contextual information about the hardware domain"""
        domain_info = HARDWARE_DOMAINS.get(domain, {})
        
        return {
            "domain": domain,
            "scope": domain_info.get("scope", []),
            "expertise_areas": domain_info.get("expertise_areas", []),
            "complexity_weight": domain_info.get("complexity_weight", 1.0),
            "typical_components": self._get_typical_components_for_domain(domain),
            "key_considerations": self._get_domain_considerations(domain)
        }
    
    def _extract_constraints_from_query(self, query: str) -> Dict[str, Any]:
        """Extract technical constraints from query text"""
        constraints = {}
        query_lower = query.lower()
        
        # Voltage constraints
        voltage_patterns = ["voltage", "volt", "v", "supply"]
        if any(pattern in query_lower for pattern in voltage_patterns):
            # Simple pattern matching for voltage ranges
            import re
            voltage_match = re.search(r'(\d+(?:\.\d+)?)\s*v?\s*to\s*(\d+(?:\.\d+)?)\s*v?', query_lower)
            if voltage_match:
                constraints["voltage_range"] = (float(voltage_match.group(1)), float(voltage_match.group(2)))
        
        # Temperature constraints
        if "temperature" in query_lower or "°c" in query_lower:
            temp_match = re.search(r'(-?\d+(?:\.\d+)?)\s*°?c?\s*to\s*(-?\d+(?:\.\d+)?)\s*°?c?', query_lower)
            if temp_match:
                constraints["temp_range"] = (float(temp_match.group(1)), float(temp_match.group(2)))
        
        # Compliance constraints
        compliance_keywords = ["aec-q100", "iso 26262", "iec 60601", "automotive", "medical"]
        found_compliance = [kw.upper().replace(" ", "_") for kw in compliance_keywords if kw in query_lower]
        if found_compliance:
            constraints["compliance"] = found_compliance
        
        return constraints
    
    def _get_relevant_categories_for_query(self, query: str) -> List[ComponentCategory]:
        """Determine relevant component categories from query"""
        query_lower = query.lower()
        categories = []
        
        category_keywords = {
            ComponentCategory.MICROCONTROLLER: ["microcontroller", "mcu", "processor", "cortex", "arm"],
            ComponentCategory.POWER_MANAGEMENT: ["power", "voltage", "regulator", "buck", "boost", "ldo"],
            ComponentCategory.SENSORS: ["sensor", "temperature", "pressure", "accelerometer"],
            ComponentCategory.ANALOG_IC: ["op-amp", "amplifier", "comparator", "reference"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                categories.append(category)
        
        return categories or [ComponentCategory.MICROCONTROLLER]  # Default fallback
    
    def _extract_compliance_requirements(self, query: str) -> List[str]:
        """Extract compliance requirements from query"""
        from .component_models import ComplianceStandard  # Import here instead of top

        query_lower = query.lower()
        compliance = []
        
        if "aec-q100" in query_lower or "automotive" in query_lower:
            compliance.append(ComplianceStandard.AEC_Q100.value)
        if "iso 26262" in query_lower or "functional safety" in query_lower:
            compliance.append(ComplianceStandard.ISO_26262.value) 
        if "iec 60601" in query_lower or "medical" in query_lower:
            compliance.append(ComplianceStandard.IEC_60601.value)
        
        return compliance
    
    def _deduplicate_components(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate components based on component_id"""
        seen_ids = set()
        unique_components = []
        
        for comp_data in components:
            comp_id = comp_data["component"]["component_id"]
            if comp_id not in seen_ids:
                seen_ids.add(comp_id)
                unique_components.append(comp_data)
        
        return unique_components
    
    def _rank_components(self, components: List[Dict[str, Any]], context: RetrievalContext) -> List[Dict[str, Any]]:
        """Rank components based on relevance to query context"""
        # Simple ranking based on similarity scores and relevance factors
        def ranking_key(comp_data):
            base_score = comp_data.get("similarity_score", 0.5)
            
            # Boost based on retrieval method
            method_boost = {
                "semantic_search": 0.1,
                "compliance_based": 0.08,
                "domain_specific": 0.06,
                "intent_based": 0.04
            }
            boost = method_boost.get(comp_data.get("retrieval_method", ""), 0.0)
            
            # Boost for domain alignment
            if context.primary_domain == "automotive" and "automotive" in str(comp_data.get("relevance_factors", [])):
                boost += 0.05
            
            return base_score + boost
        
        return sorted(components, key=ranking_key, reverse=True)
    
    def _get_typical_components_for_domain(self, domain: str) -> List[str]:
        """Get typical component types for a domain"""
        domain_components = {
            "automotive": ["Buck controllers", "CAN transceivers", "Automotive MCUs", "Power MOSFETs"],
            "medical": ["Medical-grade power supplies", "Isolation amplifiers", "Low-leakage regulators"],
            "power_electronics": ["Switching controllers", "Power MOSFETs", "Gate drivers", "Current sensors"],
            "analog_rf": ["Op-amps", "Filters", "VCOs", "Mixers"],
            "digital_design": ["Microcontrollers", "FPGAs", "Logic gates", "Clock generators"]
        }
        return domain_components.get(domain, ["General purpose components"])
    
    def _get_domain_considerations(self, domain: str) -> List[str]:
        """Get key engineering considerations for a domain"""
        considerations = {
            "automotive": ["Temperature cycling", "Vibration resistance", "EMC compliance", "Long-term reliability"],
            "medical": ["Patient safety", "Leakage current limits", "Biocompatibility", "Sterilization compatibility"],
            "power_electronics": ["Efficiency optimization", "Thermal management", "EMI suppression", "Transient response"],
            "analog_rf": ["Noise performance", "Frequency response", "Distortion", "Matching requirements"]
        }
        return considerations.get(domain, ["General reliability", "Cost optimization", "Availability"])
    
    def _get_retrieval_methods_used(self, context: RetrievalContext) -> List[str]:
        """Get list of retrieval methods used for this query"""
        methods = ["intent_based", "domain_specific"]
        if self.vector_search_available:
            methods.append("semantic_search")
        if context.primary_intent == "compliance_checking":
            methods.append("compliance_based")
        return methods
    
    def _calculate_retrieval_confidence(self, components: List[Dict], standards: List[Dict], context: RetrievalContext) -> float:
        """Calculate confidence in retrieval results"""
        base_confidence = 0.6
        
        # Boost for having relevant components
        if components:
            component_boost = min(len(components) * 0.05, 0.3)
            base_confidence += component_boost
        
        # Boost for having relevant standards
        if standards:
            standards_boost = min(len(standards) * 0.08, 0.2)
            base_confidence += standards_boost
        
        # Boost for vector search availability
        if self.vector_search_available:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
