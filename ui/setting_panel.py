import tkinter as tk

class SettingPanel(tk.Frame):
    def __init__(self, master, config_manager):
        super().__init__(master)
        self.config_manager = config_manager
        self.entries = {}
        self.init_ui()
        self.load_config()

    def init_ui(self):
        fields = [
            ("Access Key ID", "access_key_id"),
            ("Access Key Secret", "access_key_secret"),
            ("Region", "region"),
            ("Input Bucket", "input_bucket"),
            ("Output Bucket", "output_bucket"),
            ("Workflow ID", "workflow_id")
        ]
        for i, (label, key) in enumerate(fields):
            tk.Label(self, text=label).grid(row=i, column=0, sticky='e', padx=10, pady=5)
            entry = tk.Entry(self, width=40, show='*' if 'secret' in key else '')
            entry.grid(row=i, column=1, sticky='w', padx=10, pady=5)
            self.entries[key] = entry

        tk.Button(self, text="保存配置", command=self.save_config).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def save_config(self):
        self.config_manager.save_config_from_ui(self.entries)
        tk.messagebox.showinfo("提示", "配置已保存！")

    def load_config(self):
        self.config_manager.load_config_to_ui(self.entries) 