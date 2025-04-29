import tkinter as tk
from tkinter import messagebox, filedialog
from config.config_manager import ConfigManager
from core.workflow_manager import WorkflowManager
from services.ice_service import ICEService
from services.oss_service import OSSService
import os

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("阿里云视频处理程序")
        self.config_manager = ConfigManager()
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """设置UI界面"""
        # 居中显示窗口
        window_width = 900
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 配置参数输入框
        label_font = ("Arial", 18)
        entry_font = ("Arial", 18)
        button_font = ("Arial", 18)

        self.entries = {}
        row = 0
        fields = [
            ("Access Key ID:", "access_key_id"),
            ("Access Key Secret:", "access_key_secret"),
            ("Region:", "region"),
            ("Input Bucket:", "input_bucket"),
            ("Output Bucket:", "output_bucket"),
            ("Workflow ID:", "workflow_id")
        ]

        for label_text, field_name in fields:
            tk.Label(self.root, text=label_text, font=label_font).grid(
                row=row, column=0, sticky='e', padx=30, pady=15)
            
            entry = tk.Entry(self.root, font=entry_font, width=40)
            if field_name == "access_key_secret":
                entry.config(show='*')
            
            # 添加输入变化监听
            entry.bind('<KeyRelease>', lambda e, field=field_name: self.on_entry_change(field))
            
            entry.grid(row=row, column=1, sticky='w', padx=30, pady=15)
            self.entries[field_name] = entry
            row += 1

        # 创建按钮
        run_button = tk.Button(
            self.root, text="运行处理流程", 
            command=self.run_process, 
            font=button_font, width=20, height=2
        )
        run_button.grid(row=row, column=0, columnspan=2, pady=20)

        upload_button = tk.Button(
            self.root, text="上传文件到输入Bucket", 
            command=self.upload_files_to_oss, 
            font=button_font, width=20, height=2
        )
        upload_button.grid(row=row+1, column=0, columnspan=2, pady=20)

        # 添加状态标签
        self.status_label = tk.Label(
            self.root, 
            text="", 
            font=("Arial", 12),
            fg="green"
        )
        self.status_label.grid(row=row+2, column=0, columnspan=2, pady=10)

    def on_entry_change(self, field_name):
        """当输入框内容变化时自动保存配置"""
        try:
            self.config_manager.save_config_from_ui(self.entries)
            self.show_status(f"配置已自动保存")
        except Exception as e:
            self.show_status(f"保存配置失败: {str(e)}", is_error=True)

    def show_status(self, message, is_error=False):
        """显示状态信息"""
        self.status_label.config(
            text=message,
            fg="red" if is_error else "green"
        )
        # 3秒后清除状态信息
        self.root.after(3000, lambda: self.status_label.config(text=""))

    def load_config(self):
        """加载配置"""
        try:
            self.config_manager.load_config_to_ui(self.entries)
            self.show_status("配置已加载")
        except Exception as e:
            self.show_status(f"加载配置失败: {str(e)}", is_error=True)

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
            task_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            if not task_file:
                messagebox.showerror("错误", "未选择任务文件。")
                return

            # 执行任务
            results = workflow_manager.process_tasks(
                config['workflow_id'],
                config['input_bucket'],
                config['output_bucket'],
                task_file
            )

            messagebox.showinfo(
                "信息", 
                f"批量提交 {len(results)} 个任务，任务ID列表：{[r['job_id'] for r in results]}"
            )

            # 监控任务
            workflow_manager.monitor_tasks(results, config['output_bucket'])

        except Exception as e:
            messagebox.showerror("错误", f"执行过程中出现错误: {e}")

    def upload_files_to_oss(self):
        """上传文件到OSS"""
        try:
            config = self.config_manager.get_config()
            if not all(config.get(key) for key in ['access_key_id', 'access_key_secret', 'region', 'input_bucket']):
                messagebox.showerror("错误", "请先填写Access Key、Secret、Region和Input Bucket")
                return

            # 选择文件
            file_paths = filedialog.askopenfilenames(title="选择要上传的文件")
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

            messagebox.showinfo("成功", f"成功上传 {success_count} 个文件到 {config['input_bucket']}")

        except Exception as e:
            messagebox.showerror("错误", f"上传文件时出错: {e}")

    def run(self):
        """运行主程序"""
        self.root.mainloop() 