from __future__ import annotations

import os
from typing import Literal
from typing import NamedTuple

from anki_template_sync.types.field import Field
from anki_template_sync.types.template import Template


class NoteType(NamedTuple):
    name: str

    css: str

    fields: list[Field]
    sort_field_id: int

    templates: list[Template]

    type: Literal["normal", "cloze"]

    latex_pre: str
    latex_post: str
    latex_svg: bool = True

    id: int = 0
    modification_time: int = 0
    update_sequence_number: int = 0
    default_deck_id: int | None = None
    required_fields: list = []
    original_stock_kind: int = 1

    @classmethod
    def from_dict(cls, data: dict, folder: str) -> NoteType:
        with open(os.path.join(folder, data.get("cssFile", "style.css")), encoding="utf-8") as f:
            css = f.read()

        fields = [Field.from_dict(field) for field in data["fields"]]

        templates = [Template.from_dict(template, folder=folder) for template in data["templates"]]

        return NoteType(
            name=data["name"],
            css=css,
            fields=fields,
            sort_field_id=data["sortFieldID"],
            templates=templates,
            type=data["type"],
            latex_pre=data.get("latexPre", ""),
            latex_post=data.get("latexPost", ""),
        )

    def to_dict(self) -> dict:
        fields = [field.to_dict() for field in self.fields]

        templates = [template.to_dict() for template in self.templates]

        type = {
            "normal": 0,
            "cloze": 1,
        }[self.type]

        return {
            "name": self.name,
            "css": self.css,
            "flds": fields,
            "sortf": self.sort_field_id - 1,
            "tmpls": templates,
            "type": type,
            "latexPre": self.latex_pre,
            "latexPost": self.latex_post,
            "latexsvg": self.latex_svg,
            "id": self.id,
            "mod": self.modification_time,
            "usn": self.update_sequence_number,
            "did": self.default_deck_id,
            "req": self.required_fields,
            "originalStockKind": self.original_stock_kind,
        }
