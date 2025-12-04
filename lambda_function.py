import json
import boto3
from datetime import datetime

s3 = boto3.client('s3')
BUCKET_NAME = "marketing-calendly-project"
LANDING_PREFIX = "landing/"

def lambda_handler(event, context):
    try:
        print("📩 Calendly Webhook Event Received:")
        print(json.dumps(event, indent=2))

        # Convert whole event to a JSON string and wrap it in a record
        record = {"json_record": json.dumps(event)}

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        file_name = f"{LANDING_PREFIX}event_{timestamp}.json"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(record),
            ContentType='application/json'
        )

        print(f"✅ File saved to s3://{BUCKET_NAME}/{file_name}")

        return {"statusCode": 200, "body": json.dumps({"message": "Webhook saved"})}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
