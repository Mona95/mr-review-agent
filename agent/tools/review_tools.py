import os
import json
from pyexpat.errors import messages

from groq import Groq
from dotenv import load_dotenv
from agent.prompts.review_prompt import REVIEW_SYSTEM_PROMPT, REVIEW_USER_PROMPT

load_dotenv()

def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")
    return Groq(api_key=api_key)

def review_code(diff: str, context: dict) -> dict:
    """
       Send PR diff + context to Groq for AI review.
       Returns structured JSON feedback.
    """

    client = get_groq_client()

    # Build the user prompt with real data
    user_prompt = REVIEW_USER_PROMPT.format(
        title=context.get("title", "No title"),
        description=context.get("description", "No description"),
        author=context.get("author", "Unknown"),
        base_branch=context.get("base_branch", ""),
        changed_files=context.get("changed_files, 0"),
        additions=context.get("additions", 0),
        deletions=context.get("deletions", 0),
        diff=diff
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=4096,
        temperature=0.1
    )

    raw_text = response.choices[0].message.content.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
        raw_text = raw_text.split("```",1)[0].strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        return {
            "summary": "Review completed but output parsing failed",
            "score": 0,
            "categories": {
                "bugs": [],
                "security": [],
                "performance": [],
                "style": []
            },
            "positives": [],
            "raw_output": raw_text,
            "parse_error": str(e)
        }