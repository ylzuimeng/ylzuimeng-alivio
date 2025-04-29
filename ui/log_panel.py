import tkinter as tk

class LogPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.text = tk.Text(self, state='disabled')
        self.text.pack(fill=tk.BOTH, expand=True)

    def append_log(self, msg):
        self.text.config(state='normal')
        self.text.insert(tk.END, msg + '\n')
        self.text.config(state='disabled')
        self.text.see(tk.END) 