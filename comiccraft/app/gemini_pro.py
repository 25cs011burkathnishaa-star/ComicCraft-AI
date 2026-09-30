import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured. "
        "Please add GEMINI_API_KEY to your .env file."
    )

client = genai.Client(api_key=api_key)

MODEL_NAME = os.getenv(
    "GEMINI_PRO_MODEL",
    "gemini-3.1-pro-preview"
)


def generate_story(outline: list) -> str:
    """
    Generate a detailed comic story with narration and dialogue
    from the 5-panel comic outline.
    """

    formatted_outline = "\n".join(
        [
            f"Panel {i + 1}: "
            f"{item.get('title', '')} - "
            f"{item.get('scene_description', '')}"
            for i, item in enumerate(outline)
        ]
    )

    prompt = f"""
You are a professional comic book writer.

Create a fun, engaging comic story based on the following
5-panel outline.

PANEL OUTLINE:
{formatted_outline}

REQUIREMENTS:
- Write exactly 5 panels.
- Each section must begin with "Panel 1", "Panel 2", etc.
- Include narration for each panel.
- Include character dialogue where appropriate.
- Keep the characters and story consistent between panels.
- Make the story feel like a real comic book.
- Do not add unrelated scenes.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        story = (response.text or "").strip()

        if not story:
            raise ValueError("Gemini returned an empty story.")

        return story

    except Exception as e:
        print("Gemini Pro Story Generation Error:", e)
        return f"Error generating story: {str(e)}"