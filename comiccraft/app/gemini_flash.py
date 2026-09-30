import os
import json
from google import genai
from google.genai import types
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
    "GEMINI_FLASH_MODEL",
    "gemini-3.6-flash"
)


def generate_outline(user_prompt: str) -> list:
    """
    Generate exactly 5 connected comic panels using Gemini.
    Returns a list containing 5 panel dictionaries.
    """

    prompt = f"""
You are a professional AI comic story planner.

Create a connected 5-panel comic story from this story idea:

STORY:
{user_prompt}

IMPORTANT RULES:
1. Return EXACTLY 5 panels.
2. Return ONLY a valid JSON array.
3. Do NOT use Markdown.
4. Do NOT use ```json or ``` code fences.
5. Do NOT add explanations before or after the JSON.
6. Each panel must contain exactly these fields:
   - "panel": integer from 1 to 5
   - "title": short string
   - "scene_description": detailed scene description
   - "image_prompt": detailed visual prompt for an AI image generator
7. The same main character must remain visually consistent across all 5 panels.
8. The panels must form one connected story.

Required format:

[
  {{
    "panel": 1,
    "title": "Beginning",
    "scene_description": "Description of panel 1",
    "image_prompt": "Visual prompt for panel 1"
  }},
  {{
    "panel": 2,
    "title": "Development",
    "scene_description": "Description of panel 2",
    "image_prompt": "Visual prompt for panel 2"
  }},
  {{
    "panel": 3,
    "title": "Conflict",
    "scene_description": "Description of panel 3",
    "image_prompt": "Visual prompt for panel 3"
  }},
  {{
    "panel": 4,
    "title": "Climax",
    "scene_description": "Description of panel 4",
    "image_prompt": "Visual prompt for panel 4"
  }},
  {{
    "panel": 5,
    "title": "Ending",
    "scene_description": "Description of panel 5",
    "image_prompt": "Visual prompt for panel 5"
  }}
]
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json",
            ),
        )

        output_text = (response.text or "").strip()

        print("\nRAW GEMINI RESPONSE\n")
        print(output_text)

        if not output_text:
            raise ValueError("Gemini returned an empty response.")

        # Remove Markdown code fences if Gemini adds them anyway.
        if output_text.startswith("```"):
            output_text = output_text.replace("```json", "", 1)
            output_text = output_text.replace("```", "")
            output_text = output_text.strip()

        # Find the JSON array if Gemini accidentally adds extra text.
        start = output_text.find("[")
        end = output_text.rfind("]")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "Gemini did not return a valid JSON array."
            )

        json_text = output_text[start:end + 1]

        panel_data = json.loads(json_text)

        if not isinstance(panel_data, list):
            raise ValueError(
                "Gemini response is not a JSON list."
            )

        if len(panel_data) != 5:
            raise ValueError(
                f"Expected exactly 5 panels, but Gemini returned "
                f"{len(panel_data)} panels."
            )

        required_keys = {
            "panel",
            "title",
            "scene_description",
            "image_prompt",
        }

        validated_panels = []

        for index, panel in enumerate(panel_data, start=1):

            if not isinstance(panel, dict):
                raise ValueError(
                    f"Panel {index} is not a JSON object."
                )

            missing_keys = required_keys - set(panel.keys())

            if missing_keys:
                raise ValueError(
                    f"Panel {index} is missing fields: "
                    f"{', '.join(sorted(missing_keys))}"
                )

            validated_panels.append(
                {
                    "panel": index,
                    "title": str(panel["title"]).strip(),
                    "scene_description": str(
                        panel["scene_description"]
                    ).strip(),
                    "image_prompt": str(
                        panel["image_prompt"]
                    ).strip(),
                }
            )

        return validated_panels

    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        print("Full Gemini Response:")
        print(output_text if "output_text" in locals() else "")
        raise ValueError(
            f"Gemini returned invalid JSON: {e}"
        )

    except Exception as e:
        print("Gemini Generation Error:", e)
        raise
    