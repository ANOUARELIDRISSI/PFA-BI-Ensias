from __future__ import annotations

import app
from streamlit.testing.v1 import AppTest


def test_streamlit_app_imports_and_has_svg_icons() -> None:
    assert callable(app.main)
    assert app.ICONS
    assert all("<svg" in value and "</svg>" in value for value in app.ICONS.values())


def test_streamlit_app_renders_without_exception() -> None:
    rendered = AppTest.from_file("app.py").run(timeout=30)
    assert not rendered.exception
    assert rendered.title or rendered.markdown
    assert [tab.label for tab in rendered.tabs] == [
        "Estimation",
        "Recommandations",
        "Comparateur",
        "Marche",
        "Modele ML",
        "Insights",
        "Collecte",
        "Recherche en ligne",
        "Agent IA",
    ]
