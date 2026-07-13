from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "contracts" / "lexicon_v2.py").read_text(encoding="utf-8")
CLIENT = (ROOT / "app.js").read_text(encoding="utf-8")


def test_editorial_code_and_entry_edits_are_permissioned():
    assert "def _require_admin(" in SOURCE
    assert "def _require_editor(" in SOURCE
    assert "only_author_or_admin" in SOURCE


def test_open_challenge_or_appeal_blocks_finalization():
    assert "open_challenge_blocks_finalize" in SOURCE
    assert "open_appeal_blocks_finalize" in SOURCE


def test_accepted_review_revises_the_editorial_verdict():
    assert 'e["verdict"] = "rejected" if res["ruling"] == "accepted"' in SOURCE
    assert 'e["verdict"] = "published" if res["ruling"] == "granted"' in SOURCE


def test_client_exposes_citations_challenges_appeals_and_finalization():
    for method in ("create_entry", "add_citation", "submit_challenge", "submit_appeal", "finalize_entry"):
        assert method in CLIENT
