
from __future__ import annotations
from aqt import mw

from anki_template_sync.main import main

def setup_menu():
    update_action = mw.form.menuTools.addAction("Update Templates")
    update_action.triggered.connect(main)

setup_menu()
