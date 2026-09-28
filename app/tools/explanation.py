import json

from app.ai.llm import client, MODEL_NAME
from app.ai.prompts import EXPLANATION_PROMPT


def explain_validation_tool(
    validation_result: dict,
) -> str:

    validation_json = json.dumps(
        validation_result,
        default=str,
        indent=2,
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": EXPLANATION_PROMPT,
            },
            {
                "role": "user",
                "content": validation_json,
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "LLM returned an empty explanation."
        )

    return content.strip()