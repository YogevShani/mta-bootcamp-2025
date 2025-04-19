import json
from openai import OpenAI


def lambda_handler(event, context):
    client = OpenAI(
        api_key="<OPEN_AI_API_KEY>")

    print("event = ", event)

    try:
        body = json.loads(event.get('body', '{}'))
        print("body = ", body)
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON"})}

    conversation_history = []
    user_prompt = body.get('user_prompt')

    if not user_prompt:
        return {"statusCode": 400, "body": json.dumps({"error": "user_prompt is required"})}

    conversation_history.append({"role": "user", "content": user_prompt})

    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-3.5-turbo",
        max_tokens=100
    )

    ai_reply = chat_completion.choices[0].message.content

    return {
        "statusCode": 200,
        "body": json.dumps({"ai_reply": ai_reply})
    }
