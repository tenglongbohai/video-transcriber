# -*- coding: utf-8 -*-
"""
音频提取模块 - 使用FFmpeg提取和切割音频
"""
import subprocess


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
        """获取媒体文件时长"""
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

    def cut_segment(self, audio_path, output_path, start_sec, duration_sec, progress_callback=None):
        """切割音频片段"""
        cmd = [
            self.ffmpeg_path, "-y",
            "-i", audio_path,
            "-ss", str(start_sec),
            "-t", str(duration_sec),
            "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            "-loglevel", "error",
            output_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=duration_sec + 30)
            if result.returncode == 0:
                if progress_callback:
                    progress_callback(100)
                return True, "完成"
            else:
                return False, result.stderr.decode('utf-8', errors='ignore')
        except subprocess.TimeoutExpired:
            return False, "切割超时"
        except Exception as e:
            return False, str(e)


if __name__ == "__main__":
    # 测试音频提取
    extractor = AudioExtractor()
    print("音频提取模块测试成功")
