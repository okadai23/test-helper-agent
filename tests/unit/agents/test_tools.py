from __future__ import annotations

import asyncio

from test_helper.agents import tools


def test_emit_spec_and_patch(tmp_path_factory: callable) -> None:  # type: ignore[type-arg]
    tmp = tmp_path_factory()
    # Configure data path for write_spec via settings
    from test_helper.utils.settings import get_e2e_settings, reset_e2e_settings

    reset_e2e_settings()
    s = get_e2e_settings()
    s.e2e_data_path = tmp

    project_id = "p1"
    # write spec
    res = tools.emit_spec(project_id=project_id, name="Smoke", code="// code")
    assert res["path"].endswith(".spec.ts")

    # write patch next to it
    spec_rel = res["path"].split("/tests/")[-1]
    pr = tools.emit_patch(project_id=project_id, spec_rel_path=spec_rel, diff="---\n+++")
    assert pr["path"].endswith(".diff")


def test_browser_tools_return_event_dict(monkeypatch: object) -> None:  # type: ignore[type-arg]
    async def run() -> None:
        e1 = await tools.browser_navigate("https://example.com")
        assert e1.get("type") == "navigate"
        e2 = await tools.browser_click(selector="#id")
        assert e2.get("type") == "click"
        e3 = await tools.browser_fill("#user", "alice")
        assert e3.get("type") == "fill"

    asyncio.run(run())

