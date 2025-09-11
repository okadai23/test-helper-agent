from __future__ import annotations

from pathlib import Path

from test_helper.services.fix_service import apply_patch, propose_fixes


def test_propose_fixes_extracts_selector_and_scores() -> None:
    log = """
    Error at step 1: selector '#submit' not found
    Timeout waiting for element
    """.strip()
    proposal = propose_fixes(log)
    assert proposal.confidence >= 0.8
    assert any(ch.get("old") == "#submit" for ch in proposal.changes)
    assert any("data-testid" in str(ch.get("new")) for ch in proposal.changes)


def test_apply_patch_writes_diff_and_updates_file(tmp_path: Path) -> None:
    spec = tmp_path / "sample.spec.ts"
    spec.write_text("await page.locator('#submit').click();\n", encoding="utf-8")
    proposal = propose_fixes("selector '#submit' not found")
    diff = apply_patch(spec, proposal)
    content = spec.read_text(encoding="utf-8")
    assert "data-testid" in content
    assert diff

