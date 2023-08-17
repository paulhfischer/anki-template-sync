from __future__ import annotations
from contextlib import contextmanager
import os
import subprocess
import tempfile
from typing import Generator
import json
from aqt import mw
from aqt.utils import showInfo

from anki_template_sync.types.note_type import NoteType

REPOSITORY_URL = "https://www.github.com/paulhfischer/anki-templates"

def _note_types(directory: str) -> Generator[NoteType, None, None]:
    for folder_name in os.listdir(directory):
        folder = os.path.join(directory, folder_name)

        if not os.path.isdir(folder):
            continue

        if os.path.basename(folder) in (".git", ):
            continue

        with open(os.path.join(folder, "model.json"), encoding="utf-8") as f:
            data = json.load(f)

        yield NoteType.from_dict(data, folder=folder)

def _update_or_create(note_type: NoteType) -> bool:
    existing_template = mw.col.models.by_name(note_type.name)

    note_type_dict = note_type.to_dict()

    if existing_template:
        note_type_dict["id"] = existing_template["id"]

        mw.col.models.save(note_type_dict)

        return False
    else:
        mw.col.models.add(note_type_dict)

        return True

@contextmanager
def _clone_repository(url: str) -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.check_call(('git', 'clone', url, tmpdir))

        yield tmpdir

def main() -> None:
    mw.checkpoint("Update Templates")
    mw.progress.start()

    num_updated = 0
    num_created = 0

    with _clone_repository(REPOSITORY_URL) as models_dir:
        for note_type in _note_types(models_dir):
            created = _update_or_create(note_type)

            if created:
                num_created += 1
            else:
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
        showInfo(f"Updated {num_updated} {updated_string} and added {num_created} new {created_string}!")
