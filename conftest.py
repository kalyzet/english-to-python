"""Root conftest: make the repo importable and auto-mark tests by directory."""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from hypothesis import settings, HealthCheck

# Property tests spawn subprocesses / sleep by design; the 200ms default
# deadline is too tight for them (but a hang still fails within 5s).
settings.register_profile(
    "ttc",
    deadline=5000,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("ttc")


def pytest_collection_modifyitems(config, items):
    for item in items:
        path = str(getattr(item, "fspath", "") or item.path)
        if f"{os.sep}unit{os.sep}" in path:
            item.add_marker(pytest.mark.unit)
        elif f"{os.sep}property{os.sep}" in path:
            item.add_marker(pytest.mark.property)
        elif f"{os.sep}integration{os.sep}" in path:
            item.add_marker(pytest.mark.integration)
