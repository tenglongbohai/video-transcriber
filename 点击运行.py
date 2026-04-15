#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频转文字工具 - Web 服务器
"""

import os
import sys
import json
import time
import uuid
import queue
import threading
import traceback
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from functools import wraps

# 自动安装依赖
def install_deps():
    deps = {
        "flask": "flask",
        "psutil": "psutil",
        "faster-whisper": "faster-whisper",
        "python-docx": "python-docx",
    }
    for module, package in deps.items():
        try:
            __import__(module)
        except ImportError:
            print(f"正在安装 {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
    # 检查 ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except:
        print("\n" + "!" * 50)
        print("警告: ffmpeg 未安装!")
        print("是否自动安装? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            # 尝试用 winget 安装
            try:
                print("正在安装 ffmpeg (使用 winget)...")
                subprocess.check_call(["winget", "install", "Gyan.FFmpeg"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                print("ffmpeg 安装成功! 请重启程序")
                sys.exit(0)
            except:
                try:
                    # 尝试用 scoop 安装
                    print("正在安装 ffmpeg (使用 scoop)...")
                    subprocess.check_call(["scoop", "install", "ffmpeg"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    print("ffmpeg 安装成功! 请重启程序")
                    sys.exit(0)
                except:
                    print("自动安装失败，请手动安装:")
                    print("  winget install Gyan.FFmpeg")
                    print("  或从 https://ffmpeg.org 下载")
                    sys.exit(1)
        else:
            print("继续运行，但转录功能可能不可用")
            print("手动安装: winget install Gyan.FFmpeg")
        print("!" * 50)

install_deps()

# 文件日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from flask import (
    Flask, request, send_file, jsonify,
    render_template, Response
)
import psutil

# 尝试导入可选依赖
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# 创建 Flask 应用
app = Flask(__name__, static_folder='web', template_folder='web')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024  # 10GB max
app.config['UPLOAD_FOLDER'] = '输出目录'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 全局状态
class TaskState:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.is_stopped = False
        self.progress = 0
        self.stage = ""
        self.current_chunk = 0
        self.total_chunks = 0
        self.time_left = ""
        self.last_update = time.time()

state = TaskState()

# SSE 消息队列
message_queue = queue.Queue()


def send_sse(data):
    """发送 Server-Sent Events"""
    try:
        message_queue.put_nowait(json.dumps(data))
    except:
        pass


def sse_generator():
    """SSE 流生成器"""
    import time as time_module
    while True:  # 始终保持连接
        try:
            data = message_queue.get(timeout=5)
            yield f"data: {data}\n\n"
        except queue.Empty:
            # 发送心跳保持连接
            yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"


# ============================================================================
# 核心模块
# ============================================================================

class AudioExtractor:
    """FFmpeg 音频提取器"""

    def __init__(self, ffmpeg_path="ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def extract_audio(self, video_path, output_path, sample_rate=16000, progress_callback=None):
        """提取音频"""
        cmd = [
            self.ffmpeg_path, "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", str(sample_rate), "-ac", "1",
            "-loglevel", "error", output_path
        ]

        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, universal_newlines=True
            )

            duration = self._get_duration(video_path)

            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                if line and "time=" in line and progress_callback:
                    current_time = self._parse_time(line)
                    if duration > 0:
                        progress = min(95, int(current_time / duration * 100))
                        progress_callback(progress)

            if process.returncode == 0:
                if progress_callback:
                    progress_callback(100)
                return True, "完成"
            else:
                return False, process.stderr.read()

        except Exception as e:
            return False, str(e)

    def _get_duration(self, media_path):
        """获取媒体文件时长（支持视频和音频）"""
        cmd = [
            self.ffmpeg_path, "-i", media_path,
            "-f", "null", "-"
        ]
        try:
            result = subprocess.run(
                cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                timeout=30, text=True
            )
            stderr = result.stderr

            # 尝试解析多种格式
            # 格式1: Duration: 00:05:30.50
            for line in stderr.split('\n'):
                if "Duration:" in line:
                    try:
                        d = line.split("Duration:")[1].split(",")[0].strip()
                        h, m, s = d.split(":")
                        duration = int(h) * 3600 + int(m) * 60 + float(s)
                        if duration > 0:
                            return duration
                    except:
                        pass

            # 格式2: 直接解析 time= 字段
            for line in stderr.split('\n'):
                if "time=" in line:
                    try:
                        t = line.split("time=")[1].split(" ")[0].strip()
                        h, m, s = t.split(":")
                        duration = int(h) * 3600 + int(m) * 60 + float(s)
                        if duration > 0:
                            return duration
                    except:
                        pass

        except:
            pass

        # 备用方法：使用 ffprobe
        try:
            ffprobe_path = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
            cmd2 = [
                ffprobe_path, "-v", "error", "-show_entries",
                "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                media_path
            ]
            result2 = subprocess.run(cmd2, stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=30, text=True)
            if result2.stdout.strip():
                return float(result2.stdout.strip())
        except:
            pass

        return 0

    def _parse_time(self, line):
        try:
            t = line.split("time=")[1].split(" ")[0]
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
        except:
            return 0


class Transcriber:
    """Whisper 转录器"""

    def __init__(self, model_size="small", compute_type="int8_float16"):
        self.model_size = model_size
        self.compute_type = compute_type
        self.model = None

    def load_model(self):
        """加载模型"""
        if not FASTER_WHISPER_AVAILABLE:
            return False, "请安装 faster-whisper"

        try:
            # 使用 float32 稳定兼容
            compute = "float32"

            self.model = WhisperModel(
                self.model_size,
                device="cuda",
                compute_type=compute
            )
            return True, "模型加载成功"
        except Exception as e:
            return False, str(e)

    def transcribe(self, audio_path, chunk_start=0, chunk_end=None):
        """转录"""
        if self.model is None:
            success, msg = self.load_model()
            if not success:
                return False, msg, ""

        try:
            kwargs = {
                "audio": audio_path,
                "vad_filter": False,  # 关闭VAD，避免时间戳问题
                "language": "zh",
            }

            segments, info = self.model.transcribe(**kwargs)

            text_parts = []
            for segment in segments:
                seg_start = segment.start
                # 过滤时间范围
                if chunk_start > 0 and seg_start < chunk_start:
                    continue
                if chunk_end and seg_start >= chunk_end:
                    break
                text = segment.text.strip()
                if text:
                    text_parts.append(text)

            return True, "完成", " ".join(text_parts)
        except Exception as e:
            return False, str(e), ""


class PunctuationAdder:
    """标点处理"""

    def add_punctuation(self, text):
        """添加标点 - 智能分析文本结构添加标点"""
        if not text:
            return text

        # 清理文本
        text = text.strip()

        # 检测是否有标点，如果没有就智能添加
        has_punctuation = any(c in '。！？.?!' for c in text)

        if not has_punctuation:
            # 智能添加标点：按长度和常见停顿点分段
            import re
            result = []
            current = ""

            # 按空格或换行分割成句子单位
            words = re.split(r'[\s\n]+', text)

            for word in words:
                if not word.strip():
                    continue
                current += word + " "

                # 根据当前长度添加标点
                if len(current) >= 80:  # 长句用句号
                    # 找合适的断点（常见连词、转折词）
                    for sep in ['，', '的', '了', '是', '在', '和', '也', '就', '但']:
                        if sep in current[:-1]:
                            idx = current.rfind(sep)
                            if idx > 20:  # 确保前面有足够内容
                                result.append(current[:idx+1].strip() + "。")
                                current = current[idx+1:].strip()
                                if current:
                                    current += " "
                                break
                    else:
                        # 没找到断点，直接截断
                        if current.strip():
                            result.append(current.strip() + "。")
                            current = ""
                elif len(current) >= 50 and current.rstrip().endswith(('，', '、')):
                    # 中等长度，遇到逗号可以考虑结束
                    pass

            # 处理剩余内容
            if current.strip():
                if len(current.strip()) > 15:
                    result.append(current.strip() + "。")
                else:
                    result.append(current.strip())

            # 合并结果
            if result:
                return " ".join(result)

        # 已有标点，简单整理
        sentences = []
        current = ""
        for char in text:
            current += char
            if char in '。！？.?!':
                sentences.append(current.strip())
                current = ""

        if current.strip():
            sentences.append(current.strip())

        return " ".join(sentences) if sentences else text

    def split_paragraphs(self, text, max_length=500):
        """分段"""
        import re
        paragraphs = []
        current = ""

        parts = re.split(r'[。！？\?!]+', text)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if len(current) + len(part) <= max_length:
                current += part + "。 "
            else:
                if current.strip():
                    paragraphs.append(current.strip())
                current = part + "。 "

        if current.strip():
            paragraphs.append(current.strip())

        return paragraphs if paragraphs else [text]


class MiniMaxAPI:
    """MiniMax API - Anthropic 兼容接口"""

    BASE_URL = "https://api.minimaxi.com/anthropic"
    MODEL = "MiniMax-M2.7"

    def __init__(self, api_key=None):
        self.api_key = api_key  # 必须从外部传入
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

    def polish_text(self, text, log_callback=None):
        """润色文本"""
        def log(msg, level="info"):
            print(msg)
            if log_callback:
                log_callback(msg, level)

        if not text or not text.strip():
            return text

        if not self.api_key:
            log("未配置 MiniMax API Key，跳过润色", "warning")
            return text

        if not ANTHROPIC_AVAILABLE:
            log("请安装 anthropic SDK: pip install anthropic", "error")
            return text

        prompt = f"""你是一个专业的文本润色助手。请对以下转录文本进行润色：
1. 添加适当的标点符号
2. 修正明显的语音识别错误
3. 保持原意和口语风格
4. 直接输出润色结果，不要添加任何解释

原文：
{text}"""

        try:
            client = anthropic.Anthropic(
                base_url=self.BASE_URL,
                api_key=self.api_key
            )

            log("正在调用 MiniMax API...")
            message = client.messages.create(
                model=self.MODEL,
                max_tokens=4096,
                temperature=1.0,  # MiniMax 推荐使用 1.0
                system="你是一个专业的文本润色助手。直接输出润色结果，不要添加解释或说明。",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            for block in message.content:
                if block.type == "text":
                    result = block.text.strip()
                    log(f"润色完成，返回 {len(result)} 字符", "info")
                    return result

            log("润色返回空结果", "warning")
            return text

        except Exception as e:
            log(f"MiniMax API 错误: {e}", "error")
            return text


class WordExporter:
    """Word 导出"""

    def create_document(self, paragraphs, output_path, title="转录文档"):
        """创建文档"""
        if not DOCX_AVAILABLE:
            return False, "请安装 python-docx"

        try:
            doc = Document()
            doc.core_properties.title = title

            heading = doc.add_heading(title, 0)
            heading.alignment = 1

            doc.add_paragraph(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            doc.add_paragraph()

            for para_text in paragraphs:
                if para_text.strip():
                    para = doc.add_paragraph(para_text)
                    para.paragraph_format.line_spacing = 1.5

            doc.save(output_path)
            return True, output_path
        except Exception as e:
            return False, str(e)


# ============================================================================
# 转录任务
# ============================================================================

def run_transcription(video_path, output_dir, config):
    """执行转录任务"""
    global state

    state.is_running = True
    state.is_paused = False
    state.is_stopped = False
    state.progress = 0
    state.stage = "初始化"
    state.current_chunk = 0
    state.total_chunks = 0

    temp_files = []

    try:
        # 初始化
        send_sse({"type": "log", "level": "info", "message": "开始初始化组件..."})
        audio_extractor = AudioExtractor()
        transcriber = Transcriber(config["model"])
        punctuation_adder = PunctuationAdder()
        word_exporter = WordExporter()

        # 输出文件
        output_name = config.get("output_name", "转录文档")
        output_path = os.path.join(output_dir, output_name + ".docx")

        # 阶段1: 音频提取
        send_sse({"type": "log", "level": "info", "message": "正在提取音频..."})
        state.stage = "音频提取"

        temp_audio = os.path.join(output_dir, f".temp_{uuid.uuid4().hex}.wav")
        temp_files.append(temp_audio)

        success, msg = audio_extractor.extract_audio(
            video_path, temp_audio,
            progress_callback=lambda p: send_sse({
                "type": "progress",
                "progress": int(p * 0.1),
                "stage": f"音频提取 {p}%"
            })
        )

        if not success:
            raise Exception(f"音频提取失败: {msg}")

        send_sse({"type": "log", "level": "info", "message": "音频提取完成"})

        # 加载模型
        send_sse({"type": "log", "level": "info", "message": "加载 Whisper 模型..."})
        success, msg = transcriber.load_model()
        if not success:
            raise Exception(msg)

        send_sse({"type": "log", "level": "info", "message": f"模型加载完成: {transcriber.model_size}"})

        # 获取总时长
        total_duration = audio_extractor._get_duration(temp_audio)
        chunk_duration = int(config.get("chunk_duration", 5)) * 60
        total_chunks = max(1, int(total_duration / chunk_duration) + (1 if total_duration % chunk_duration > 0 else 0))
        state.total_chunks = total_chunks

        send_sse({"type": "log", "level": "info", "message": f"音频时长: {total_duration:.0f}秒, 分为 {total_chunks} 个片段"})

        # 阶段2: 分段转录
        all_texts = []
        base_progress = 10
        start_time = time.time()
        remaining_chunks = total_chunks

        def calc_time_left(current, total):
            """计算预估剩余时间"""
            elapsed = time.time() - start_time
            if current == 0:
                return ""
            avg_time_per_chunk = elapsed / current
            remaining = int(avg_time_per_chunk * (total - current))
            if remaining >= 60:
                return f"{remaining // 60}分{remaining % 60}秒"
            return f"{remaining}秒"

        for chunk_idx in range(total_chunks):
            # 检查停止
            if state.is_stopped:
                send_sse({"type": "log", "level": "warning", "message": "任务已停止"})
                break

            # 等待暂停
            while state.is_paused and not state.is_stopped:
                time.sleep(0.5)

            chunk_start = chunk_idx * chunk_duration
            chunk_end = min(chunk_start + chunk_duration, total_duration)
            state.current_chunk = chunk_idx + 1
            state.stage = f"转录片段 {chunk_idx + 1}/{total_chunks}"

            # 每个片段开始时就更新进度
            chunk_progress = (chunk_idx + 1) / total_chunks * 50
            time_left = calc_time_left(chunk_idx + 1, total_chunks)
            send_sse({
                "type": "progress",
                "progress": base_progress + int(chunk_progress),
                "stage": state.stage,
                "current": chunk_idx + 1,
                "total": total_chunks,
                "time_left": time_left
            })
            send_sse({"type": "log", "level": "info", "message": f"开始转录片段 {chunk_idx + 1}/{total_chunks} ({chunk_start:.0f}-{chunk_end:.0f}秒)"})

            success, msg, text = transcriber.transcribe(
                temp_audio,
                chunk_start=chunk_start,
                chunk_end=chunk_end
            )

            if success and text:
                all_texts.append(text)
                send_sse({"type": "log", "level": "info", "message": f"片段 {chunk_idx + 1} 完成 ({len(text)} 字符)"})
            else:
                send_sse({"type": "log", "level": "warning", "message": f"片段 {chunk_idx + 1} 失败: {msg}"})

        send_sse({"type": "log", "level": "info", "message": f"转录完成，共 {len(all_texts)} 个片段，总字符: {sum(len(t) for t in all_texts)}"})

        if not all_texts:
            raise Exception("没有成功转录任何内容")

        # 阶段3: 润色或标点
        full_text = " ".join(all_texts)
        send_sse({"type": "log", "level": "info", "message": f"原始文本: {len(full_text)} 字符"})

        state.stage = "后处理"

        if config.get("polish", False):
            api_key = config.get("api_key", "").strip()
            if not api_key:
                send_sse({"type": "log", "level": "warning", "message": "未提供 MiniMax API Key，无法润色"})
                full_text = punctuation_adder.add_punctuation(full_text)
                send_sse({"type": "progress", "progress": 75, "stage": "添加标点", "time_left": "即将完成"})
            else:
                send_sse({"type": "log", "level": "info", "message": "正在使用 MiniMax 润色..."})
                try:
                    minimax = MiniMaxAPI(api_key)
                    segments = punctuation_adder.split_paragraphs(full_text, 800)
                    polish_start = time.time()
                    polished = []

                    # 日志回调函数
                    def polish_log(msg, level="info"):
                        send_sse({"type": "log", "level": level, "message": msg})

                    for i, seg in enumerate(segments):
                        polished.append(minimax.polish_text(seg, log_callback=polish_log))
                        elapsed = time.time() - polish_start
                        remaining = int(elapsed / (i + 1) * (len(segments) - i - 1))
                        time_str = f"{remaining}秒" if remaining < 60 else f"{remaining // 60}分{remaining % 60}秒"
                        send_sse({
                            "type": "progress",
                            "progress": 60 + int((i + 1) / len(segments) * 20),
                            "stage": f"润色中 {i + 1}/{len(segments)}",
                            "time_left": time_str
                        })
                    full_text = " ".join(polished)
                    send_sse({"type": "log", "level": "info", "message": f"润色完成: {len(full_text)} 字符"})
                except Exception as e:
                    send_sse({"type": "log", "level": "warning", "message": f"润色失败: {e}，使用原始文本"})
                    full_text = punctuation_adder.add_punctuation(full_text)
                    send_sse({"type": "progress", "progress": 75, "stage": "添加标点", "time_left": "即将完成"})
        else:
            # 未启用润色时，智能添加标点
            full_text = punctuation_adder.add_punctuation(full_text)
            send_sse({"type": "progress", "progress": 75, "stage": "添加标点", "time_left": "即将完成"})

        send_sse({"type": "log", "level": "info", "message": f"标点处理后: {len(full_text)} 字符"})

        # 阶段4: 导出
        state.stage = "生成文档"
        send_sse({"type": "progress", "progress": 90, "stage": "生成文档", "time_left": "即将完成"})

        # 智能分段
        paragraphs = punctuation_adder.split_paragraphs(full_text, 500)
        send_sse({"type": "log", "level": "info", "message": f"智能分段: {len(paragraphs)} 个段落"})

        success, msg = word_exporter.create_document(
            paragraphs, output_path,
            title=f"视频转录 - {output_name}"
        )

        if not success:
            raise Exception(f"文档创建失败: {msg}")

        # 完成
        send_sse({"type": "progress", "progress": 100, "stage": "完成", "time_left": "0秒"})
        send_sse({
            "type": "complete",
            "output_path": output_path,
            "output_name": output_name,
            "memory": f"{psutil.virtual_memory().percent:.0f}%"
        })

        state.progress = 100
        state.stage = "完成"

    except Exception as e:
        send_sse({"type": "error", "message": str(e)})
        send_sse({"type": "log", "level": "error", "message": f"错误: {traceback.format_exc()}"})

    finally:
        # 清理临时文件
        for f in temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass

        state.is_running = False


# ============================================================================
# Flask 路由
# ============================================================================

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    """开始转录"""
    if state.is_running:
        return jsonify({"error": "已有任务在运行"}), 400

    video = request.files.get('video')
    if not video:
        return jsonify({"error": "未上传视频文件"}), 400

    # 保存上传的视频
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}_{video.filename}")
    video.save(video_path)

    # 获取视频所在目录作为输出目录
    video_dir = os.path.dirname(video_path)

    # 获取配置
    config = {
        "output_name": request.form.get('output_name', '转录文档'),
        "model": request.form.get('model', 'small'),
        "chunk_duration": int(request.form.get('chunk_duration', 5)),
        "punctuation": request.form.get('punctuation', 'true').lower() == 'true',
        "polish": request.form.get('polish', 'false').lower() == 'true',
        "api_key": request.form.get('api_key', ''),
        "video_path": video_path,
        "output_dir": video_dir  # 保存到视频所在目录
    }

    # 启动后台任务
    thread = threading.Thread(target=run_transcription, args=(video_path, app.config['UPLOAD_FOLDER'], config))
    thread.daemon = True
    thread.start()

    return jsonify({"status": "started"})


@app.route('/api/progress')
def progress():
    """SSE 进度流"""
    return Response(sse_generator(), mimetype='text/event-stream')


@app.route('/api/pause', methods=['POST'])
def pause():
    """暂停/继续"""
    state.is_paused = not state.is_paused
    return jsonify({"paused": state.is_paused})


@app.route('/api/stop', methods=['POST'])
def stop():
    """停止任务"""
    state.is_stopped = True
    return jsonify({"stopped": True})


@app.route('/api/status')
def status():
    """获取状态"""
    return jsonify({
        "running": state.is_running,
        "paused": state.is_paused,
        "memory": f"{psutil.virtual_memory().percent:.0f}"
    })


@app.route('/api/download/<path:filename>')
def download(filename):
    """下载文件"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        file_path = file_path + '.docx'
    return send_file(file_path, as_attachment=True)


# ============================================================================
# 启动
# ============================================================================

if __name__ == '__main__':
    import webbrowser
    import threading

    print("=" * 50)
    print("视频转文字工具 - Web 版")
    print("=" * 50)
    print("正在启动服务器...")
    print("=" * 50)

    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open('http://localhost:5000')

    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
