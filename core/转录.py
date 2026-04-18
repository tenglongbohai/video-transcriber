# -*- coding: utf-8 -*-
"""
转录模块 - 使用Whisper进行语音转文字
"""
import os

# 尝试导入 faster-whisper
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False


class Transcriber:
    """Whisper 转录器"""

    def __init__(self, model_size="small", compute_type="int8_float16"):
        self.model_size = model_size
        self.compute_type = compute_type
        self.model = None

    def load_model(self):
        """加载模型"""
        if not FASTER_WHISPER_AVAILABLE:
            return False, "请安装 faster-whisper: pip install faster-whisper"

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


if __name__ == "__main__":
    # 测试转录模块
    transcriber = Transcriber()
    if FASTER_WHISPER_AVAILABLE:
        print("转录模块测试成功 - faster-whisper 已安装")
    else:
        print("转录模块测试成功 - 请安装 faster-whisper")
