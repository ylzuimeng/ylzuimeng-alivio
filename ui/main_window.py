import tkinter as tk
from tkinter import ttk
from config.config_manager import ConfigManager
from core.workflow_manager import WorkflowManager
from services.ice_service import ICEService
from services.oss_service import OSSService
import os
from ui.upload_panel import UploadPanel
from ui.log_panel import LogPanel
from ui.download_panel import DownloadPanel

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("阿里云视频处理程序")
        self.notebook = ttk.Notebook(self.root)
        self.config_manager = ConfigManager()
        self.upload_panel = UploadPanel(self.notebook, oss_service=None)
        self.log_panel = LogPanel(self.notebook)
        self.download_panel = DownloadPanel(self.notebook, oss_service=None)
        self.notebook.add(self.upload_panel, text="上传")
        self.notebook.add(self.log_panel, text="日志")
        self.notebook.add(self.download_panel, text="下载")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.root.mainloop()

    def load_config(self):
        """加载配置"""
        self.config_manager.load_config_to_ui(self.entries)

    def run_process(self):
        """运行处理流程"""
        try:
            # 保存配置
            self.config_manager.save_config_from_ui(self.entries)
            config = self.config_manager.get_config()

            # 初始化服务
            ice_service = ICEService(
                config['access_key_id'],
                config['access_key_secret'],
                config['region']
            )
            oss_service = OSSService(
                config['access_key_id'],
                config['access_key_secret'],
                config['region']
            )
            workflow_manager = WorkflowManager(ice_service, oss_service)

            # 选择任务文件
            task_file = tk.filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            if not task_file:
                tk.messagebox.showerror("错误", "未选择任务文件。")
                return

            # 执行任务
            results = workflow_manager.process_tasks(
                config['workflow_id'],
                config['input_bucket'],
                config['output_bucket'],
                task_file
            )

            tk.messagebox.showinfo(
                "信息", 
                f"批量提交 {len(results)} 个任务，任务ID列表：{[r['job_id'] for r in results]}"
            )

            # 监控任务
            workflow_manager.monitor_tasks(results, config['output_bucket'])

        except Exception as e:
            tk.messagebox.showerror("错误", f"执行过程中出现错误: {e}")

    def upload_files_to_oss(self):
        """上传文件到OSS"""
        try:
            config = self.config_manager.get_config()
            if not all(config.get(key) for key in ['access_key_id', 'access_key_secret', 'region', 'input_bucket']):
                tk.messagebox.showerror("错误", "请先填写Access Key、Secret、Region和Input Bucket")
                return

            # 选择文件
            file_paths = tk.filedialog.askopenfilenames(title="选择要上传的文件")
            if not file_paths:
                return

            oss_service = OSSService(
                config['access_key_id'],
                config['access_key_secret'],
                config['region']
            )

            success_count = 0
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                if oss_service.upload_file(config['input_bucket'], file_name, file_path):
                    success_count += 1

            tk.messagebox.showinfo("成功", f"成功上传 {success_count} 个文件到 {config['input_bucket']}")

        except Exception as e:
            tk.messagebox.showerror("错误", f"上传文件时出错: {e}") 