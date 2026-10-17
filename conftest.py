"""Root conftest: make the repo importable and auto-mark tests by directory."""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest


def pytest_collection_modifyitems(config, items):
    for item in items:
        path = str(getattr(item, "fspath", "") or item.path)
        if f"{os.sep}unit{os.sep}" in path:
            item.add_marker(pytest.mark.unit)
        elif f"{os.sep}property{os.sep}" in path:
            item.add_marker(pytest.mark.property)
        elif f"{os.sep}integration{os.sep}" in path:
            item.add_marker(pytest.mark.integration)
