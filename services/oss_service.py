import alibabacloud_oss_v2 as oss
import os

class OSSService:
    def __init__(self, access_key_id, access_key_secret, region):
        # 创建凭证提供者
        credentials_provider = oss.credentials.StaticCredentialsProvider(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        
        # 加载默认配置
        cfg = oss.config.load_default()
        cfg.credentials_provider = credentials_provider
        cfg.region = region
        cfg.endpoint = f'oss-{region}.aliyuncs.com'
        
        # 创建OSS客户端
        self.client = oss.Client(cfg)

    def upload_file(self, bucket, object_name, file_path):
        """上传文件到OSS"""
        try:
            # 创建上传请求
            with open(file_path, 'rb') as file_obj:
                result = self.client.put_object(
                    oss.PutObjectRequest(
                        bucket=bucket,
                        key=object_name,
                        body=file_obj
                    )
                )
            
            if result.status_code == 200:
                print(f"成功上传文件 {object_name} 到 {bucket}")
                return True
            else:
                print(f"上传文件 {object_name} 失败，状态码: {result.status_code}")
                return False
                
        except Exception as e:
            print(f"上传文件 {object_name} 失败: {str(e)}")
            return False

    def download_result(self, bucket, object_name, local_path):
        """从OSS下载结果文件"""
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 创建下载请求
            result = self.client.get_object(
                oss.GetObjectRequest(
                    bucket=bucket,
                    key=object_name
                )
            )
            
            # 保存文件
            with open(local_path, 'wb') as f:
                f.write(result.body)
                
            print(f"成功下载 {object_name} 到 {local_path}")
            return True
            
        except Exception as e:
            print(f"下载 {object_name} 失败: {str(e)}")
            return False 