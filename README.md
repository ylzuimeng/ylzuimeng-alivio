# 阿里云视频处理程序

这是一个基于阿里云ICE和OSS服务的视频处理程序，用于批量处理视频文件。

## 功能特点

- 支持批量上传视频文件到OSS
- 支持自定义视频处理工作流
- 支持批量执行视频处理任务
- 自动监控任务状态并下载处理结果

## 项目结构

```
.
├── config/                # 配置管理
│   ├── __init__.py
│   └── config_manager.py
├── core/                 # 核心业务逻辑
│   ├── __init__.py
│   └── workflow_manager.py
├── services/            # 服务层
│   ├── __init__.py
│   ├── ice_service.py
│   └── oss_service.py
├── ui/                  # 用户界面
│   ├── __init__.py
│   └── main_window.py
├── utils/              # 工具函数
│   └── __init__.py
├── main.py             # 程序入口
├── requirements.txt    # 依赖包
└── README.md          # 项目说明
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python main.py
```

2. 在界面中填写阿里云配置信息：
   - Access Key ID
   - Access Key Secret
   - Region
   - Input Bucket
   - Output Bucket
   - Workflow ID

3. 点击"上传文件到输入Bucket"按钮上传视频文件

4. 准备CSV格式的任务文件，包含以下字段：
   - opening_video
   - opening_text
   - transition_image
   - transition_text
   - main_video
   - subtitle_text
   - ending_video

5. 点击"运行处理流程"按钮，选择任务文件开始处理

## 注意事项

- 请确保已正确配置阿里云账号和权限
- 请确保OSS Bucket已创建并具有正确的访问权限
- 请确保Workflow ID有效且配置正确 