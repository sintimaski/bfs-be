import urllib

from PIL import Image
from io import BytesIO

import boto3


class S3Manager:
    def __init__(self, bucket_name):
        self.base = f"https://{bucket_name}.s3.amazonaws.com/"
        self.s3 = boto3.resource(
            "s3",
            aws_access_key_id="AKIAZMEE227CTW62T4MC",
            aws_secret_access_key="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",
        )
        self.bucket_name = bucket_name

    def put(self, file, path_list):
        path_list = [urllib.parse.quote_plus(p) for p in path_list]
        path = "/".join(path_list)
        obj = self.s3.Bucket(self.bucket_name).put_object(Key=path, Body=file)
        obj_path = self.base + obj.key
        return obj_path


def get_image_ext_for_s3(filename):
    ext = filename.rsplit(".", 1)[1] or ""
    ext = ext.lower()
    ext = "jpeg" if ext == "jpg" else ext
    return ext


def optimize_image(image):
    im = Image.open(image)
    im.thumbnail((1000, 1000), Image.BICUBIC)
    s_file = BytesIO()
    im.save(s_file, format="JPEG", quality=60, optimize=True)
    return s_file.getvalue()
