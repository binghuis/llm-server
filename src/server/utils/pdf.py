import re
from os import path
from pprint import pprint
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup
from langchain_community.docstore.document import Document
from langchain_community.document_loaders import PDFMinerPDFasHTMLLoader

cur_path = path.abspath(__file__)

cur_dir = path.dirname(cur_path)

abs_cur_path = path.join(cur_dir, "../docs/test.pdf")

loader = PDFMinerPDFasHTMLLoader(abs_cur_path)

data = loader.load()[0]

soup = BeautifulSoup(data.page_content, "lxml")

content = soup.find_all("div")

cur_fs: Optional[int] = None
cur_text: str = ""
snippets: List[Tuple[str, int | None]] = []
for c in content:
    sp = c.find("span")
    if not sp:
        continue
    st = sp.get("style")
    if not st:
        continue
    fs_match = re.findall(r"font-size:(\d+)px", st)
    if not fs_match:
        continue
    fs = int(fs_match[0])
    if not cur_fs:
        cur_fs = fs
    if fs == cur_fs:
        cur_text += c.text
    else:
        snippets.append((cur_text, cur_fs))
        cur_fs = fs
        cur_text = c.text
snippets.append((cur_text, cur_fs))

cur_idx = -1
semantic_snippets: List[Document] = []
# Assumption: headings have higher font size than their respective content
for s in snippets:
    # if current snippet's font size > previous section's heading => it is a new heading
    if (
        not semantic_snippets
        or s[1] > semantic_snippets[cur_idx].metadata["heading_font"]
    ):
        metadata = {"heading": s[0], "content_font": 0, "heading_font": s[1]}
        metadata.update(data.metadata)
        semantic_snippets.append(Document(page_content="", metadata=metadata))
        cur_idx += 1
        continue

    # if current snippet's font size <= previous section's content => content belongs to the same section (one can also create
    # a tree like structure for sub sections if needed but that may require some more thinking and may be data specific)
    if (
        not semantic_snippets[cur_idx].metadata["content_font"]
        or s[1] <= semantic_snippets[cur_idx].metadata["content_font"]
    ):
        semantic_snippets[cur_idx].page_content += s[0]
        semantic_snippets[cur_idx].metadata["content_font"] = max(
            s[1], semantic_snippets[cur_idx].metadata["content_font"]
        )
        continue

    # if current snippet's font size > previous section's content but less than previous section's heading than also make a new
    # section (e.g. title of a PDF will have the highest font size but we don't want it to subsume all sections)
    metadata = {"heading": s[0], "content_font": 0, "heading_font": s[1]}
    metadata.update(data.metadata)
    semantic_snippets.append(Document(page_content="", metadata=metadata))
    cur_idx += 1

pprint(semantic_snippets)
