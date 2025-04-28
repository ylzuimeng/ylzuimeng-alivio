from alibabacloud_oss20190517.client import Client as OSSClient
from alibabacloud_tea_openapi import models as open_api_models

class OSSService:
    def __init__(self, access_key_id, access_key_secret, region):
        self.client = OSSClient(open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint=f'oss-{region}.aliyuncs.com'
        ))

    def upload_file(self, bucket, object_name, file_path):
        """上传文件到OSS"""
        try:
            with open(file_path, 'rb') as f:
                self.client.put_object(bucket, object_name, f)
            return True
        except Exception as e:
            print(f"上传文件 {object_name} 失败: {e}")
            return False

    def download_result(self, bucket, object_name, local_path):
        """从OSS下载结果文件"""
        try:
            self.client.get_object_to_file(bucket, object_name, local_path)
            print(f"成功下载 {object_name} 到 {local_path}")
            return True
        except Exception as e:
            print(f"下载 {object_name} 失败: {e}")
            return False 