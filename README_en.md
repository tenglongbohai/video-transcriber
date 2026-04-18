# Video to Text Tool v3.0.0

A Web-based video transcription tool with local Faster-Whisper speech recognition and MiniMax AI polishing. Convert video audio to well-formatted Word documents with punctuation and sections.

## Changelog

### v3.0.0 (2026-04-18)
- 🛑 **Optimized shutdown**: Removed redundant popup, closes directly on confirmation
- 🚀 **One-click startup script**: Double-click to launch
- 🔧 **Environment check script**: Auto-detect/install Python, ffmpeg dependencies

### v2.0.0 (2026-04-17)
- ✨ **MiniMax AI Polishing**: Auto-add punctuation, generate video outline
- 🔧 **API Test Interface**: Test MiniMax API connection in real-time
- 📝 **Auto-check after polishing**: Auto-fill punctuation if missing
- 🗑️ **Removed packaging feature**: Simplified structure
- 🧹 **Cleanup optimization**: Auto-clean old logs on startup

### v1.0.0 (2026-04-14)
- Initial release
- Faster-Whisper speech recognition
- Local punctuation addition
- Word document export

## Features

- 🎬 **Video to Text**: Support MP4, AVI, MKV, MOV and other formats
- 🎤 **Faster-Whisper Recognition**: Local processing, no upload required. Tiny/Small/Medium models available
- ✂️ **Smart Segmentation**: Transcribe by time segments
- 📝 **Punctuation**: Auto-add punctuation to transcript
- ✨ **AI Polishing** (optional): MiniMax API for text polishing
- 📄 **Word Export**: Generate .docx documents

## Requirements

- Windows 10/11
- Python 3.8+
- ffmpeg (for audio extraction)
- GPU acceleration (optional, NVIDIA CUDA for faster transcription)

## Installation

### 1. Download & Extract

Download the latest version and extract to any directory.

### 2. Check Environment (First-time Setup)

Double-click `检测环境.bat` to auto-detect and install missing dependencies (Python, ffmpeg).

> Tip: If prompted about ffmpeg, type `y` to auto-install, or run `winget install Gyan.FFmpeg`

### 3. Launch Service

Double-click `双击运行(后等待几秒钟).bat`, wait a few seconds for browser to open.

### 4. Start Using

Open browser to http://localhost:5000

## Usage

### Start Service

Double-click `双击运行(后等待几秒钟).bat`, wait ~8 seconds for browser to open.

### Stop Service

Double-click `关闭服务.bat`, or click "关闭服务" button on the page.

### How to Use

1. **Select video**: Click the file area to choose video
2. **Set output filename**: Default is video filename, customizable
3. **Select Faster-Whisper model**:
   - Tiny: Fastest, basic quality
   - Small: Recommended, balance of speed and quality
   - Medium: Best quality, slower
4. **Set segment duration**: 5-10 minutes recommended, shorter for large videos
5. **Configure options**:
   - ✅ Local Punctuation: Auto-add punctuation (default on)
   - ✅ MiniMax Polishing: Requires API Key
6. **Start transcription**: Click "开始转录"

### MiniMax Token Plan Key

1. Visit [MiniMax Token Plan](https://platform.minimaxi.com/subscribe/token-plan)
2. Subscribe to a plan
3. Create Token Plan Key at [API Keys](https://platform.minimaxi.com/user-center/basic-information/interface-key)
4. Enable "MiniMax 润色" and paste the Key

> Note: Subscription required, Key only valid during subscription period.

### View Progress

- Real-time progress on page
- Log area shows detailed processing info
- Pause or stop anytime

### Get Results

After transcription, document auto-downloads to browser downloads, also saved in the video folder as .docx.

### Output Folder

Program auto-creates `输出文件` folder for:
- Uploaded videos (temporary)
- Generated Word documents

> This folder is in `.gitignore`, not synced to GitHub.

## FAQ

### Q: Transcription too slow?
- Use GPU: Install CUDA and PyTorch GPU version
- Use smaller model: Tiny is fastest
- Reduce segment duration

### Q: Audio duration shows 0?
- Ensure ffmpeg installed correctly
- Ensure ffmpeg in system PATH

### Q: Punctuation not added?
- Ensure "本地标点" option checked
- Or enable "MiniMax 润色" for AI punctuation

### Q: MiniMax polishing failed?
- Check API Key is correct
- Ensure account has sufficient balance
- Check network connection

## Project Structure

```
video_transcriber_v2/
├── main.py                      # Flask Web main program, all API endpoints
├── requirements.txt              # Python dependencies
├── README.md                     # Documentation (Chinese)
├── README_en.md                  # Documentation (English)
├── .gitignore                    # Git ignore rules
├── web/                         # Frontend resources
│   └── index.html               # Web interface
├── core/                        # Core modules
│   ├── __init__.py              # Package init
│   ├── 音频提取.py              # Extract audio with ffmpeg
│   ├── 转录.py                  # Speech recognition with faster-whisper
│   ├── 标点处理.py              # Add punctuation
│   ├── 润色.py                  # MiniMax API polishing
│   ├── 导出Word.py              # Generate .docx
│   └── 进度管理.py              # SSE progress updates
├── 检测环境.bat                 # Check/install dependencies
├── 双击运行(后等待几秒钟).bat   # Launch service
└── 关闭服务.bat                 # Stop service
```

**Runtime files (not packaged, not uploaded):**
- `web_server.log` - Program log
- `输出文件/` - Output directory

## Tech Stack

- **Backend**: Flask (Python Web Framework)
- **Speech Recognition**: Faster-Whisper (High-performance OpenAI Whisper implementation, up to 4x faster with GPU)
- **AI Polishing**: MiniMax API (Anthropic-compatible)
- **Frontend**: HTML5 + CSS3 + JavaScript

## Author

[@科技锐评](https://weibo.com/u/3315426953)

## Disclaimer

For learning and research only. Do not use for illegal purposes. MiniMax API usage fees are the user's responsibility.
