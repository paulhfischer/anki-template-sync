from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Generator
from contextlib import contextmanager
from typing import Literal

from aqt import mw
from aqt.utils import showInfo

from anki_template_sync.types.note_type import NoteType

REPOSITORY_URL = "https://www.github.com/paulhfischer/anki-templates"


def _note_types(directory: str) -> Generator[NoteType, None, None]:
    for folder_name in os.listdir(directory):
        folder = os.path.join(directory, folder_name)

        if not os.path.isdir(folder):
            continue

        if os.path.basename(folder) in (".git",):
            continue

        with open(os.path.join(folder, "model.json"), encoding="utf-8") as f:
            data = json.load(f)

        yield NoteType.from_dict(data, folder=folder)


def _is_different(old: dict, new: dict) -> bool:
    for key in ("name", "css", "sortf", "type", "latexPre", "latexPost", "latexsvg", "did"):
        if new[key] != old[key]:
            return True

    if len(new["flds"]) != len(old["flds"]):
        return True
    for new_field in new["flds"]:
        old_field = next(field for field in old["flds"] if field["ord"] == new_field["ord"])

        for key in (
            "name",
            "description",
            "excludeFromSearch",
            "sticky",
            "collapsed",
            "font",
            "size",
            "rtl",
            "plainText",
        ):
            if new_field[key] != old_field[key]:
                return True

    if len(new["tmpls"]) != len(old["tmpls"]):
        return True
    for new_template in new["tmpls"]:
        old_template = next(
            template for template in old["tmpls"] if template["ord"] == new_template["ord"]
        )

        for key in ("name", "qfmt", "afmt", "bqfmt", "bafmt", "bfont", "bsize", "did"):
            if new_template[key] != old_template[key]:
                return True

    return False


def _update_or_create(note_type: NoteType) -> Literal["update", "create", "skip"]:
    existing_template = mw.col.models.by_name(note_type.name)

    note_type_dict = note_type.to_dict()

    if existing_template:
        note_type_dict["id"] = existing_template["id"]

        if not _is_different(existing_template, note_type_dict):
            return "skip"

        mw.col.models.save(note_type_dict)

        return "update"
    else:
        mw.col.models.add(note_type_dict)

        return "create"


@contextmanager
def _empty_template_directory() -> Generator[str, None, None]:
    addons_path = mw.addonManager.addonsFolder()
    userfiles_path = os.path.join(addons_path, "user_files")
    templates_path = os.path.join(userfiles_path, "templates")

    if os.path.exists(templates_path):
        shutil.rmtree(templates_path)
    os.makedirs(templates_path)

    yield templates_path


def _clone_repository(url: str, directory: str) -> None:
    subprocess.check_call(("git", "clone", url, directory))


def main() -> None:
    mw.checkpoint("Update Templates")
    mw.progress.start()

    num_updated = 0
    num_created = 0

    with _empty_template_directory() as models_dir:
        _clone_repository(REPOSITORY_URL, models_dir)

        for note_type in _note_types(models_dir):
            operation = _update_or_create(note_type)

            if operation == "create":
                num_created += 1
            elif operation == "update":
                num_updated += 1

    mw.progress.finish()
    mw.reset()

    updated_string = "templates" if num_updated > 1 else "template"
    created_string = "templates" if num_created > 1 else "template"

    if num_created == 0:
        showInfo(f"Updated {num_updated} {updated_string}!")
    elif num_updated == 0:
        showInfo(f"Added {num_created} new {created_string}!")
    else:
        showInfo(
            f"Updated {num_updated} {updated_string} and added {num_created} new {created_string}!",
        )
