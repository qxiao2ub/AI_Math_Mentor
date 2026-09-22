from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


def test_home_page_runs_without_exception():
    app = AppTest.from_file(str(APP), default_timeout=60)
    app.run()
    assert not app.exception


def test_all_navigation_pages_render():
    app = AppTest.from_file(str(APP), default_timeout=60)
    app.run()
    assert not app.exception

    for page in ["Analyze", "Mastery", "About", "Settings", "Home"]:
        app.radio[0].set_value(page)
        app.run()
        assert not app.exception, f"{page} page raised an exception"
