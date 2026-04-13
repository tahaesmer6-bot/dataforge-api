from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field
from app.middleware.rate_limiter import limiter
from app.services.text_service import analyze_text

router = APIRouter()


class TextRequest(BaseModel):
    text: str = Field(
        ...,
        description="Text to analyze",
        min_length=1,
        max_length=100000,
        example="The quick brown fox jumps over the lazy dog. This is a sample text for analysis.",
    )


@router.post("", summary="Analyze text content")
@limiter.limit("30/minute")
async def analyze(request: Request, body: TextRequest):
    """
    Comprehensive text analysis:
    - Character, word, sentence, paragraph counts
    - Reading time estimation
    - Speaking time estimation
    - Readability scores (Flesch Reading Ease, Flesch-Kincaid)
    - Vocabulary richness
    - Word frequency analysis
    - Basic sentiment analysis
    - Character type breakdown
    """
    return analyze_text(body.text)


@router.post("/word-count", summary="Quick word count")
@limiter.limit("60/minute")
async def word_count(request: Request, body: TextRequest):
    """Quick word count without full analysis."""
    import re
    words = re.findall(r'\b\w+\b', body.text)
    return {
        "word_count": len(words),
        "character_count": len(body.text),
        "character_count_no_spaces": len(body.text.replace(" ", "")),
    }


@router.post("/reading-time", summary="Estimate reading time")
@limiter.limit("60/minute")
async def reading_time(request: Request, body: TextRequest):
    """Estimate reading and speaking time for text."""
    import re
    words = len(re.findall(r'\b\w+\b', body.text))
    read_min = round(words / 200, 2)
    speak_min = round(words / 130, 2)

    return {
        "word_count": words,
        "reading_time": {
            "minutes": read_min,
            "seconds": round(read_min * 60),
        },
        "speaking_time": {
            "minutes": speak_min,
            "seconds": round(speak_min * 60),
        },
    }
