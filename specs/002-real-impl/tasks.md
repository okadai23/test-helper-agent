最高です。では、**Python**で実装前提・即手を動かせる粒度で、まず“並行・排他的に着手できる”4 タスクを切り出し、その**詳細タスク仕様（背景/入出力/IF/受け入れ基準/リスク）**と**実装サンプル**を提示します。
（以降の仕様やパス名は既存の設計/ドキュメントを踏まえています。ストレージ構成・CLI・依存はリポジトリの `specs/` と `docker-compose.yml` に明記済みです。ストレージ構成、CLI フローは research/quickstart に定義があります。 ）

---

# 先に実装できる 4 つのタスク（並行可）

## タスク A：Playwright MCP クライアント層の実装

**目的**
Agents からブラウザ操作を行う最小ツール面（navigate/click/fill/assert など）を MCP 経由で提供。既存 compose には Playwright MCP サービスが含まれ、標準ポート・環境が定義済み（`MCP_PORT=3001`）。**Quickstart とポート表記が食い違う（9000 vs 3001）ため設定で吸収**します。&#x20;

**背景情報**

-   Playwright MCP 採用方針・接続パターンは research に記載（MCP クライアント →PlaywrightServer 接続 → 関数ツール化）。
-   ストレージ/モデル/CLI の全体計画は research/plan/quickstart にあり、それと整合。&#x20;

**入出力**

-   入力：アクション（`navigate|click|fill|assert`）、セレクタ/ロール/テキストなど
-   出力：標準化**InteractionEvent**（trace 用）＋スクリーンショット（任意）

**公開 IF（Python）**

-   `test_helper/services/mcp_client.py`

    -   `class MCPClient:`

        -   `async connect(host: str, port: int) -> None`
        -   `async navigate(url: str) -> Event`
        -   `async click(selector_or_role: dict) -> Event`
        -   `async fill(selector: str, value: str) -> Event`
        -   `async assert_role(role: str, name: str|None) -> Event`

**受け入れ基準**

-   `docker-compose up` の MCP へ接続でき、`navigate('https://example.com')` が完了
-   返却イベントが Pydantic モデル（後述のタスク B で使う）に準拠

**実装サンプル（抜粋）**

```python
# src/test_helper/services/mcp_client.py
from __future__ import annotations
import asyncio
from typing import Any, Dict
from pydantic import BaseModel, Field
from test_helper.utils.settings import get_e2e_settings

class InteractionEvent(BaseModel):
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class MCPClient:
    def __init__(self) -> None:
        self._connected = False
        self._host = "localhost"
        self._port = 0

    async def connect(self, host: str | None = None, port: int | None = None) -> None:
        s = get_e2e_settings()
        # composeでは3001, quickstartでは9000 → 設定で統一
        self._host = host or "localhost"
        self._port = port or int(s.playwright_mcp_port)  # 例: settingsに追加
        # ここでMCPトランスポート確立（stdio or tcp）。擬似接続：
        await asyncio.sleep(0.01)
        self._connected = True

    async def navigate(self, url: str) -> InteractionEvent:
        assert self._connected
        # 実際には MCP の request を送る
        return InteractionEvent(type="navigate", payload={"url": url})

    async def click(self, selector: str | None = None, role: str | None = None, name: str | None = None) -> InteractionEvent:
        assert self._connected
        locator = {"selector": selector} if selector else {"role": role, "name": name}
        return InteractionEvent(type="click", payload=locator)

    async def fill(self, selector: str, value: str) -> InteractionEvent:
        assert self._connected
        return InteractionEvent(type="fill", payload={"selector": selector, "value": value})

    async def assert_role(self, role: str, name: str | None = None) -> InteractionEvent:
        assert self._connected
        return InteractionEvent(type="assert", payload={"role": role, "name": name})
```

> 参考：MCP 連携の全体方針（research の Integration Approach）
> 参考：compose での MCP サービス（ポート含む）

---

## タスク B：操作トレース →Playwright テストコード生成器

**目的**
タスク A が吐く標準化トレース `InteractionEvent[]` を **Playwright Test（TypeScript）** の `*.spec.ts` にコンパイル。\*\*locator 戦略（data-testid > role > text > css）\*\*と `test.step`/`expect` を付与。ストレージ構成に従い `data/projects/{id}/tests/` へ出力する想定。

**背景情報**

-   研究ドキュメントのストレージ構成に `tests/` `cache/captures.json` `selectors.json` が明記。
-   生成系は Phase 1 優先事項としても明記。

**入出力**

-   入力：`InteractionEvent[]`、オプション（テスト名、タイムアウト、アサーション方針）
-   出力：TS 文字列＋ファイル書き出しパス

**公開 IF**

-   `test_helper/services/generator_service.py`

    -   `def render_spec_ts(events: list[InteractionEvent], name: str) -> str`
    -   `def write_spec(project_id: str, name: str, code: str) -> str`

**受け入れ基準**

-   最低 `navigate/click/fill/assert` を TS へ正しくマッピング
-   生成ファイルを`quickstart`の例に準じた場所に配置できる（`data/projects/{id}/tests/`）

**実装サンプル（抜粋）**

```python
# src/test_helper/services/generator_service.py
from __future__ import annotations
from pathlib import Path
from typing import Iterable
from test_helper.services.mcp_client import InteractionEvent
from test_helper.utils.settings import get_e2e_settings

_LOCATOR_TS = """\
import { test, expect } from '@playwright/test';

test('{name}', async ({ page }) => {{
  {body}
}});
"""

def _to_locator(e: InteractionEvent) -> str:
    if "selector" in e.payload and e.payload["selector"]:
        return f"page.locator('{e.payload['selector']}')"
    if "role" in e.payload:
        name = e.payload.get("name")
        return f"page.getByRole('{e.payload['role']}'{', {{ name: ' + JSON.stringify(name) + ' }}' if name else ''})"
    return "page.locator('body')"

def render_spec_ts(events: Iterable[InteractionEvent], name: str) -> str:
    lines: list[str] = []
    for e in events:
        if e.type == "navigate":
            lines.append(f"await page.goto('{e.payload['url']}');")
        elif e.type == "click":
            lines.append(f"await {_to_locator(e)}.click();")
        elif e.type == "fill":
            lines.append(f"await page.fill('{e.payload['selector']}', '{e.payload['value']}');")
        elif e.type == "assert":
            lines.append(f"await expect({_to_locator(e)}).toBeVisible();")
    body = "\n  ".join(lines)
    return _LOCATOR_TS.format(name=name, body=body)

def write_spec(project_id: str, name: str, code: str) -> str:
    s = get_e2e_settings()
    base = Path(s.e2e_data_path) / "projects" / project_id / "tests"
    base.mkdir(parents=True, exist_ok=True)
    filename = base / f\"test_{name.replace(' ', '_').lower()}.spec.ts\"
    filename.write_text(code, encoding='utf-8')
    return str(filename)
```

> 参考：保管パス構成（research の Storage Structure）

---

## タスク C：Temporal ワークフロー骨格＋ WorkflowClient の配線

**目的**
**準備 → キャプチャ → 生成**の最小ハッピーパスを**Temporal Workflow + Activities**に分割し、**未実装の `WorkflowClient.start_capture/start_generate`** を実装で置換。現状、ここは `NotImplementedError` のままなので最優先配線ポイント。&#x20;

**背景情報**

-   Temporal 採用・Activity 分離の設計は research の「Workflow Design」に明記。
-   compose で Temporal サーバ/UI が提供される。&#x20;

**入出力**

-   入力：`project_id`
-   出力：`capture_result`（簡易トレース）→`spec_code`（TS 文字列 or 出力パス）

**公開 IF**

-   `test_helper/services/temporal_workflows.py`

    -   Workflow: `E2ETestWorkflow.run(project_id: str) -> str`
    -   Activities: `capture_activity(project_id) -> list[InteractionEvent]` / `generate_activity(events) -> str`

-   `test_helper/services/workflow_client.py`

    -   `start_capture`/`start_generate` を Temporal クライアント実装で起動

**受け入れ基準**

-   Temporal に接続し、Workflow 開始 →Activities 実行 → 生成完了の一往復が通る
-   例外時にリトライが効く（Activity リトライ設定）

**実装サンプル（抜粋）**

```python
# src/test_helper/services/temporal_workflows.py
from __future__ import annotations
from datetime import timedelta
from temporalio import workflow, activity
from test_helper.services.mcp_client import MCPClient, InteractionEvent
from test_helper.services.generator_service import render_spec_ts

@activity.defn
async def capture_activity(project_id: str) -> list[InteractionEvent]:
    client = MCPClient()
    await client.connect()  # settingsでポート解決
    events = []
    events.append(await client.navigate("https://example.com"))
    events.append(await client.click(role="button", name="Get started"))
    return events

@activity.defn
async def generate_activity(events: list[InteractionEvent]) -> str:
    return render_spec_ts(events, name="smoke_flow")

@workflow.defn
class E2ETestWorkflow:
    @workflow.run
    async def run(self, project_id: str) -> str:
        evts = await workflow.execute_activity(
            capture_activity, project_id,
            start_to_close_timeout=timedelta(minutes=5),
        )
        code = await workflow.execute_activity(
            generate_activity, evts,
            start_to_close_timeout=timedelta(minutes=2),
        )
        return code
```

```python
# src/test_helper/services/workflow_client.py （置換版・抜粋）
from temporalio import Client
from test_helper.services.temporal_workflows import E2ETestWorkflow

class WorkflowClient:
    def __init__(self, impl: Client) -> None:
        self._impl = impl

    async def start_capture(self, *, project_id: str):
        # この例では capture+generate を単一Workflowで扱う
        return await self._impl.start_workflow(
            E2ETestWorkflow.run, project_id,
            id=f"e2e-{project_id}",
            task_queue="e2e-tq",
        )

    async def start_generate(self, *, capture_session: dict):
        # 将来的に分離したい場合のフック
        return await self._impl.start_workflow(
            E2ETestWorkflow.run, capture_session["project_id"],
            id=f"e2e-{capture_session['project_id']}",
            task_queue="e2e-tq",
        )
```

> 参考：未実装メソッド（現状 NotImplementedError）
> 参考：Workflow/Activities の構成（research）
> 参考：Temporal サービス（compose）

---

## タスク D：プロジェクト/ストレージ管理の下回り

**目的**
`data/projects/{project_id}/` 配下の **プロジェクト初期化・メタ管理・保存パス生成** を一元化（テスト生成/実行/レポートの置き場を固定化）。

**背景情報**

-   Quickstart の「Create project」「Generate/Execute」コマンドの出力先が具体化されているため、**そのレイアウトに揃える**。&#x20;
-   設定クラス（E2ESettings）にベースディレクトリや上限値・バックエンド切替がある（OpenAI モデル許可リスト、backend 切替）。

**入出力**

-   入力：`name/url/browser_config` 等
-   出力：`project_id`、`metadata.json` 作成、パス返却

**公開 IF**

-   `test_helper/storage/project_store.py`

    -   `def init_project(name: str, url: str, browser: str='chromium') -> dict`
    -   `def project_paths(project_id: str) -> dict`（tests/reports/cache/history/logs など）

**受け入れ基準**

-   `metadata.json`（Quickstart 例のキー群）を生成できる&#x20;
-   生成先ディレクトリの存在を保証

**実装サンプル（抜粋）**

```python
# src/test_helper/storage/project_store.py
from __future__ import annotations
import json, uuid
from pathlib import Path
from typing import Dict
from test_helper.utils.settings import get_e2e_settings

def project_root(project_id: str) -> Path:
    s = get_e2e_settings()
    return Path(s.e2e_data_path) / "projects" / project_id

def project_paths(project_id: str) -> Dict[str, Path]:
    root = project_root(project_id)
    paths = {
        "root": root,
        "tests": root / "tests",
        "cache": root / "cache",
        "reports": root / "reports",
        "history": root / "history",
        "logs": root / "logs",
    }
    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)
    return paths

def init_project(name: str, url: str, browser: str = "chromium") -> dict:
    project_id = str(uuid.uuid4())
    paths = project_paths(project_id)
    metadata = {
        "project": {
            "id": project_id,
            "name": name,
            "url": url,
            "browser_config": {"browser": browser, "headless": True, "viewport": {"width": 1280, "height": 720}},
        },
        "settings": {"auto_fix_confidence_threshold": 0.8, "max_retries": 3, "timeout_ms": 30000, "parallel_execution": True},
    }
    (paths["root"] / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {"project_id": project_id, "paths": {k: str(v) for k, v in paths.items()}}
```

> 参考：metadata.json 例（キー構造）
> 参考：ストレージ全体構成（tests/cache/history）

---

# すぐには並行できない“後続”タスク（抜粋）

-   **E**：Axe 連携と a11y レポート出力の実装（`@axe-core/playwright` を実行時に付加）
-   **F**：既存 E2E の自己修復（失敗ログ → ロケーター更新/待機調整 →PR 提案）
-   **G**：CLI コマンド（`test-helper e2e capture/generate/execute`）の Python 実装（現行 Quickstart の仕様に準拠）&#x20;
-   **H**：OpenAI Agents SDK 統合（tool 呼び出しで MCPClient を公開）。Allowed モデル/バックエンド切替は設定に準じる（`agent_backend`/`openai_model`）

---

# 補足（設定と整合性）

-   **ポート整合**：`docker-compose.yml` の MCP は 3001/TCP。Quickstart は 9000 と記述箇所あり（将来修正候補）。まずは**settings に `playwright_mcp_port` を追加**して吸収します。&#x20;
-   **モデル/バックエンド安全弁**：`E2ESettings.openai_model` の許可セット、`agent_backend/temporal_backend` の切替は既に定義済（検証器あり）。

---

## 次アクション（私が今すぐ出せること）

-   上記 4 ファイル（`mcp_client.py` / `generator_service.py` / `temporal_workflows.py` / `project_store.py`）の**完全版**をこのまま展開できます。
-   また、**4 つの AI Agent**（A〜D に 1 タスクずつ割当）で並行実装しやすいように、各タスクが**モジュール間で衝突しない**設計にしてあります（**A**=外部 I/O、**B**=純関数に近い生成、**C**=ワークフロー配線、**D**=ファイルシステム管理）。

必要ならこの 4 ファイルの**完成版コード**も、次のメッセージでまとめて貼ります。

以下の 4 タスクは、既存リポジトリをベースに最初に実装でき、かつ並行して進められる内容です。各タスクは互いに排他的で、後続タスクの基盤となります。

### タスク A：Playwright MCP クライアントの実装

**目的**：OpenAI Agents からブラウザ操作を行うための最小ツール層を提供し、`navigate`/`click`/`fill`/`assert` などの操作を Playwright MCP 経由で実行できるようにします。
**背景**：研究ドキュメントでは MCP サーバへの接続と function ツール化が推奨されています。`docker-compose.yml`で Playwright MCP サービスが定義され、ポート 3001 で公開されています。
**インターフェース**：`src/test_helper/services/mcp_client.py` に `MCPClient` クラスを実装し、`connect()`, `navigate(url)`, `click(selector|role)`, `fill(selector, value)`, `assert_role(role, name)` メソッドを用意します。返り値は標準化された `InteractionEvent`。
**サンプルコード**：

```python
class InteractionEvent(BaseModel):
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class MCPClient:
    async def connect(self, host: str = None, port: int = None) -> None:
        # MCPサーバへ接続

    async def navigate(self, url: str) -> InteractionEvent:
        return InteractionEvent(type="navigate", payload={"url": url})

    async def click(self, selector: str = None, role: str = None, name: str = None) -> InteractionEvent:
        locator = {"selector": selector} if selector else {"role": role, "name": name}
        return InteractionEvent(type="click", payload=locator)
    # fill() / assert_role() も同様
```

### タスク B：操作トレースから Playwright テストコード生成

**目的**：タスク A の`InteractionEvent`のリストを Playwright Test（TypeScript）の `*.spec.ts` に変換し、`tests` ディレクトリへ保存する。
**背景**：研究では階層型ストレージ構造が定義され、Quickstart では生成されたテストが`data/projects/<id>/tests/`に格納される。
**インターフェース**：`src/test_helper/services/generator_service.py` に `render_spec_ts(events, name)` と `write_spec(project_id, name, code)` を実装。
**サンプルコード**：

```python
def render_spec_ts(events: Iterable[InteractionEvent], name: str) -> str:
    lines = []
    for e in events:
        if e.type == "navigate":
            lines.append(f"await page.goto('{e.payload['url']}');")
        elif e.type == "click":
            lines.append(f"await page.locator('{e.payload['selector']}').click();")
        # fill/assert も同様
    body = "\n  ".join(lines)
    return f"import {{ test, expect }} from '@playwright/test';\\n\\ntest('{name}', async ({{ page }}) => {{\\n  {body}\\n}});"

def write_spec(project_id: str, name: str, code: str) -> str:
    base = Path(get_e2e_settings().e2e_data_path) / 'projects' / project_id / 'tests'
    base.mkdir(parents=True, exist_ok=True)
    filename = base / f"test_{name.replace(' ', '_').lower()}.spec.ts"
    filename.write_text(code)
    return str(filename)
```

### タスク C：Temporal ワークフロー骨格と WorkflowClient の実装

**目的**：準備 → キャプチャ → 生成の基本フローを Temporal Workflow と Activity に分割し、未実装の`WorkflowClient.start_capture`/`start_generate` を具体的に実装します。
**背景**：研究では Activity を分離したワークフロー構成が示されています。現状`WorkflowClient`は `NotImplementedError` を投げており、ここを置き換える必要があります。
**インターフェース**：

-   `src/test_helper/services/temporal_workflows.py` に `capture_activity`・`generate_activity`・`E2ETestWorkflow` を定義。
-   `src/test_helper/services/workflow_client.py` で Temporal クライアントを用いてワークフローを開始。
    **サンプルコード**：

```python
@activity.defn
async def capture_activity(project_id: str) -> list[InteractionEvent]:
    client = MCPClient()
    await client.connect()
    return [await client.navigate('https://example.com')]

@activity.defn
async def generate_activity(events: list[InteractionEvent]) -> str:
    return render_spec_ts(events, 'smoke_flow')

@workflow.defn
class E2ETestWorkflow:
    @workflow.run
    async def run(self, project_id: str) -> str:
        events = await workflow.execute_activity(capture_activity, project_id, ...)
        code = await workflow.execute_activity(generate_activity, events, ...)
        return code

class WorkflowClient:
    async def start_capture(self, *, project_id: str):
        return await self._impl.start_workflow(E2ETestWorkflow.run, project_id, id=f"e2e-{project_id}", task_queue="e2e-tq")
```

### タスク D：プロジェクトおよびストレージ管理

**目的**：`data/projects/<project_id>/` 以下のディレクトリと`metadata.json`の生成・管理を一元化し、他モジュールが依存するファイルパスを提供する。
**背景**：ストレージ構造（metadata, tests, cache, history）が research で規定されており、Quickstart でもプロジェクト作成時に初期化されることが示されています。
**インターフェース**：`src/test_helper/storage/project_store.py` に `init_project(name, url, browser)` と `project_paths(project_id)` を実装。
**サンプルコード**：

```python
def project_paths(project_id: str) -> Dict[str, Path]:
    root = Path(get_e2e_settings().e2e_data_path) / 'projects' / project_id
    paths = {'root': root, 'tests': root/'tests', 'cache': root/'cache', 'reports': root/'reports', 'history': root/'history', 'logs': root/'logs'}
    for p in paths.values(): p.mkdir(parents=True, exist_ok=True)
    return paths

def init_project(name: str, url: str, browser: str = 'chromium') -> dict:
    project_id = str(uuid.uuid4())
    paths = project_paths(project_id)
    metadata = {
        'project': {'id': project_id, 'name': name, 'url': url, 'browser_config': {'browser': browser, 'headless': True, 'viewport': {'width': 1280, 'height': 720}}},
        'settings': {'auto_fix_confidence_threshold': 0.8, 'max_retries': 3, 'timeout_ms': 30000, 'parallel_execution': True}
    }
    (paths['root'] / 'metadata.json').write_text(json.dumps(metadata, indent=2))
    return {'project_id': project_id, 'paths': {k: str(v) for k, v in paths.items()}}
```

---

これら 4 タスクは互いに独立して着手でき、A→B→C→D の順に依存関係が増える想定です。他の後続タスク（a11y レポート生成、テスト修復、CLI 実装、Agents SDK 統合など）は、これら基盤が整ってから進めることで効率的に開発できます。
