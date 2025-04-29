import csv
import os
from configparser import ConfigParser
from alibabacloud_ice20201109.client import Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_oss20190517.client import Client as OSSClient
from alibabacloud_ice20201109 import models as ice_models
from concurrent.futures import ThreadPoolExecutor
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

CONFIG_FILE = "config.ini"

def create_workflow(access_key_id, access_key_secret, region):
    """
    创建自定义视频剪辑工作流
    """
    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        endpoint=f'ice.{region}.aliyuncs.com'
    )
    client = Client(config)

    workflow = {
        "Name": "custom-video-workflow",
        "Description": "自定义视频剪辑工作流",
        "InputBucket": "your-input-bucket",
        "InputLocation": f"oss-{region}",
        "OutputBucket": "your-output-bucket",
        "OutputLocation": f"oss-{region}",
        "Steps": [
            {
                "Name": "add_opening_text",
                "Action": "AliyunMts.AddSubtitle",
                "Input": ["${opening_video}"],
                "Output": ["opening_with_text_${opening_video}"],
                "Args": {
                    "SubtitleText": "${opening_text}"
                }
            },
            {
                "Name": "add_transition_text",
                "Action": "AliyunMts.AddTextToImage",
                "Input": ["${transition_image}"],
                "Output": ["transition_with_text_${transition_image}"],
                "Args": {
                    "Text": "${transition_text}"
                }
            },
            {
                "Name": "add_subtitle_to_main_video",
                "Action": "AliyunMts.AddSubtitle",
                "Input": ["${main_video}"],
                "Output": ["main_video_with_subtitle_${main_video}"],
                "Args": {
                    "SubtitleText": "${subtitle_text}"
                }
            },
            {
                "Name": "video_composition",
                "Action": "AliyunMts.ComposeVideo",
                "Input": [
                    "opening_with_text_${opening_video}",
                    "transition_with_text_${transition_image}",
                    "main_video_with_subtitle_${main_video}",
                    "${ending_video}"
                ],
                "Output": ["final_video_${main_video}"]
            }
        ]
    }

    try:
        # 使用正确的API方法名和请求模型
        request = ice_models.CreateMediaProducingTemplateRequest(
            template=workflow
        )
        response = client.create_media_producing_template(request)
        print(response.body.get('TemplateId'))
        return response.body.get('TemplateId')
    except Exception as e:
        print(f"创建工作流失败: {e}")
        return None


def execute_workflow_task(client, template_id, input_bucket, task_params):
    """
    触发单个工作流任务
    """
    opening_video = task_params["opening_video"]
    opening_text = task_params["opening_text"]
    transition_image = task_params["transition_image"]
    transition_text = task_params["transition_text"]
    main_video = task_params["main_video"]
    subtitle_text = task_params["subtitle_text"]
    ending_video = task_params["ending_video"]

    # 构造工作流参数（需与工作流定义中的变量名一致）
    parameters = {
        "opening_video": f"oss://{input_bucket}/{opening_video}",
        "opening_text": opening_text,
        "transition_image": f"oss://{input_bucket}/{transition_image}",
        "transition_text": transition_text,
        "main_video": f"oss://{input_bucket}/{main_video}",
        "subtitle_text": subtitle_text,
        "ending_video": f"oss://{input_bucket}/{ending_video}"
    }

    try:
        # 使用正确的API方法名和请求模型
        request = ice_models.SubmitMediaProducingJobRequest(
            template_id=template_id,
            parameters=parameters
        )
        response = client.submit_media_producing_job(request)
        return {
            "task": task_params,
            "job_id": response.body["JobId"],
            "status": "Submitted"
        }
    except Exception as e:
        print(f"执行任务 {task_params['main_video']} 失败: {e}")
        return None


def check_job_status(client, job_id):
    """
    检查工作流任务状态
    """
    try:
        # 使用正确的API方法名和请求模型
        request = ice_models.GetMediaProducingJobRequest(
            job_id=job_id
        )
        response = client.get_media_producing_job(request)
        return response.body["Status"]
    except Exception as e:
        print(f"检查任务 {job_id} 状态失败: {e}")
        return None


def download_result(oss_client, output_bucket, object_name, local_path):
    """
    从 OSS 下载结果文件
    """
    try:
        oss_client.get_object_to_file(output_bucket, object_name, local_path)
        print(f"成功下载 {object_name} 到 {local_path}")
    except Exception as e:
        print(f"下载 {object_name} 失败: {e}")


def load_config():
    config = ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if 'default' in config:
            section = config['default']
            access_key_id_entry.delete(0, tk.END)
            access_key_id_entry.insert(0, section.get('access_key_id', ''))
            access_key_secret_entry.delete(0, tk.END)
            access_key_secret_entry.insert(0, section.get('access_key_secret', ''))
            region_entry.delete(0, tk.END)
            region_entry.insert(0, section.get('region', ''))
            input_bucket_entry.delete(0, tk.END)
            input_bucket_entry.insert(0, section.get('input_bucket', ''))
            output_bucket_entry.delete(0, tk.END)
            output_bucket_entry.insert(0, section.get('output_bucket', ''))
            workflow_id_entry.delete(0, tk.END)
            workflow_id_entry.insert(0, section.get('workflow_id', ''))


def save_config():
    config = ConfigParser()
    config['default'] = {
        'access_key_id': access_key_id_entry.get(),
        'access_key_secret': access_key_secret_entry.get(),
        'region': region_entry.get(),
        'input_bucket': input_bucket_entry.get(),
        'output_bucket': output_bucket_entry.get(),
        'workflow_id': workflow_id_entry.get()
    }
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)


def run_process():
    try:
        # 保存配置
        save_config()
        # 读取配置
        access_key_id = access_key_id_entry.get()
        access_key_secret = access_key_secret_entry.get()
        region = region_entry.get()
        input_bucket = input_bucket_entry.get()
        output_bucket = output_bucket_entry.get()
        template_id = workflow_id_entry.get()

        if not template_id:
            messagebox.showerror("错误", "请填写Template ID（可在阿里云ICE控制台获取）")
            return

        # 初始化 ICE 客户端
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint=f'ice.{region}.aliyuncs.com'
        )
        ice_client = Client(config)

        # 初始化 OSS 客户端
        oss_config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint=f'oss-{region}.aliyuncs.com'
        )
        oss_client = OSSClient(oss_config)

        # 选择任务文件
        task_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not task_file:
            messagebox.showerror("错误", "未选择任务文件。")
            return

        # 批量执行任务
        with open(task_file, "r") as f:
            reader = csv.DictReader(f)
            tasks = list(reader)

        with ThreadPoolExecutor(max_workers=10) as executor:  # 控制并发数
            results = list(executor.map(lambda task: execute_workflow_task(ice_client, template_id, input_bucket, task), tasks))
            results = [result for result in results if result]

        messagebox.showinfo("信息", f"批量提交 {len(results)} 个任务，任务ID列表：{[r['job_id'] for r in results]}")

        # 监控任务状态并下载结果
        for result in results:
            job_id = result["job_id"]
            main_video = result["task"]["main_video"]
            while True:
                status = check_job_status(ice_client, job_id)
                if status == 'Success':
                    output_object_name = f"final_video_{main_video}"
                    local_path = os.path.join("output", output_object_name)
                    download_result(oss_client, output_bucket, output_object_name, local_path)
                    break
                elif status == 'Failed':
                    messagebox.showerror("错误", f"任务 {job_id} 失败")
                    break
                else:
                    time.sleep(5)  # 每 5 秒检查一次状态
    except Exception as e:
        messagebox.showerror("错误", f"执行过程中出现错误: {e}")


def upload_files_to_oss():
    try:
        access_key_id = access_key_id_entry.get()
        access_key_secret = access_key_secret_entry.get()
        region = region_entry.get()
        input_bucket = input_bucket_entry.get()
        if not (access_key_id and access_key_secret and region and input_bucket):
            messagebox.showerror("错误", "请先填写Access Key、Secret、Region和Input Bucket")
            return
        # 选择文件（可多选）
        file_paths = filedialog.askopenfilenames(title="选择要上传的文件")
        if not file_paths:
            return
        oss_client = OSSClient(open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint=f'oss-{region}.aliyuncs.com'
        ))
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            try:
                with open(file_path, 'rb') as f:
                    oss_client.put_object(input_bucket, file_name, f)
            except Exception as e:
                messagebox.showerror("错误", f"上传 {file_name} 失败: {e}")
                return
        messagebox.showinfo("成功", f"成功上传 {len(file_paths)} 个文件到 {input_bucket}")
    except Exception as e:
        messagebox.showerror("错误", f"上传文件时出错: {e}")


# 创建主窗口
root = tk.Tk()
root.title("阿里云视频处理程序")

# 居中显示窗口
window_width = 900
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 配置参数输入框
label_font = ("Arial", 18)
entry_font = ("Arial", 18)
button_font = ("Arial", 18)

row = 0
tk.Label(root, text="Access Key ID:", font=label_font).grid(row=row, column=0, sticky='e', padx=30, pady=15)
access_key_id_entry = tk.Entry(root, font=entry_font, width=40)
access_key_id_entry.grid(row=row, column=1, sticky='w', padx=30, pady=15)
row += 1

tk.Label(root, text="Access Key Secret:", font=label_font).grid(row=row, column=0, sticky='e', padx=30, pady=15)
access_key_secret_entry = tk.Entry(root, show='*', font=entry_font, width=40)
access_key_secret_entry.grid(row=row, column=1, sticky='w', padx=30, pady=15)
row += 1

tk.Label(root, text="Region:", font=label_font).grid(row=row, column=0, sticky='e', padx=30, pady=15)
region_entry = tk.Entry(root, font=entry_font, width=40)
region_entry.grid(row=row, column=1, sticky='w', padx=30, pady=15)
row += 1

tk.Label(root, text="Input Bucket:", font=label_font).grid(row=row, column=0, sticky='e', padx=30, pady=15)
input_bucket_entry = tk.Entry(root, font=entry_font, width=40)
input_bucket_entry.grid(row=row, column=1, sticky='w', padx=30, pady=15)
row += 1

tk.Label(root, text="Output Bucket:", font=label_font).grid(row=row, column=0, sticky='e', padx=30, pady=15)
output_bucket_entry = tk.Entry(root, font=entry_font, width=40)
output_bucket_entry.grid(row=row, column=1, sticky='w', padx=30, pady=15)
row += 1

tk.Label(root, text="Workflow ID:", font=label_font).grid(row=row, column=0, sticky='e', padx=30, pady=15)
workflow_id_entry = tk.Entry(root, font=entry_font, width=40)
workflow_id_entry.grid(row=row, column=1, sticky='w', padx=30, pady=15)
row += 1

# 创建按钮，跨两列居中
run_button = tk.Button(root, text="运行处理流程", command=run_process, font=button_font, width=20, height=2)
run_button.grid(row=row, column=0, columnspan=2, pady=20)

# 新增上传文件按钮
upload_button = tk.Button(root, text="上传文件到输入Bucket", command=upload_files_to_oss, font=button_font, width=20, height=2)
upload_button.grid(row=row+1, column=0, columnspan=2, pady=20)

# 启动时加载配置
load_config()
# 运行主循环
root.mainloop()
    