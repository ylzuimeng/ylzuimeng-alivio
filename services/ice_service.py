from alibabacloud_ice20201109.client import Client
from alibabacloud_tea_openapi import models as open_api_models

class ICEService:
    def __init__(self, access_key_id, access_key_secret, region):
        self.client = Client(open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint=f'ice.{region}.aliyuncs.com'
        ))

    def create_workflow(self, workflow_config):
        """创建自定义视频剪辑工作流"""
        try:
            response = self.client.create_workflow(workflow=workflow_config)
            return response.body.get('WorkflowId')
        except Exception as e:
            print(f"创建工作流失败: {e}")
            return None

    def do_workflow_task(self, workflow_id, parameters):
        """执行工作流任务"""
        try:
            response = self.client.submit_media_producing_job(
                # WorkflowId=workflow_id,
                InputParameters=parameters
            )
            return response.body
        except Exception as e:
            print(f"执行工作流任务失败: {e}")
            raise

    def check_job_status(self, job_id):
        """检查工作流任务状态"""
        try:
            response = self.client.get_workflow_task_status(JobId=job_id)
            return response.body["Status"]
        except Exception as e:
            print(f"检查任务 {job_id} 状态失败: {e}")
            return None 