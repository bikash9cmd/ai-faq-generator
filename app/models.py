from typing import List, Literal

from pydantic import BaseModel, Field


class FAQ(BaseModel):
    question: str
    answer: str


class FAQResponse(BaseModel):
    faqs: List[FAQ]


class FAQRequest(BaseModel):
    source_type: Literal["topic", "text", "url"] = Field(
        ...,
        description="Input type: topic, text, or url"
    )

    source: str = Field(
    ...,
    min_length=1,
    max_length=50000,
    description="Topic, pasted content, or webpage URL"
)

    faq_count: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of FAQs to generate"
    )

    language: str = Field(
        default="English",
        min_length=1,
        description="Output language"
    )

    tone: str = Field(
        default="Professional",
        min_length=1,
        description="Answer tone"
    )
