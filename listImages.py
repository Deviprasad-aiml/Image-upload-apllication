import json, os, boto3
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


def lambda_handler(event, context):
    items = table.scan()["Items"]
    items.sort(key=lambda i: i["createdAt"], reverse=True)
    for i in items:
        i["url"] = s3.generate_presigned_url(
            "get_object", Params={"Bucket": BUCKET, "Key": i["key"]}, ExpiresIn=3600
        )
        i["createdAt"] = int(i["createdAt"])
    return {"statusCode": 200, "body": json.dumps(items)}
