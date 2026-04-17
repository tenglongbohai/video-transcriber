# 视频转文字工具 v1.0.0

一款基于 Web 的视频转录工具，支持本地 Faster-Whisper 语音识别和 MiniMax AI 润色，可将视频中的语音快速转换为带标点、分段的 Word 文档。

## 功能特点

- 🎬 **视频转文字**：支持 MP4、AVI、MKV、MOV 等主流视频格式
- 🎤 **Faster-Whisper 语音识别**：本地运行，无需上传，支持 Tiny/Small/Medium 三种模型
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

### 1. 下载并解压

下载最新版本，解压到任意目录。

### 2. 双击运行

双击 `点击运行.py`，程序会自动检测并安装缺失的依赖。

> 提示：如果提示 ffmpeg 未安装，输入 `y` 自动安装，或手动运行 `winget install Gyan.FFmpeg`

### 3. 开始使用

打开浏览器访问 http://localhost:5000

## 使用方法

### 启动服务

**方式一：双击运行（推荐）**
直接双击 `点击运行.py`，会自动打开浏览器

**方式二：命令行运行**
在工具目录下打开终端，运行：

```powershell
python 点击运行.py
```

启动后会自动打开浏览器访问：**http://localhost:5000**

### 操作步骤

1. **选择视频文件**：点击文件选择区域，选择要转录的视频
2. **设置输出文件名**：默认使用视频文件名，可自定义
3. **选择 Faster-Whisper 模型**：
   - Tiny：最快，效果一般
   - Small：推荐，速度和效果平衡
   - Medium：效果最好，速度较慢
4. **设置分段时长**：建议 5-10 分钟，大视频建议更短
5. **配置选项**：
   - ✅ 本地标点：自动添加标点（默认开启）
   - ✅ MiniMax 润色：需要提供 API Key
6. **开始转录**：点击「开始转录」按钮

### MiniMax Token Plan Key 获取

1. 访问 [MiniMax Token Plan 订阅页面](https://platform.minimaxi.com/subscribe/token-plan)
2. 选择并订阅合适的套餐
3. 在 [接口密钥页面](https://platform.minimaxi.com/user-center/basic-information/interface-key) 创建 Token Plan Key
4. 勾选「MiniMax 润色」后，在输入框中粘贴 Key

> 注意：需要订阅 Token Plan 后才能使用，Key 仅在订阅有效期内有效。

### 查看进度

- 页面实时显示转录进度
- 日志区域显示详细处理信息
- 可随时暂停或停止任务

### 获取结果

转录完成后，文档会自动下载到浏览器下载目录，也可以在视频所在文件夹找到生成的 .docx 文件。

### 输出文件文件夹

程序运行后会自动创建 `输出文件` 文件夹，用于存放：
- 上传的视频文件（临时存储）
- 转录生成的 Word 文档

> 此文件夹已加入 `.gitignore`，不会同步到 GitHub。

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
video_transcriber_v2/
├── 点击运行.py        # 主程序（Web服务 + 转录 + 润色）
├── requirements.txt   # Python 依赖
├── README.md          # 使用说明
├── web/
│   └── index.html     # 前端页面
└── 输出文件/          # 转录结果目录（自动创建）
```

## 技术栈

- **后端**：Flask（Python Web 框架）
- **语音识别**：Faster-Whisper（基于 OpenAI Whisper 的高性能实现，GPU 加速可达 4 倍速）
- **AI 润色**：MiniMax API（Anthropic 兼容接口）
- **前端**：HTML5 + CSS3 + JavaScript

## 制作信息

制作人 [@科技锐评](https://weibo.com/u/3315426953)

## 免责声明

本工具仅用于学习和研究使用，请勿用于任何非法用途。使用 MiniMax API 产生的费用由用户自行承担。
