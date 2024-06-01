from typing import Dict, List, Literal, TypedDict, Union


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
    y1: float


Element = Union[TextElement, TableElement]

PagePaddingType = Dict[Literal["pl", "pt", "pr", "pb"], float] | None
