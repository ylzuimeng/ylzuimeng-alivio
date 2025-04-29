import tkinter as tk
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor

class UploadPanel(tk.Frame):
    def __init__(self, master, oss_service):
        super().__init__(master)
        self.oss_service = oss_service
        self.queue = []
        self.progress_bars = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.init_ui()

    def init_ui(self):
        self.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.upload_btn = tk.Button(self, text="选择文件上传", command=self.select_files)
        self.upload_btn.pack()

    def select_files(self):
        from tkinter import filedialog
        file_paths = filedialog.askopenfilenames()
        for path in file_paths:
            self.queue.append(path)
            self.listbox.insert(tk.END, path)
            self.executor.submit(self.upload_file, path)

    def upload_file(self, file_path):
        # 这里调用oss_service.upload_file
        # 上传进度可通过回调或定时刷新
        pass 