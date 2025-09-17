"""
FastAPI endpoints for Hardware AI Orchestrator
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import time
import logging
from typing import Dict, Any

from .models import (
    HardwareQueryRequest, HardwareQueryResponse, 
    HealthResponse, ErrorResponse
)
from ..classification.query_analyzer import HardwareQueryAnalyzer
from ..config.settings import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["Hardware Analysis"])

# Initialize query analyzer (singleton)
query_analyzer = None

def get_query_analyzer() -> HardwareQueryAnalyzer:
    """Dependency to get query analyzer instance"""
    global query_analyzer
    if query_analyzer is None:
        query_analyzer = HardwareQueryAnalyzer()
    return query_analyzer

@router.post("/analyze", 
             response_model=HardwareQueryResponse,
             summary="Analyze Hardware Engineering Query",
             description="Analyze hardware engineering query for intent, domain, complexity and optimal AI model routing")
async def analyze_hardware_query(
    request: HardwareQueryRequest,
    analyzer: HardwareQueryAnalyzer = Depends(get_query_analyzer)
) -> HardwareQueryResponse:
    """
    Analyze hardware engineering query and determine optimal AI model routing
    
    - **query**: Hardware engineering question or request
    - **user_expertise**: User's technical expertise level
    - **project_phase**: Optional project development phase
    - **preferred_domain**: Optional preferred hardware domain
    
    Returns complete analysis including intent classification, domain detection,
    complexity scoring, and AI model routing decision.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing query from {request.user_expertise} user: {request.query[:100]}...")
        
        # Perform complete analysis
        analysis = analyzer.analyze_query(request.query)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Create response
        response = HardwareQueryResponse(
            **analysis,
            processing_time_ms=round(processing_time, 2)
        )
        
        logger.info(f"Analysis completed in {processing_time:.2f}ms - "
                   f"Model: {analysis['routing']['selected_model']}")
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed for query: {request.query[:50]}... Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query analysis failed: {str(e)}"
        )

@router.get("/health", 
           response_model=HealthResponse,
           summary="Health Check",
           description="Check system health and component status")
async def health_check() -> HealthResponse:
    """System health check endpoint"""
    try:
        # Test analyzer initialization
        analyzer = get_query_analyzer()
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            components={
                "intent_classifier": "operational",
                "domain_detector": "operational", 
                "complexity_scorer": "operational",
                "model_router": "operational"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"System unhealthy: {str(e)}"
        )

@router.get("/models",
           summary="Available AI Models",
           description="List available AI models and their routing criteria")
async def get_available_models() -> Dict[str, Any]:
    """Get information about available AI models and routing criteria"""
    from ..routing.routing_rules import ModelRoutingRules
    
    models = ModelRoutingRules.get_all_models()
    
    return {
        "available_models": list(models.keys()),
        "model_details": models,
        "routing_info": {
            "complexity_thresholds": {
                "claude_sonnet_4": "≥ 0.8",
                "grok_2": "0.6 - 0.8", 
                "gpt_4o": "0.4 - 0.7",
                "gpt_4o_mini": "< 0.4"
            }
        }
    }

@router.get("/categories",
           summary="Hardware Categories",
           description="List all supported intent categories and hardware domains")
async def get_categories() -> Dict[str, Any]:
    """Get supported hardware categories and domains"""
    from ..config.intent_categories import INTENT_CATEGORIES
    from ..config.domain_definitions import HARDWARE_DOMAINS
    
    return {
        "intent_categories": {
            name: {
                "description": config["description"],
                "base_complexity": config["base_complexity"]
            }
            for name, config in INTENT_CATEGORIES.items()
        },
        "hardware_domains": {
            name: {
                "scope": config["scope"],
                "expertise_areas": config["expertise_areas"]
            }
            for name, config in HARDWARE_DOMAINS.items()
        }
    }

@router.post("/analyze-with-knowledge", 
             response_model=Dict[str, Any],
             summary="Analyze Query with Knowledge Retrieval",
             description="Complete analysis with RAG-enhanced knowledge retrieval")
async def analyze_with_knowledge(
    request: HardwareQueryRequest,
    analyzer: HardwareQueryAnalyzer = Depends(get_query_analyzer)
) -> Dict[str, Any]:
    """
    Perform complete analysis including knowledge retrieval for RAG enhancement
    """
    start_time = time.time()
    
    try:
        # Step 1: Perform Day 1 analysis (intent, domain, complexity, routing)
        analysis = analyzer.analyze_query(request.query)
        
        # Step 2: Knowledge retrieval for RAG
        from ..knowledge.retrieval_engine import HardwareRetrievalEngine, RetrievalContext
        
        retrieval_engine = HardwareRetrievalEngine()
        
        retrieval_context = RetrievalContext(
            query=request.query,
            primary_intent=analysis["classification"]["primary_intent"]["intent"],
            primary_domain=analysis["classification"]["primary_domain"]["domain"],
            complexity_score=analysis["complexity"]["final_score"],
            user_expertise=request.user_expertise.value
        )
        
        knowledge = retrieval_engine.retrieve_knowledge(retrieval_context)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Combine Day 1 analysis with Day 2 knowledge
        enhanced_response = {
            **analysis,  # Include all Day 1 analysis
            "knowledge": {
                "components": knowledge.components,
                "standards": knowledge.standards,
                "domain_context": knowledge.domain_context,
                "retrieval_summary": knowledge.retrieval_summary
            },
            "processing_time_ms": round(processing_time, 2),
            "capabilities": ["intent_classification", "domain_detection", "complexity_scoring", "model_routing", "knowledge_retrieval"]
        }
        
        logger.info(f"Enhanced analysis completed in {processing_time:.2f}ms - "
                   f"Retrieved {len(knowledge.components)} components, {len(knowledge.standards)} standards")
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Enhanced analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced analysis failed: {str(e)}")
