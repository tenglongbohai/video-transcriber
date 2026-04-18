# -*- coding: utf-8 -*-
"""
润色模块 - 使用MiniMax API对文本进行润色
"""
import time

# 尝试导入 anthropic SDK
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class MiniMaxAPI:
    """MiniMax API - Anthropic 兼容接口"""

    BASE_URL = "https://api.minimaxi.com/anthropic"
    MODELS = ["MiniMax-M2.5", "MiniMax-M2.7", "MiniMax-M2.1", "MiniMax-M2"]

    def __init__(self, api_key=None, model="MiniMax-M2.5"):
        self.api_key = api_key  # 必须从外部传入
        self.model = model
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

    def polish_text(self, text, log_callback=None):
        """润色文本，返回 (润色后文本, 大纲)"""
        def log(msg, level="info"):
            print(msg)
            if log_callback:
                log_callback(msg, level)

        if not text or not text.strip():
            return text, ""

        if not self.api_key:
            log("未配置 MiniMax API Key，跳过润色", "warning")
            return text, ""

        if not ANTHROPIC_AVAILABLE:
            log("请安装 anthropic SDK: pip install anthropic", "error")
            return text, ""

        prompt = f"""你是一个专业的文本润色助手。请对以下转录文本进行处理：
1. 首先分析内容，生成一个简洁的视频大纲（用数字列表列出主要话题）
2. 然后对原文进行润色：添加标点、修正错误、保持口语风格
3. **必须使用简体中文输出**，不要使用繁体字
4. 严格按照以下格式输出，不要添加任何解释：

---
**视频大纲：**
:[根据内容生成的大纲，每行一个话题]

**正文：**
:[润色后的正文]
---

原文：
{text}"""

        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                client = anthropic.Anthropic(
                    base_url=self.BASE_URL,
                    api_key=self.api_key
                )

                if attempt > 0:
                    log(f"正在调用 MiniMax API（第 {attempt + 1} 次重试）...")
                else:
                    log("正在调用 MiniMax API...")

                message = client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=1.0,
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
                        raw_result = block.text.strip()
                        log(f"润色完成，返回 {len(raw_result)} 字符", "info")

                        # 提取正文和大纲部分
                        if "**正文：**" in raw_result or "**正文:**" in raw_result:
                            lines = raw_result.split('\n')
                            in_outline = False
                            in_body = False
                            outline_lines = []
                            body_lines = []
                            for line in lines:
                                # 检测大纲开始
                                if '**视频大纲' in line or '**大纲' in line:
                                    in_outline = True
                                    in_body = False
                                    continue
                                # 检测正文开始
                                if '**正文' in line:
                                    in_outline = False
                                    in_body = True
                                    continue
                                # 跳过结束标记
                                if line.strip().startswith('---'):
                                    continue
                                # 收集大纲
                                if in_outline:
                                    if line.strip():
                                        outline_lines.append(line.strip())
                                # 收集正文
                                if in_body:
                                    if not line.strip():
                                        continue
                                    body_lines.append(line.strip())

                            # 返回 (正文, 大纲) 元组
                            if body_lines:
                                result = '\n'.join(body_lines)
                                outline = '\n'.join(outline_lines) if outline_lines else ""
                                return result, outline
                            return raw_result, ""

                log("润色返回空结果", "warning")
                return text, ""

            except Exception as e:
                error_str = str(e)
                if "overloaded_error" in error_str or "529" in error_str:
                    if attempt < max_retries - 1:
                        log(f"MiniMax 服务器繁忙，{retry_delay}秒后重试...", "warning")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        log(f"MiniMax API 重试 {max_retries} 次仍失败: {e}", "error")
                        return text, ""
                else:
                    log(f"MiniMax API 错误: {e}", "error")
                    return text, ""


if __name__ == "__main__":
    # 测试润色模块（不调用API）
    api = MiniMaxAPI(api_key="test-key")
    if ANTHROPIC_AVAILABLE:
        print("润色模块测试成功 - anthropic SDK 已安装")
    else:
        print("润色模块测试成功 - 请安装 anthropic SDK")
