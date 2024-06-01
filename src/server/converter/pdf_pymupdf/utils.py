from functools import partial
from typing import List

import regex as re


def has_suffix(file_path, suffix):
    return file_path.lower().endswith(suffix.lower())


is_pdf = partial(has_suffix, suffix=".pdf")
is_markdown = partial(has_suffix, suffix=".md")


def clean_text(input_str) -> str:
    if not input_str:
        return ""
    # 同一文本块不换行
    formatted_str = re.sub(r"[\r\n]+", "", input_str)
    # 删除中文间空格
    formatted_str = re.sub(r"(\p{Han})(\p{Z}+)(\p{Han})", r"\1\3", formatted_str)
    # # 中文和字母、数字之间加空格
    formatted_str = re.sub(r"(\p{Han})([\p{Latin}\p{Nd}])", r"\1 \2", formatted_str)
    # # 字母、数字和中文之间加空格
    formatted_str = re.sub(r"([\p{Latin}\p{Nd}])(\p{Han})", r"\1 \2", formatted_str)
    # # 删除标点前后空格
    formatted_str = re.sub(r"\p{Z}*([\p{P}])\p{Z}*", r"\1", formatted_str)
    # # 部分标点后加一个空格
    formatted_str = re.sub(r"([,:;])", r"\1 ", formatted_str)
    # # 移除多余的空格
    formatted_str = re.sub(r"\p{Z}+", " ", formatted_str).strip()

    return formatted_str


def flags_decomposer(flags):
    """Make font flags human readable."""
    ret: List[str] = []
    if flags & 2**0:
        ret.append("superscript")
    if flags & 2**1:
        ret.append("italic")
    if flags & 2**2:
        ret.append("serifed")
    else:
        ret.append("sans")
    if flags & 2**3:
        ret.append("monospaced")
    else:
        ret.append("proportional")
    if flags & 2**4:
        ret.append("bold")
    return ", ".join(ret)
