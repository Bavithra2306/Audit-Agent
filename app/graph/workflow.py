from langgraph.graph import StateGraph, START, END

from app.graph.state import InvoiceState
from app.graph.nodes import (
    parse_node,
    extraction_node,
    identity_guard_node,
    calculation_node,
    validation_node,
    explanation_node,
)


def route_after_extraction(state: InvoiceState) -> str:
    status = state.get("status")
    if status == "NEEDS_INVOICE_NUMBER":
        return "end"          # fixed message, no LLM explanation needed
    if status == "FAILED":
        return "explain"
    if state.get("is_reaudit"):
        return "identity_guard"
    return "calculate"


def route_after_identity_guard(state: InvoiceState) -> str:
    # Wrong invoice uploaded → reject, skip calculation/validation
    if state.get("status") == "REJECTED":
        return "explain"

    return "calculate"


def build_workflow():

    graph = StateGraph(InvoiceState)

    graph.add_node("parse", parse_node)
    graph.add_node("extract", extraction_node)
    graph.add_node("identity_guard", identity_guard_node)
    graph.add_node("calculate", calculation_node)
    graph.add_node("validate", validation_node)
    graph.add_node("explain", explanation_node)

    graph.add_edge(START, "parse")
    graph.add_edge("parse", "extract")

    graph.add_conditional_edges(
        "extract",
        route_after_extraction,
        {
            "explain": "explain",
            "identity_guard": "identity_guard",
            "calculate": "calculate",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "identity_guard",
        route_after_identity_guard,
        {
            "explain": "explain",
            "calculate": "calculate",
        },
    )

    graph.add_edge("calculate", "validate")
    graph.add_edge("validate", "explain")
    graph.add_edge("explain", END)

    return graph.compile()