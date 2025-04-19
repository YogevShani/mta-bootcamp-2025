from openai import OpenAI

client = OpenAI(
    api_key="<OPEN_AI_API_KEY>")
conversation_history = []

while True:
    user_prompt = input("Enter your prompt (or 'exit' to quit): ")
    if user_prompt.lower() == 'exit':
        break

    conversation_history.append({"role": "user", "content": user_prompt})

    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-3.5-turbo",
        max_tokens=100  # Limit the number of tokens in the reply
    )

    ai_reply = chat_completion.choices[0].message.content
    print("AI:", ai_reply)

    conversation_history.append({"role": "assistant", "content": ai_reply})

