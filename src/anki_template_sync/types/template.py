from __future__ import annotations
import os

from typing import NamedTuple, Optional


class Template(NamedTuple):
    id: int

    name: str

    question: str
    answer: str

    browser_question: str = ""
    browser_answer: str = ""

    browser_font_type: str = ""
    browser_font_size: int = 0

    default_deck_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict, folder: str) -> Template:
        with open(os.path.join(folder, data.get("frontFile", f"card_{data['id']}_front.html")), encoding="utf-8") as f:
            question = f.read()

        with open(os.path.join(folder, data.get("frontFile", f"card_{data['id']}_back.html")), encoding="utf-8") as f:
            answer = f.read()

        return Template(
            id=data["id"],
            name=data["name"],
            question=question,
            answer=answer,
        )

    def to_dict(self) -> dict:
        return {
            "ord": self.id - 1,
            "name": self.name,
            "qfmt": self.question,
            "afmt": self.answer,
            "bqfmt": self.browser_question,
            "bafmt": self.browser_answer,
            "bfont": self.browser_font_type,
            "bsize": self.browser_font_size,
            "did": self.default_deck_id,
        }
