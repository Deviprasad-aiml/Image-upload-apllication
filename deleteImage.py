import json, os, boto3

s3 = boto3.client("s3")
table = boto3.resource("dynamodb").Table(os.environ["TABLE"])
BUCKET = os.environ["BUCKET"]


def respond(code, body):
    return {"statusCode": code, "body": json.dumps(body)}


def lambda_handler(event, context):
    image_id = (event.get("pathParameters") or {}).get("imageId")
    if not image_id:
        return respond(400, {"error": "imageId is required"})

    # Look up the S3 key from the database instead of trusting the client
    item = table.get_item(Key={"imageId": image_id}).get("Item")
    if not item:
        return respond(404, {"error": "Image not found"})

    s3.delete_object(Bucket=BUCKET, Key=item["key"])
    table.delete_item(Key={"imageId": image_id})

    return respond(200, {"deleted": image_id})
