import re


def getLLMReply(content: str) -> str:
    """
    获取大模型的回复，提取 </think>

标签之后的内容。
    """
    marker = '</think>'
    idx = content.rfind(marker)
    if idx != -1:
        return content[idx + len(marker):].strip()
    return content.strip()
