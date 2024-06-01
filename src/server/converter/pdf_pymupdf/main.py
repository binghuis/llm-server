from os import path
from typing import Dict, List, Literal, Optional

import pymupdf
import regex as re
from server.converter.pdf_pymupdf.type import Element, PagePaddingType, TableElement
from server.converter.pdf_pymupdf.utils import clean_text, is_markdown

"""
功能：
- 识别表格生成 markdown 表格 ✅
- 识别正文自然段，添加自然段前缀 ✅
- 忽略图片 ✅
- 忽略页眉页脚 ✅
- 正文标题替换为完整层级标题 ✅
- 格式化文本，删除多余空格 ✅

pymupdf 问题：
1. get_toc(simple=False) 
目录页码是根据文档内容生成的，和你自己写的目录没有关系。
2. table to_markdown() 会把 table 外文本提取为表头。
3. find_tables() 很多表无法识别，目前没找到规律。
"""


# 坐标相关文档
# https://pymupdf.readthedocs.io/en/latest/app3.html#origin-point-point-size-and-y-axis


# 字号
FONT_XXS = 10
FONT_XS = 12
FONT_SM = 14
FONT_BASE = 16
FONT_LG = 18
# 字号预期偏移量
FONT_OFFSET = 0.5


# 主要文本：字号 10 - 14，偏移字号为 10 - 14.5
def is_primary_text(size: float) -> bool:
    return FONT_XXS < size < FONT_SM + FONT_OFFSET


# 噪音文本：字号小于 10 为噪音文本
# 包括页眉页脚、图片标题等
def is_noise_text(size: float) -> bool:
    return size <= FONT_XXS


# 换行符
NEW_LINE_CHAR = "\n"
# 自然段标识前缀
PARAGRAPH_PREFFIX = "$$$"
TITLE_PREFFIX = "###"
MD_NEW_LINE_CHAR = "  \n"
MD_PARAGRAPH_PREFFIX_PREFFIX = ""
TOC_FLAG = "$$TOC_FLAG$$"


# 匹配目录块
PATTERN_TOC_BLOCK = re.compile(
    r"^(\p{Nd}*(?:.\p{Nd})*)\p{Z}*([\p{Han}\p{Latin}\p{Nd}\p{Z}\p{P}]*?)[-\.]{3,}([\p{Han}\p{Nd}！。]+?)$",
    re.MULTILINE,
)


class PDFConverter:
    def __init__(self):
        # 是否开始处理目录
        self.has_meet_toc = False
        self.new_line_char = NEW_LINE_CHAR
        self.paragraph_preffix = PARAGRAPH_PREFFIX
        self.title_preffix = TITLE_PREFFIX
        self.page_padding: PagePaddingType = None
        self.toc = []
        self.body_content_start_page_index = None
        self.toc_dict = {}

    # 判断块坐标是否在表格范围内
    def is_block_in_table(
        self, y0: float, y1: float, tables: List[TableElement]
    ) -> bool:
        return any(range["y0"] <= y0 and y1 <= range["y1"] for range in tables)

    def find_img_by_block_number(self, images, block_numbers: List[int]):
        for block_number in block_numbers:
            if any(img["number"] == block_number for img in images):
                return True
        return None

    def compute_page_padding(self, page: pymupdf.Page) -> PagePaddingType:
        page_rect = page.rect
        bbox_list = page.get_bboxlog()
        if len(bbox_list) == 0:
            return None
        first_bbox_rect = bbox_list[0][1]
        last_bbox_rect = bbox_list[len(bbox_list) - 1][1]
        container_rect = [
            first_bbox_rect[0],
            first_bbox_rect[1],
            last_bbox_rect[2],
            last_bbox_rect[3],
        ]
        for bbox in bbox_list[1:-1]:
            bbox_rect = bbox[1]
            if bbox_rect[0] < container_rect[0]:
                container_rect[0] = bbox_rect[0]
            if bbox_rect[2] > container_rect[2]:
                container_rect[2] = bbox_rect[2]
        result: Dict[Literal["pl", "pt", "pr", "pb"], float] = {
            "pl": container_rect[0],
            "pt": container_rect[1],
            "pr": page_rect[2] - container_rect[2],
            "pb": page_rect[3] - container_rect[3],
        }

        return result

    def table2md(self, table: List[List[Optional[str]]]) -> str:
        if not table or len(table) < 2:
            return ""
        table_md = ""
        for row in table:
            table_md += (
                "| "
                + " | ".join(clean_text(cell) for cell in row)
                + f" |{self.new_line_char}"
            )
        header_sep = (
            "| " + " | ".join("---" for _ in table[0]) + f" |{self.new_line_char}"
        )
        table_md = (
            table_md.split(self.new_line_char, 1)[0]
            + self.new_line_char
            + header_sep
            + table_md.split(self.new_line_char, 1)[1]
        )
        return table_md

    # 目录转为字典
    def process_toc(self, toc):
        formatted_toc = [
            toc_item
            for toc_item in toc
            if toc_item[1] and re.match(r"\p{Nd}+", toc_item[2])
        ]
        if len(toc) == 0:
            return "", None
        toc_dict: Dict[int, List[Dict[str, str]]] = {}
        title_stack: List[str] = []
        formatted_toc_block: str = ""

        for item in formatted_toc:
            page_num = int(item[2])
            page_index = (
                page_num + self.body_content_start_page_index
                if self.body_content_start_page_index
                else page_num
            )
            title = clean_text(f"{item[0]} {item[1]}")
            formatted_toc_block = f"{formatted_toc_block}{self.paragraph_preffix}{title}{self.new_line_char}"
            level = len(item[0].split("."))
            while len(title_stack) >= level:
                title_stack.pop()
            title_stack.append(f"{title}")

            toc_item = {
                "title": title,
                "full_title": "-".join(title_stack),
            }

            if toc_dict.get(page_index):
                toc_dict[page_index].append(toc_item)
            else:
                toc_dict[page_index] = [toc_item]

        return formatted_toc_block, toc_dict

    def convert_pdf(self, pdf_path: str, output_path: str) -> str:
        if is_markdown(output_path):
            self.new_line_char = MD_NEW_LINE_CHAR
            self.paragraph_preffix = MD_PARAGRAPH_PREFFIX_PREFFIX

        doc = pymupdf.open(pdf_path)

        result: str = ""

        for page in doc:
            self.page_padding = self.compute_page_padding(page)
            if not self.page_padding:
                continue
            page_index = page.number
            text_page = page.get_textpage()
            text_dict = text_page.extractDICT()
            imgs = page.get_image_info()
            tables = page.find_tables()
            # 储存页面元素，用于文本和表格排序
            page_elements: List[Element] = []
            # 页码
            for table in tables:
                # print(table.header.external)
                # print(table.to_markdown())
                if len(table.extract()) > 1:
                    page_elements.append(
                        {
                            "type": "table",
                            "content": table.extract(),
                            "y0": table.bbox[1],
                            "y1": table.bbox[3],
                        }
                    )
            table_elements = [
                element for element in page_elements if element["type"] == "table"
            ]
            page_toc = (
                self.toc_dict.get(page_index)
                if (
                    self.body_content_start_page_index
                    and page_index >= self.body_content_start_page_index
                )
                else None
            )
            # 处理页面每个块
            for block in text_dict["blocks"]:
                block_x0 = block["bbox"][0]
                block_y0 = block["bbox"][1]
                block_y1 = block["bbox"][3]
                block_lines = block["lines"]
                block_number = block["number"]
                block_size = block_lines[0]["spans"][0]["size"]
                page_mid = page.rect[2] / 2
                # 计算当前块缩进空格数
                space_count = int(block_x0 - self.page_padding["pl"]) / block_size
                block_text = ""
                if is_noise_text(block_size):
                    continue
                # 拼接块内所有行文本
                for line in block_lines:
                    spans = line["spans"]
                    block_text = clean_text(
                        block_text + " ".join([span["text"] for span in spans])
                    )
                if not block_text:
                    continue
                if (
                    self.body_content_start_page_index
                    and page_index < self.body_content_start_page_index
                ):
                    # 将正文目录标题替换为全标题
                    if page_toc:
                        block_text = next(
                            (
                                toc["full_title"]
                                for toc in page_toc
                                if toc["title"] == block_text
                            ),
                            block_text,
                        )
                else:
                    if self.is_block_in_table(block_y0, block_y1, table_elements):
                        continue

                    if is_primary_text(block_size):
                        if space_count > 1.8 and space_count < 2.5:
                            block_text = f"{self.paragraph_preffix}{block_text}"
                        if space_count > 3 and block_x0 <= page_mid:
                            if self.find_img_by_block_number(
                                imgs, [block_number - 1, block_number]
                            ):
                                continue
                            else:
                                block_text = f"{self.title_preffix}{block_text}"

                page_elements.append(
                    {"type": "text", "content": block_text, "y0": block_y0}
                )
            # 页面元素按 y0 排序
            page_elements.sort(key=lambda elem: elem["y0"])
            cur_page_has_toc = False
            for elem in page_elements:
                if elem["type"] == "text":
                    toc_match = (
                        PATTERN_TOC_BLOCK.match(elem["content"])
                        if not self.body_content_start_page_index
                        else None
                    )
                    if toc_match:
                        cur_page_has_toc = True
                        self.toc.append(toc_match.groups())
                        if not self.has_meet_toc:
                            result = result + "$$TOC_FLAG$$" + self.new_line_char
                            self.has_meet_toc = True
                    else:
                        result = result + elem["content"] + self.new_line_char
                elif elem["type"] == "table":
                    markdown_table = self.table2md(elem["content"])
                    result = result + markdown_table + self.new_line_char
            if (
                self.has_meet_toc
                and not cur_page_has_toc
                and not self.body_content_start_page_index
            ):
                self.body_content_start_page_index = page_index
                formatted_toc_block, self.toc_dict = self.process_toc(self.toc)
                result = result.replace(TOC_FLAG, formatted_toc_block)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        return output_path


if __name__ == "__main__":
    cur_path = path.abspath(__file__)
    cur_dir = path.dirname(cur_path)
    input = path.join(cur_dir, "../../samples/sample1.pdf")
    output = path.join(cur_dir, "../../samples/output/sample1.txt")
    pdf_converter = PDFConverter()
    pdf_converter.convert_pdf(input, output)
