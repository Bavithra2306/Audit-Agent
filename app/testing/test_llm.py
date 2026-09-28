from app.ai.llm import client, MODEL_NAME


response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {
            "role": "user",
            "content": "What is an invoice? Answer in one sentence.",
        }
    ],
)


print(response.choices[0].message.content)