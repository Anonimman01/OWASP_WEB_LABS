"""Shared helpers for the exploit tests.

Every lab ships two apps (``vulnerable/app.py`` and ``fixed/app.py``) that have
the same module names (``app``, ``labui``). To test them side by side we load
each ``app.py`` under a unique module name and put its folder on ``sys.path``
only while it is being imported (``from labui import ...`` needs that).

The module is re-imported for every test, so in-memory state (guestbook,
sqlite file, counters) never leaks from one test to another.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def load_lab(lab: str, variant: str):
    """Import ``<lab>/<variant>/app.py`` as a fresh module and return it."""
    folder = ROOT / lab / variant
    name = f"{lab}_{variant}_app".replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, folder / "app.py")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(folder))
    sys.modules.pop("labui", None)  # labui.py is copied into every lab
    sys.modules.pop("sky", None)    # ...and so is A05's sky.py (translations)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(folder))
        sys.modules.pop("labui", None)
        sys.modules.pop("sky", None)
    return module


def make_client_fixture(lab: str, variant: str):
    """Build a pytest fixture that yields a Flask test client for one variant."""

    @pytest.fixture
    def client():
        module = load_lab(lab, variant)
        module.app.config["TESTING"] = True
        with module.app.test_client() as c:
            yield c

    return client
