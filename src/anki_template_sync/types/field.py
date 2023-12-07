from __future__ import annotations

from typing import NamedTuple


class Field(NamedTuple):
    id: int

    name: str
    description: str

    exclude_from_search: bool

    collapsed: bool

    sticky: bool = False

    font_type: str = "Verdana"
    font_size: int = 20
    rtl: bool = False
    plain_text: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> Field:
        return Field(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            exclude_from_search=data.get("excludeFromSearch", False),
            collapsed=data.get("collapsed", False),
        )

    def to_dict(self) -> dict:
        return {
            "ord": self.id - 1,
            "name": self.name,
            "description": self.description,
            "excludeFromSearch": self.exclude_from_search,
            "sticky": self.sticky,
            "collapsed": self.collapsed,
            "font": self.font_type,
            "size": self.font_size,
            "rtl": self.rtl,
            "plainText": self.plain_text,
        }
