import json
from openai import OpenAI
import boto3
from boto3.dynamodb.conditions import Key
import time

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('chat-history')

def lambda_handler(event, context):
    client = OpenAI(
        api_key="<OPEN_AI_API_KEY>")

    print("event = ", event)

    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": ""
        }

    try:
        body = json.loads(event.get('body', '{}'))
        print("body = ", body)
    except json.JSONDecodeError:
        return {"statusCode": 400, 'headers': headers, "body": json.dumps({"error": "Invalid JSON"})}

    user_prompt = body.get('user_prompt')
    user_id = body.get('user_id')

    if not user_prompt:
        return {"statusCode": 400, 'headers': headers, "body": json.dumps({"error": "user_prompt is required"})}

    if not user_id:
        return {"statusCode": 400, 'headers': headers, "body": json.dumps({"error": "user_id is required"})}

    # Retrieve the last 6 messages from DynamoDB
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id),
        ScanIndexForward=False,
        Limit=6
    )
    conversation_history = response.get('Items', [])
    print("conversation_history we got:",conversation_history)

    conversation_history = sorted(conversation_history, key=lambda x: x['timestamp'])
    print("conversation_history after sort",conversation_history)

    print("remove unnecessary fields from conversation_history")
    # Remove unnecessary fields
    for message in conversation_history:
        del message['user_id']
        del message['timestamp']

    conversation_history.append({"role": "user", "content": user_prompt})

    print("conversation_history after adding prompt",conversation_history)


    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-3.5-turbo",
        max_tokens=100
    )

    ai_reply = chat_completion.choices[0].message.content

    # Save only the last prompt and reply to DynamoDB
    timestamp = int(time.time() * 1000)
    table.put_item(
        Item={
            'user_id': user_id,
            'timestamp': timestamp,
            'role': 'user',
            'content': user_prompt
        }
    )
    table.put_item(
        Item={
            'user_id': user_id,
            'timestamp': timestamp + 1,
            'role': 'assistant',
            'content': ai_reply
        }
    )


    return {
        "statusCode": 200,
        'headers': headers,
        "body": json.dumps({"ai_reply": ai_reply})
    }
