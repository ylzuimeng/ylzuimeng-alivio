import tkinter as tk

class DownloadPanel(tk.Frame):
    def __init__(self, master, oss_service):
        super().__init__(master)
        self.oss_service = oss_service
        self.init_ui()

    def init_ui(self):
        self.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.download_btn = tk.Button(self, text="批量下载", command=self.batch_download)
        self.download_btn.pack()

    def batch_download(self):
        # TODO: 批量下载并压缩，生成下载链接
        pass 