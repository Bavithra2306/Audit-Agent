from app.tools.explanation import explain_validation_tool


validation_result = {
    "status": "DISCREPANCY_FOUND",
    "discrepancies": [
        {
            "field": "subtotal",
            "issue": "Value mismatch",
            "stated": 1043340.00,
            "calculated": 1018340.00,
            "difference": 25000.00,
        }
    ],
}


print("\n========== EXPLANATION TEST ==========\n")


explanation = explain_validation_tool(
    validation_result
)


print(explanation)


print("\n======================================\n")