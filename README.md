# 视频转文字工具

一款基于 Web 的视频转录工具，支持本地 Whisper 语音识别和 MiniMax AI 润色，可将视频中的语音快速转换为带标点、分段的 Word 文档。

## 功能特点

- 🎬 **视频转文字**：支持 MP4、AVI、MKV、MOV 等主流视频格式
- 🎤 **Whisper 语音识别**：本地运行，无需上传，支持 Tiny/Small/Medium 三种模型
- ✂️ **智能分段**：按时间长度的片段分别转录
- 📝 **标点添加**：自动为转录文本添加标点符号
- ✨ **AI 润色**（可选）：接入 MiniMax API 进行文本润色
- 📄 **Word 导出**：生成规范的 .docx 文档

## 系统要求

- Windows 10/11 系统
- Python 3.8+
- ffmpeg（用于提取音频）
- GPU 加速（可选，NVIDIA CUDA 用于提升转录速度）

## 安装步骤

### 1. 安装 Python

从 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python 3.8 或更高版本，安装时勾选 "Add Python to PATH"。

### 2. 安装 ffmpeg

Windows 用户推荐使用 winget 安装：

```powershell
winget install ffmpeg
```

或者从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载并配置环境变量。

### 3. 安装依赖

在工具目录下打开终端，运行：

```powershell
pip install -r requirements.txt
```

### 4. （可选）安装 GPU 加速

如果使用 NVIDIA 显卡，安装 CUDA 后 Whisper 转录速度会大幅提升：

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 使用方法

### 启动服务

在工具目录下打开终端，运行：

```powershell
python web_server.py
```

启动成功后，打开浏览器访问：**http://localhost:5000**

### 操作步骤

1. **选择视频文件**：点击文件选择区域，选择要转录的视频
2. **设置输出文件名**：默认使用视频文件名，可自定义
3. **选择 Whisper 模型**：
   - Tiny：最快，效果一般
   - Small：推荐，速度和效果平衡
   - Medium：效果最好，速度较慢
4. **设置分段时长**：建议 5-10 分钟，大视频建议更短
5. **配置选项**：
   - ✅ 本地标点：自动添加标点（默认开启）
   - ✅ MiniMax 润色：需要提供 API Key
6. **开始转录**：点击「开始转录」按钮

### MiniMax API Key 获取

1. 访问 [MiniMax 开放平台](https://www.minimaxi.com/)
2. 注册并登录账号
3. 在控制台获取 API Key
4. 勾选「MiniMax 润色」后，在输入框中粘贴 Key

> 注意：MiniMax 润色是付费功能，需要账户有足够余额。

### 查看进度

- 页面实时显示转录进度
- 日志区域显示详细处理信息
- 可随时暂停或停止任务

### 获取结果

转录完成后，文档会自动下载到浏览器下载目录，也可以在视频所在文件夹找到生成的 .docx 文件。

## 常见问题

### Q: 转录速度慢？
- 使用 GPU 加速：确保已安装 CUDA 和 PyTorch GPU 版本
- 选择更小的模型：Tiny 模型速度最快
- 减小分段时长：减少单次处理量

### Q: 音频时长显示 0 秒？
- 确保已正确安装 ffmpeg
- 确保 ffmpeg 已添加到系统环境变量

### Q: 标点没有添加？
- 确保勾选了「本地标点」选项
- 或勾选「MiniMax 润色」使用 AI 添加标点

### Q: MiniMax 润色失败？
- 检查 API Key 是否正确
- 确保账户有足够余额
- 检查网络连接

## 项目结构

```
video_transcriber/
├── web_server.py      # Web 服务端
├── video_transcriber.py  # 核心转录模块
├── web/
│   └── index.html     # 前端页面
├── requirements.txt   # Python 依赖
└── uploads/           # 上传文件目录
```

## 技术栈

- **后端**：Flask（Python Web 框架）
- **语音识别**：OpenAI Whisper
- **AI 润色**：MiniMax API（Anthropic 兼容接口）
- **前端**：HTML5 + CSS3 + JavaScript

## 制作信息

制作人 [@科技锐评](https://weibo.com/u/3315426953)

## 免责声明

本工具仅用于学习和研究使用，请勿用于任何非法用途。使用 MiniMax API 产生的费用由用户自行承担。
