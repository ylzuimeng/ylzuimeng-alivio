from concurrent.futures import ThreadPoolExecutor
import time
import csv
from services.ice_service import ICEService
from services.oss_service import OSSService

class WorkflowManager:
    def __init__(self, ice_service, oss_service):
        self.ice_service = ice_service
        self.oss_service = oss_service

    def do_workflow_task(self, workflow_id, input_bucket, task_params):
        """执行单个工作流任务"""
        try:
            # 构造工作流参数
            parameters = {
                "opening_video": f"oss://{input_bucket}/{task_params['opening_video']}",
                "opening_text": task_params["opening_text"],
                "transition_image": f"oss://{input_bucket}/{task_params['transition_image']}",
                "transition_text": task_params["transition_text"],
                "main_video": f"oss://{input_bucket}/{task_params['main_video']}",
                "subtitle_text": task_params["subtitle_text"],
                "ending_video": f"oss://{input_bucket}/{task_params['ending_video']}"
            }

            response = self.ice_service.do_workflow_task(workflow_id, parameters)
            return {
                "task": task_params,
                "job_id": response["JobId"],
                "status": "Submitted"
            }
        except Exception as e:
            print(f"执行任务 {task_params['main_video']} 失败: {e}")
            return None

    def process_tasks(self, workflow_id, input_bucket, output_bucket, task_file):
        """批量处理任务"""
        results = []
        with open(task_file, "r") as f:
            reader = csv.DictReader(f)
            tasks = list(reader)

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(
                lambda task: self.do_workflow_task(workflow_id, input_bucket, task),
                tasks
            ))
            results = [result for result in results if result]

        return results

    def monitor_tasks(self, results, output_bucket):
        """监控任务状态并下载结果"""
        for result in results:
            job_id = result["job_id"]
            main_video = result["task"]["main_video"]
            while True:
                status = self.ice_service.check_job_status(job_id)
                if status == 'Success':
                    output_object_name = f"final_video_{main_video}"
                    local_path = f"output/{output_object_name}"
                    self.oss_service.download_result(output_bucket, output_object_name, local_path)
                    break
                elif status == 'Failed':
                    print(f"任务 {job_id} 失败")
                    break
                else:
                    time.sleep(5)  # 每 5 秒检查一次状态 