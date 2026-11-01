import json, os, time, uuid, boto3
from botocore.config import Config

REGION = os.environ["AWS_REGION"]
s3 = boto3.client(
    "s3",
    region_name=REGION,
    endpoint_url=f"https://s3.{REGION}.amazonaws.com",
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
)
table = boto3.resource("dynamodb").Table(os.environ["TABLE"])
BUCKET = os.environ["BUCKET"]
ALLOWED = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    ctype = body.get("contentType")
    if ctype not in ALLOWED:
        return {"statusCode": 400, "body": json.dumps({"error": "Unsupported file type"})}

    image_id = str(uuid.uuid4())
    key = f"uploads/{image_id}.{ctype.split('/')[1]}"

    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": BUCKET, "Key": key, "ContentType": ctype},
        ExpiresIn=300,
    )
    table.put_item(Item={"imageId": image_id, "key": key, "createdAt": int(time.time())})

    return {"statusCode": 200, "body": json.dumps({"uploadUrl": url, "imageId": image_id})}
