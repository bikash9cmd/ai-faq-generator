from google import genai

from app.models import FAQ, FAQResponse
from app.config import settings
client = genai.Client(api_key=settings.gemini_api_key)


def generate_faqs(
    content: str,
    faq_count: int = 5,
    language: str = "English",
    tone: str = "Professional"
) -> FAQResponse:

    prompt = f"""
You are an AI FAQ generator.

Based ONLY on the content provided below, generate exactly {faq_count}
frequently asked questions and concise answers.

Requirements:
- Language: {language}
- Tone: {tone}
- Questions must be directly related to the provided content.
- Answers must be concise and useful.
- Do not invent information that is not supported by the content.
- Avoid duplicate questions.

CONTENT:
{content}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": FAQResponse,
        },
    )

    return FAQResponse.model_validate_json(response.text)


def regenerate_faq(
    content: str,
    current_question: str,
    current_answer: str,
    language: str = "English",
    tone: str = "Professional"
) -> FAQ:

    prompt = f"""
You are an AI FAQ generator.

Regenerate the FAQ below using ONLY the information
available in the source content.

SOURCE CONTENT:
{content}

CURRENT FAQ:
Question: {current_question}
Answer: {current_answer}

Requirements:
- Create a different but relevant question.
- Create a concise answer.
- The answer must be supported by the source.
- Do not invent information.
- Do not repeat the original question.
- Write in {language}.
- Use a {tone} tone.
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": FAQ,
        },
    )

    return FAQ.model_validate_json(response.text)


def regenerate_faq_by_index(
    result: FAQResponse,
    index: int,
    content: str,
    language: str = "English",
    tone: str = "Professional"
) -> FAQResponse:

    if index < 0 or index >= len(result.faqs):
        raise ValueError("FAQ index out of range.")

    current_faq = result.faqs[index]

    new_faq = regenerate_faq(
        content=content,
        current_question=current_faq.question,
        current_answer=current_faq.answer,
        language=language,
        tone=tone,
    )

    result.faqs[index] = new_faq

    return result
