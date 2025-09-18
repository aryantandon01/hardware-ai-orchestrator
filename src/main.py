"""
Main FastAPI Application - Hardware AI Orchestrator
Enhanced with Multi-Modal Schematic Processing Capabilities
"""
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
import uvicorn
import os


from .api.endpoints import router
from .config.settings import settings


# Import schematic router with graceful fallback
try:
    from .vision.schematic_processor.integration_handler import schematic_router, EnhancedSchematicProcessor
    SCHEMATIC_AVAILABLE = True
    logging.info("✅ Schematic processing module loaded successfully")
except ImportError as e:
    schematic_router = None
    EnhancedSchematicProcessor = None
    SCHEMATIC_AVAILABLE = False
    logging.warning(f"⚠️ Schematic processing not available: {e}")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create FastAPI app with enhanced metadata
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    🚀 AI Orchestration System for Hardware Engineering
    
    **Core Capabilities:**
    - Intelligent AI model routing based on query complexity
    - RAG-enhanced knowledge retrieval with vector search
    - Multi-domain expertise (automotive, medical, IoT, digital design)
    - Advanced query analysis with intent classification
    
    **Advanced Features:**
    - Multi-modal schematic understanding and analysis
    - Component detection and recommendation
    - Design compliance checking
    - Supply chain intelligence (planned)
    
    **API Endpoints:**
    - `/api/v1/analyze` - Natural language hardware queries
    - `/api/v1/schematic/analyze` - Schematic image analysis
    - `/docs` - Interactive API documentation
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Hardware AI Orchestrator",
        "url": "https://github.com/your-repo/hardware-ai-orchestrator"
    }
)


# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Request-ID"]
)


# Request timing and ID middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time and request ID to response headers"""
    import uuid
    
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]
    
    # Add request ID to request state for logging
    request.state.request_id = request_id
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    response.headers["X-Request-ID"] = request_id
    
    return response


# Include existing API router
app.include_router(router)


# ✅ CRITICAL FIX: Include schematic router WITHOUT additional prefix
# The schematic_router already has prefix="/api/v1/schematic" defined internally
if SCHEMATIC_AVAILABLE and schematic_router:
    app.include_router(
        schematic_router,  # No prefix here - router already defines its own
        tags=["schematic-processing"]
    )
    logger.info("🔍 Schematic processing endpoints enabled at /api/v1/schematic/*")
else:
    logger.warning("⚠️ Schematic processing endpoints not available")


# Enhanced root endpoint
@app.get("/", 
         summary="Hardware AI Orchestrator Root", 
         description="System information and available endpoints")
async def root():
    """Enhanced root endpoint with comprehensive system information"""
    endpoints = {
        "analyze": {
            "url": "/api/v1/analyze",
            "method": "POST",
            "description": "Natural language hardware engineering queries with AI routing"
        },
        "health": {
            "url": "/api/v1/health", 
            "method": "GET",
            "description": "System health check"
        }
    }
    
    # Add schematic endpoints if available
    if SCHEMATIC_AVAILABLE:
        endpoints["schematic_analyze"] = {
            "url": "/api/v1/schematic/analyze",
            "method": "POST", 
            "description": "Multi-modal schematic image analysis and component detection"
        }
        endpoints["schematic_health"] = {
            "url": "/api/v1/schematic/health",
            "method": "GET",
            "description": "Schematic processing service health check"
        }
        endpoints["schematic_capabilities"] = {
            "url": "/api/v1/schematic/capabilities",
            "method": "GET",
            "description": "Schematic processing capabilities and features"
        }
    
    return {
        "message": "🚀 Hardware AI Orchestrator",
        "version": settings.app_version,
        "status": "operational",
        "capabilities": {
            "ai_routing": "✅ Enabled",
            "knowledge_retrieval": "✅ Enabled", 
            "vector_search": "✅ Enabled",
            "schematic_processing": "✅ Enabled" if SCHEMATIC_AVAILABLE else "⚠️ Unavailable"
        },
        "endpoints": endpoints,
        "documentation": {
            "interactive_docs": "/docs",
            "redoc": "/redoc"
        }
    }


# Enhanced system status endpoint
@app.get("/api/v1/status", 
         summary="System Status", 
         description="Detailed system status and feature availability")
async def system_status():
    """Comprehensive system status endpoint"""
    try:
        # Test core components
        from .analysis.query_analyzer import HardwareQueryAnalyzer
        from .routing.model_router import ModelRouter
        
        core_status = "healthy"
        query_analyzer = HardwareQueryAnalyzer()
        model_router = ModelRouter()
        
    except Exception as e:
        core_status = "degraded"
        logger.error(f"Core component check failed: {e}")
    
    # Test knowledge retrieval
    try:
        from .knowledge.retrieval_engine import HardwareRetrievalEngine
        retrieval_engine = HardwareRetrievalEngine()
        knowledge_status = "healthy"
    except Exception as e:
        knowledge_status = "degraded"
        logger.error(f"Knowledge retrieval check failed: {e}")
    
    # Test schematic processing
    schematic_status = "healthy" if SCHEMATIC_AVAILABLE else "unavailable"
    
    return {
        "timestamp": time.time(),
        "system": {
            "status": core_status,
            "uptime": "operational",
            "version": settings.app_version
        },
        "components": {
            "core_ai_pipeline": core_status,
            "knowledge_retrieval": knowledge_status,
            "schematic_processing": schematic_status,
            "vector_database": "healthy" if knowledge_status == "healthy" else "unknown"
        },
        "features": {
            "intelligent_routing": True,
            "rag_enhancement": True,
            "multi_modal_processing": SCHEMATIC_AVAILABLE,
            "predictive_intelligence": False,  # Future feature
            "collaborative_features": False   # Future feature
        }
    }


# Enhanced global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Enhanced global exception handler with detailed logging"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(
        f"🚨 Unhandled exception [Request ID: {request_id}] "
        f"Path: {request.url.path} "
        f"Method: {request.method} "
        f"Error: {str(exc)}"
    )
    
    # Don't expose internal errors in production
    error_detail = str(exc) if settings.debug else "An internal error occurred"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": error_detail,
            "request_id": request_id,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


# HTTP exception handler for better error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Enhanced HTTP exception handler"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("🚀 Hardware AI Orchestrator starting up...")
    logger.info(f"📊 Version: {settings.app_version}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    logger.info(f"🔍 Schematic processing: {'Enabled' if SCHEMATIC_AVAILABLE else 'Disabled'}")
    
    # Initialize components
    try:
        from .knowledge.retrieval_engine import HardwareRetrievalEngine
        retrieval_engine = HardwareRetrievalEngine()
        logger.info("✅ Knowledge retrieval engine initialized")
    except Exception as e:
        logger.warning(f"⚠️ Knowledge retrieval initialization failed: {e}")
    
    # Log available routes for debugging
    logger.info("🔗 Available API routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            logger.info(f"  {route.methods} {route.path}")
    
    logger.info("✅ Hardware AI Orchestrator startup complete")


# Shutdown event  
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("🛑 Hardware AI Orchestrator shutting down...")
    # Add cleanup tasks here if needed
    logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    # Enhanced development server configuration
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    
    logger.info(f"🌐 Starting server at http://{host}:{port}")
    logger.info(f"📚 API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        access_log=True,
        reload_dirs=["src"] if settings.debug else None
    )
