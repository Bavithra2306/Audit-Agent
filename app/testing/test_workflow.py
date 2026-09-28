from app.graph.workflow import build_workflow

workflow = build_workflow()

result = workflow.invoke({
    "file_path": "uploads/invoices/example.pdf"
})

print(result)