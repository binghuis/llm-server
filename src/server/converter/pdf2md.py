from os import path
from typing import Dict, List, Literal, Optional, TypedDict, Union

import pymupdf
import regex as re

"""
目前实现：
1. 识别文本内容生成目录
2. 识别表格生成 markdown 表格
3. 识别正文自然段，添加自然段前缀
4. 忽略图片
5. 忽略页眉页脚
6. 正文标题替换为完整层级标题
7. 格式化文本，删除多余空格

pymupdf 问题：
1. get_toc(simple=False) 
目录页码是根据文档内容生成的，和你自己写的目录没有关系。
2. table to_markdown() 会把 table 外文本提取为表头。
3. find_tables() 很多表无法识别，目前没找到规律。
"""


class TableRangeY(TypedDict):
    y0: float
    y1: float


class TextElement(TypedDict):
    type: Literal["text"]
    content: str
    y0: float


class TableElement(TypedDict):
    type: Literal["table"]
    content: List[List[str | None]]
    y0: float


Element = Union[TextElement, TableElement]


class PDFConverter:
    PREFFIX = "$$$"  # 自然段前缀
    NORMAL_LINE_LEFT = 85.08  # 85.08 页面默认左边距
    HEADER_Y1 = 53  # 52.84700012207031 页眉底部 y 坐标
    FOOTER_Y0 = 778  # 778.8968505859375 页脚顶部 y 坐标
    # 字体大小
    SIZE_10 = 10
    SIZE_12 = 12
    SIZE_14 = 14
    SIZE_16 = 16

    PATTERN_TOC_BLOCK = re.compile(
        r"^([\p{Han}\p{Latin}\p{Nd}\p{Zs}.]*)-{3,}([\p{Han}\p{Latin}\p{Nd}\p{P}]+)$",
        re.MULTILINE,
    )

    def __init__(self):
        self.meet_toc = False
        self.has_toc_flag = False

    def clean_text(self, input_str) -> str:
        if not input_str:
            return ""

        # 移除换行符和全角空格，但保留普通空格
        formatted_str = re.sub(r"[\u3000\r\n]+", "", input_str)
        # 中文之间删除空格
        formatted_str = re.sub(r"(\p{Han})(\p{Z}+)(\p{Han})", r"\1\3", formatted_str)
        # 中文和英文、数字之间添加空格
        formatted_str = re.sub(r"(\p{Han})([\p{Latin}\p{Nd}])", r"\1 \2", formatted_str)
        # 英文、数字和中文之间添加空格
        formatted_str = re.sub(r"([\p{Latin}\p{Nd}])(\p{Han})", r"\1 \2", formatted_str)
        # 空格+中英文标点+空格
        formatted_str = re.sub(r"\p{Z}*([\p{P}])\p{Z}*", r"\1", formatted_str)
        # 部分标点后加一个空格
        formatted_str = re.sub(r"([,:;])", r"\1 ", formatted_str)
        # 移除多余的空格
        formatted_str = re.sub(r"\p{Zs}+", " ", formatted_str).strip()

        return formatted_str

    # 判断块是否在表格坐标范围内
    def is_in_table_range(self, y: float, tables_range: List[TableRangeY]) -> bool:
        return any(range["y0"] <= y <= range["y1"] for range in tables_range)

    # 将表格转为 markdown
    def table2md(self, table: List[List[Optional[str]]]) -> str:
        if not table:
            return ""
        markdown_table = ""

        for row in table:
            markdown_table += (
                "| " + " | ".join(self.clean_text(cell) for cell in row) + " |\n"
            )
        header_sep = "| " + " | ".join("---" for _ in table[0]) + " |\n"
        markdown_table = (
            markdown_table.split("\n", 1)[0]
            + "\n"
            + header_sep
            + markdown_table.split("\n", 1)[1]
        )
        return markdown_table

    # 目录转为字典
    def extract_toc(self, toc):
        toc_dict: Dict[int, List[Dict[str, str]]] = {}
        title_stack: List[str] = []
        formatted_toc_block: str = ""

        for item in toc:
            page_num = item[2]
            page_index = page_num - 1
            title = self.clean_text(item[1])
            formatted_toc_block = f"{formatted_toc_block}{title}  {page_num}\n"
            level = item[0]
            while len(title_stack) >= level:
                title_stack.pop()
            title_stack.append(f'{'#' * level} {title}')

            toc_item = {
                "title": title,
                "full_title": "\n".join(title_stack),
            }

            if toc_dict.get(page_index):
                toc_dict[page_index].append(toc_item)
            else:
                toc_dict[page_index] = [toc_item]

        return formatted_toc_block, toc_dict

    def convert_pdf(self, pdf_path: str, output_path: str) -> str:
        result: str = ""
        doc = pymupdf.open(pdf_path)
        toc = doc.get_toc()
        formatted_toc_block, toc_dict = self.extract_toc(toc)

        # 从这页开始是正文内容
        body_content_start_page_index = toc[0][2] - 1

        # 处理每一页
        for page in doc:
            tables = page.find_tables()
            tables_range: List[TableRangeY] = []
            # 储存页面元素，用于文本和表格排序
            page_elements: List[Element] = []
            # 页码
            page_index = page.number
            for table in tables:
                # print(table.header.external)
                # print(table.to_markdown())
                tables_range.append({"y0": table.bbox[1], "y1": table.bbox[3]})
                page_elements.append(
                    {"type": "table", "content": table.extract(), "y0": table.bbox[1]}
                )
            page_toc = toc_dict.get(page_index)

            text_page = page.get_textpage()
            page_dict = text_page.extractDICT()
            # 处理页面每个块
            for block in page_dict["blocks"]:
                if block["type"] == 1:  # 图片格式不处理
                    continue
                block_x0 = block["bbox"][0]
                block_y0 = block["bbox"][1]
                block_y1 = block["bbox"][3]
                # 页眉页脚不处理
                if block_y1 < self.HEADER_Y1 or block_y0 > self.FOOTER_Y0:
                    continue
                if self.is_in_table_range(block_y0, tables_range):
                    continue
                block_lines = block["lines"]
                block_size = block_lines[0]["spans"][0]["size"]
                # 计算当前块缩进空格数
                space_count = int(block_x0 - self.NORMAL_LINE_LEFT) / block_size
                block_text = ""
                # 拼接块内所有行文本
                for line in block_lines:
                    spans = line["spans"]
                    block_text = self.clean_text(
                        block_text + " ".join([span["text"] for span in spans])
                    )
                if "目录" in block_text:
                    block_text = self.PREFFIX + block_text
                    self.has_toc_flag = True
                # 处理正文内容前面的页面
                if (
                    page_index <= body_content_start_page_index
                    and self.PATTERN_TOC_BLOCK.match(block_text)
                ):
                    if not self.meet_toc:
                        block_text = (
                            formatted_toc_block
                            if self.has_toc_flag
                            else self.PREFFIX + formatted_toc_block
                        )
                        self.meet_toc = True
                    else:
                        continue
                if (
                    space_count > 1
                    and space_count < 3
                    and block_size < self.SIZE_16
                    and block_size > self.SIZE_10
                ):
                    block_text = f"{self.PREFFIX}{block_text}"
                # 将正文目录标题替换为全标题
                if page_toc:
                    block_text = next(
                        (
                            toc_item["full_title"]
                            for toc_item in page_toc
                            if toc_item["title"] == block_text
                        ),
                        block_text,
                    )
                page_elements.append(
                    {"type": "text", "content": block_text, "y0": block_y0}
                )

            # 页面元素按 y0 排序
            page_elements.sort(key=lambda elem: elem["y0"])
            # 按元素类型拼接页面内容
            for elem in page_elements:
                if elem["type"] == "text":
                    result = result + elem["content"] + "\n"
                elif elem["type"] == "table":
                    markdown_table = elem["content"]
                    result = result + self.table2md(markdown_table) + "\n"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        return output_path


if __name__ == "__main__":
    cur_path = path.abspath(__file__)
    cur_dir = path.dirname(cur_path)

    input = path.join(cur_dir, "../samples/sample1.pdf")
    output = path.join(cur_dir, "../../../output/sample1.txt")
    pdf_converter = PDFConverter()
    pdf_converter.convert_pdf(input, output)
