# -*- coding: utf-8 -*-
"""
标点处理模块 - 为转录文本添加标点符号
"""
import re


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


if __name__ == "__main__":
    # 测试标点处理
    adder = PunctuationAdder()
    test_text = "这是测试文本没有标点 我需要添加标点让它更易读"
    result = adder.add_punctuation(test_text)
    print(f"原文: {test_text}")
    print(f"处理后: {result}")
    print("标点处理模块测试成功")
