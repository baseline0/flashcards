"""The published site is the site/ folder and nothing else.

GitHub Pages uploads site/ as a whole, so content and internal docs must stay out of it. These checks read the
workflow as text and list the folder, so they need no YAML parser and no network."""

from flashcards.constants import REPO_ROOT

SITE = REPO_ROOT / "site"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "deploy-pages.yml"
PUBLISHED = {"index.html", ".nojekyll"}


def test_the_site_folder_holds_only_the_published_files() -> None:
    assert {path.name for path in SITE.iterdir()} == PUBLISHED


def test_the_workflow_uploads_only_the_site_folder() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "path: 'site'" in text
    assert "path: 'docs'" not in text


def test_the_workflow_runs_on_site_changes() -> None:
    assert "- 'site/**'" in WORKFLOW.read_text(encoding="utf-8")


def test_the_server_serves_the_site_folder_and_the_study_page() -> None:
    from flashcards.server.app import SITE_DIR, STUDY_PAGE

    assert SITE_DIR == SITE
    assert STUDY_PAGE.is_file()
    assert STUDY_PAGE.parent.parent.name == "server"
