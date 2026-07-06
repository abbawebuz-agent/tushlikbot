"""
One-off: сделать статику в S3-совместимом бакете публично читаемой.

Нужно для провайдеров вроде Tigris (Railway Object Storage), где бакет закрыт
по умолчанию и объектного ACL public-read недостаточно — требуется bucket policy
на анонимный s3:GetObject.

Читает те же переменные, что и Django-настройки (AWS_*), и ставит политику,
разрешающую публичное чтение только префикса статики (AWS_STATIC_LOCATION/*).

Запуск (внутри контейнера web, где есть boto3 и .env):
    python scripts/s3_public_static.py
"""

import json
import os
import sys

import boto3


def _clean(v):
    v = (v or "").strip()
    return v or None


def main():
    bucket = _clean(os.getenv("AWS_STORAGE_BUCKET_NAME"))
    if not bucket:
        sys.exit("AWS_STORAGE_BUCKET_NAME is not set")

    prefix = (os.getenv("AWS_STATIC_LOCATION", "static") or "static").strip("/")

    session = boto3.session.Session(
        aws_access_key_id=_clean(os.getenv("AWS_ACCESS_KEY_ID")),
        aws_secret_access_key=_clean(os.getenv("AWS_SECRET_ACCESS_KEY")),
        region_name=_clean(os.getenv("AWS_S3_REGION_NAME")),
    )
    s3 = session.client(
        "s3",
        endpoint_url=_clean(os.getenv("AWS_S3_ENDPOINT_URL")),
    )

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadStatic",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket}/{prefix}/*",
            }
        ],
    }

    s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))
    print(f"OK: public-read policy applied to s3://{bucket}/{prefix}/*")


if __name__ == "__main__":
    main()
