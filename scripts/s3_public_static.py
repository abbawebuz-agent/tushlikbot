"""
One-off: сделать статику в S3-совместимом бакете публично читаемой.

Tigris (Railway Object Storage) НЕ поддерживает bucket policy (PutBucketPolicy
возвращает NotImplemented). Публичный доступ включается объектным ACL
public-read на каждом объекте. Этот скрипт проставляет public-read на все
объекты под префиксом статики (AWS_STATIC_LOCATION/*).

Читает те же переменные, что и Django-настройки (AWS_*).

Запуск (внутри контейнера web, где есть boto3 и переменные окружения):
    python scripts/s3_public_static.py
"""

import os
import sys

import boto3
from botocore.exceptions import ClientError


def _clean(v):
    v = (v or "").strip()
    return v or None


def main():
    bucket = _clean(os.getenv("AWS_STORAGE_BUCKET_NAME"))
    if not bucket:
        sys.exit("AWS_STORAGE_BUCKET_NAME is not set")

    prefix = (os.getenv("AWS_STATIC_LOCATION", "static") or "static").strip("/") + "/"

    session = boto3.session.Session(
        aws_access_key_id=_clean(os.getenv("AWS_ACCESS_KEY_ID")),
        aws_secret_access_key=_clean(os.getenv("AWS_SECRET_ACCESS_KEY")),
        region_name=_clean(os.getenv("AWS_S3_REGION_NAME")),
    )
    s3 = session.client(
        "s3",
        endpoint_url=_clean(os.getenv("AWS_S3_ENDPOINT_URL")),
    )

    paginator = s3.get_paginator("list_objects_v2")
    total = 0
    failed = 0
    first_error = None
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            try:
                s3.put_object_acl(Bucket=bucket, Key=key, ACL="public-read")
                total += 1
            except ClientError as e:
                failed += 1
                if first_error is None:
                    first_error = f"{key}: {e}"

    print(f"public-read applied: {total} object(s), failed: {failed}")
    if first_error:
        print(f"first error: {first_error}")
        sys.exit(1)
    if total == 0:
        print(f"WARNING: no objects found under s3://{bucket}/{prefix}")


if __name__ == "__main__":
    main()
