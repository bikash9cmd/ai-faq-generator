import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.models import FAQRequest, FAQResponse
from app.faq_generator import generate_faqs, regenerate_faq_by_index
from app.content_extractor import extract_content_from_url

from app.database import init_db, save_faq_history, get_faq_history

class RegenerateFAQRequest(BaseModel):
    result: FAQResponse
    index: int
    content: str
    language: str = "English"
    tone: str = "Professional"


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("ai-faq-generator")


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="AI FAQ Generator API",
    description="Backend API for the AI FAQ Generator",
    version="1.0.0"
)
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
	"http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


# --------------------------------------------------
# Global exception handler

# --------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred."
        },
    )


# --------------------------------------------------# Root endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "AI FAQ Generator API is running!"
    }


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.get("/history")
def get_history():
    try:
        return {
            "history": get_faq_history()
        }
    except Exception:
        logger.exception("Failed to fetch FAQ history")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch FAQ history."
        )
# --------------------------------------------------
# Generate FAQs
# --------------------------------------------------

@app.post("/regenerate-faq", response_model=FAQResponse)
@limiter.limit("10/minute")
def regenerate_faq_endpoint(
    request: Request,
    data: RegenerateFAQRequest
):
    try:
        logger.info(
            "FAQ regeneration requested | index=%s | language=%s",
            data.index,
            data.language
        )

        if not data.content or not data.content.strip():
            raise HTTPException(
                status_code=400,
                detail="Content cannot be empty."
            )

        result = regenerate_faq_by_index(
            result=data.result,
            index=data.index,
            content=data.content,
            language=data.language,
            tone=data.tone
        )

        logger.info(
            "FAQ regeneration completed successfully | index=%s",
            data.index
        )

        return result

    except ValueError as exc:
        logger.warning(
            "FAQ regeneration validation error: %s",
            exc
        )
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception:
        logger.exception(
            "Unexpected error during FAQ regeneration"
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to regenerate FAQ. Please try again later."
        )

# --------------------------------------------------
# Regenerate FAQ
# --------------------------------------------------
# ----------------------------------------
# Generate FAQs
# ----------------------------------------

@app.post("/generate-faq", response_model=FAQResponse)
@limiter.limit("10/minute")
def generate_faq_endpoint(
    request: Request,
    faq_request: FAQRequest
):
    try:
        logger.info(
            "FAQ generation requested | source_type=%s | faq_count=%s | language=%s",
            faq_request.source_type,
            faq_request.faq_count,
            faq_request.language
        )

        if not faq_request.source or not faq_request.source.strip():
            raise HTTPException(
                status_code=400,
                detail="Source content cannot be empty."
            )

        if faq_request.source_type not in ("topic", "text", "url"):
            raise HTTPException(
                status_code=400,
                detail="source_type must be 'topic', 'text', or 'url'."
            )

        if faq_request.source_type == "url":
            content = extract_content_from_url(faq_request.source)
        else:
            content = faq_request.source

        result = generate_faqs(
            content,
            faq_request.faq_count,
            faq_request.language,
            faq_request.tone
        )



        save_faq_history(
            source_type=faq_request.source_type,
            source=faq_request.source,
            faq_count=faq_request.faq_count,
            language=faq_request.language,
            tone=faq_request.tone,
            faqs=[faq.model_dump() for faq in result.faqs]
        )

        logger.info(
            "FAQ generation completed successfully | faq_count=%s",
            faq_request.faq_count
        )

        return result

    except ValueError as exc:
        logger.warning(
            "FAQ generation validation error: %s",
            exc
        )
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Unexpected error during FAQ generation"
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate FAQs. Please try again later."
        )
