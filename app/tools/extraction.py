import json

from app.ai.llm import client, MODEL_NAME
from app.ai.prompts import EXTRACTION_PROMPT
from app.schema.invoice import InvoiceCreate


def extract_invoice(parsed_text: str) -> dict:

    # ---------------------------------------------------------
    # 1. SEND PARSED DOCUMENT TO LLM
    # ---------------------------------------------------------

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": EXTRACTION_PROMPT,
            },
            {
                "role": "user",
                "content": parsed_text,
            },
        ],
    )

    content = response.choices[0].message.content

    # ---------------------------------------------------------
    # 2. CHECK LLM RESPONSE
    # ---------------------------------------------------------

    if not content:
        raise ValueError(
            "LLM returned an empty response."
        )

    content = content.strip()

    # ---------------------------------------------------------
    # 3. REMOVE MARKDOWN CODE FENCES
    # ---------------------------------------------------------

    if content.startswith("```"):

        if content.startswith("```json"):
            content = content[len("```json"):]

        elif content.startswith("```"):
            content = content[len("```"):]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

    # ---------------------------------------------------------
    # 4. CONVERT JSON TEXT TO PYTHON DICTIONARY
    # ---------------------------------------------------------

    try:
        data = json.loads(content)

    except json.JSONDecodeError:

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1 or start >= end:
            raise ValueError(
            "LLM did not return a valid JSON object.\n"
            f"Response was:\n{content}"
        )

        json_content = content[start:end + 1]

        try:
            data = json.loads(json_content)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON.\n"
                f"Response was:\n{content}"
            ) from exc

    # ---------------------------------------------------------
    # 5. VALIDATE JSON AGAINST INVOICE SCHEMA
    # ---------------------------------------------------------

    try:
        invoice = InvoiceCreate.model_validate(data)

    except Exception as exc:
        raise ValueError(
            "LLM returned JSON that does not match "
            "the invoice schema.\n"
            f"Validation error:\n{exc}"
        ) from exc

    # ---------------------------------------------------------
    # 6. CHECK EXTRACTION SUFFICIENCY
    # ---------------------------------------------------------

    extraction_issues = []

    # --------------------------------
    # Invoice-level checks
    # --------------------------------

    if not invoice.company_name:
        extraction_issues.append({
        "field": "company_name",
        "issue": "Company name could not be extracted",
    })
    

    if not invoice.items:
        extraction_issues.append(
            {
                "field": "items",
                "issue": (
                    "Invoice items could not be extracted"
                ),
            }
        )

    # --------------------------------
    # Item-level checks
    # --------------------------------

    for index, item in enumerate(
        invoice.items,
        start=1,
    ):

        if item.quantity is None:
            extraction_issues.append(
                {
                    "field": (
                        f"items[{index}].quantity"
                    ),
                    "issue": (
                        "Quantity could not be extracted"
                    ),
                }
            )

        if item.unit_price is None:
            extraction_issues.append(
                {
                    "field": (
                        f"items[{index}].unit_price"
                    ),
                    "issue": (
                        "Unit price could not be extracted"
                    ),
                }
            )

    # ---------------------------------------------------------
    # 7. RETURN INVOICE + EXTRACTION ISSUES
    # ---------------------------------------------------------

    return {
        "invoice": invoice,
        "extraction_issues": extraction_issues,
    }

