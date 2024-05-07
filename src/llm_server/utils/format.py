from typing import Literal, Optional, Union


def format_event_data(
    event: Literal["add", "end"], count: Union[int, str], data: Optional[str] = ""
):
    if event == "add":
        return f"event: add\ndata: {data}\nid: {count}\n\n"
    else:
        return f"event: end\nid: {count}\n\n"
