import os
from configparser import ConfigParser
import tkinter as tk

CONFIG_FILE = "config.ini"

class ConfigManager:
    def __init__(self):
        self.config = ConfigParser()
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)

    def load_config_to_ui(self, entries):
        """将配置加载到UI输入框"""
        if 'default' in self.config:
            section = self.config['default']
            for key, entry in entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, section.get(key, ''))

    def save_config_from_ui(self, entries):
        """从UI输入框保存配置"""
        self.config['default'] = {
            key: entry.get() for key, entry in entries.items()
        }
        with open(CONFIG_FILE, 'w') as f:
            self.config.write(f)

    def get_config(self):
        """获取配置"""
        return self.config['default'] if 'default' in self.config else {} 