やった！A〜D まで着手済みとのことなので、最新のリポジトリ構成（研究・計画・テスト用フィクスチャ/クイックスタートなど）を踏まえて、**後続タスクを再整理**し、\*\*実装仕様書（背景・IF・入出力・受け入れ基準・リスク・実装サンプル）\*\*を提示します。
※ストレージ/ワークフロー/MCP は既存の設計に明記されています（ストレージ構造、ワークフロー方針、MCP 接続方針、CLI の入出力例など）。必要箇所に引用を付けています。

---

# まず把握しておく現状（確認ポイント）

-   研究ドキュメント：OpenAI Agents SDK ＋ Temporal ＋ Playwright MCP の方針・実装パターン・ストレージ構造が整理済み【】【】【】
-   ストレージ構造：`data/projects/{id}/` 配下に `metadata.json`/`tests/`/`cache/`/`history/` を格納する設計【】
-   Docker Compose：Temporal と MCP コンテナがあり、**MCP は 3001/TCP**で公開【】
-   Quickstart：CLI の入出力例は `data/projects/<id>/tests/` に生成物を置く想定（**例示の MCP ポートは 9000 記載**なので設定値で吸収/統一が必要）【】【】
-   tests/conftest.py：E2E 関連のフィクスチャがあり、テストデータ・メタ・モック I/F の形が示されている（今後のユニット/統合テスト方針の足場になる）【】【】

---

# 後続タスクの再整理（ロードマップ）

優先度高から順に。**上段の 4 つ（E〜H）は“並行・排他的”に進められるよう、依存を分離**しています。

1. **E. a11y 自動検査（axe-core）統合 & レポート添付**
2. **F. 自己修復（ロケーター更新/待機調整/差分パッチ）**
3. **G. CLI コマンド群（project/capture/generate/execute/fix）の実装**
4. **H. OpenAI Agents SDK オーケストレーション（最終出力ツール/ループ制御）**

以降、**先行 4 タスクの上に載せる**発展（こちらは後回し OK）：

-   I. ブラックボックス探索の強化（サイトマップ探索・代表フロー抽出）
-   J. ホワイトボックス解析（ルーティング/`data-testid`抽出・優先度付け）
-   K. レポート統合（HTML/JSON ＋スクショ/動画＋ a11y 結果）とダッシュボード
-   L. CI/CD（GitHub Actions）と PR ボット（結果/差分/アドバイス投稿）
-   M. ワークフローバージョニング/強靭化（リトライ方針・検知メトリクス）
-   N. セキュリティ・サンドボックス（URL/パス検証・分離コンテキストなど）【】

---

# 後続タスクの実装仕様書（E〜H：並行で着手可）

## タスク E：a11y 自動検査統合（axe-core）とレポート出力

### 背景

-   研究・計画ではストレージ/レポート箇所が予め想定されており、ここに a11y 結果（JSON/HTML）を添付すると「１か所で完結」できます【】。
-   セキュリティ/隔離、URL 検証等の基本ガードも併せて適用（研究のセキュリティ考慮）【】。

### 目的/効果

-   Playwright 実行時に `@axe-core/playwright` を呼び出し、**WCAG タグ**（例：`wcag2a`, `wcag2aa`, `wcag21aa`）で検査。
-   結果を `reports/{executionId}/a11y.json` と `a11y.html` に保存（後の K タスクでダッシュボードに集約）。

### 追加する主なファイル

-   `src/test_helper/services/executor_service.py`（Playwright 実行に a11y スキャンを組み込み）
-   `src/test_helper/reporters/a11y_reporter.py`（JSON/HTML 生成器）

### IF / 入出力

-   入力：`project_id`, `spec_paths: list[str]`, 実行オプション（並列数/タイムアウト）
-   出力：`ExecutionResult`（各 spec の pass/fail, a11y 結果パス, スクショ/動画パス）
-   保存先：`data/projects/{id}/reports/{executionId}/`

### 受け入れ基準

-   a11y スキャンが **ON/OFF 切替可能**（設定値）
-   規定タグの違反があれば結果 JSON に**ルール ID/影響度/対象ノード**が記録される
-   実行失敗時もレポートフォルダが残る（失敗要因の調査が可能）

### 実装サンプル（Python 呼び出し側）

```python
# executor_service.py（抜粋）
from pathlib import Path
import json, subprocess
from test_helper.storage.project_store import project_paths

def run_playwright_with_a11y(project_id: str, specs: list[str]) -> dict:
    paths = project_paths(project_id)
    run_id = "exec-001"  # 実装ではUUID
    out_dir = Path(paths["reports"]) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Playwright実行（--reporter html,line など好みで）
    subprocess.run(["npx", "playwright", "test", *specs, "--reporter", "list"], check=False)

    # 2) 実行後にa11yスキャン（node側で a11y スクリプトを用意し叩く）
    a11y_json = out_dir / "a11y.json"
    subprocess.run(["node", "scripts/a11y_scan.mjs", str(out_dir)], check=False)

    # 3) 結果集約（簡易例）
    result = {"run_id": run_id, "reports_dir": str(out_dir)}
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
```

> 保存レイアウトは既定のストレージ構造に沿う【】。

---

## タスク F：自己修復（ロケーター更新/待機調整/差分パッチ提案）

### 背景

-   研究ドキュメントの「Known Challenges」で、ロケーター安定性やスマートウェイト等が課題として挙げられている（＝本タスクの主眼）【】【】。
-   `tests/conftest.py` に**修復提案**データの形（`fix_proposal`）があり、これをモデル化/適用の出発点にできる【】。

### 目的/効果

-   失敗ログやスクリーンショットから「候補ロケーター（`data-testid` > role > text > CSS）」に自動置換、`diff` を生成し PR 用パッチ出力（後の L タスクで PR 連携）。

### 追加する主なファイル

-   `src/test_helper/services/fix_service.py`（ログ解析 → 修復提案 → パッチ）
-   `src/test_helper/models/fix_proposal.py`（Pydantic）

### IF / 入出力

-   入力：`execution_artifacts`（logs/trace/screenshot）, `spec_path`
-   出力：`FixProposal`（変更点/信頼度/影響範囲/自動適用可否）, `patch.diff`

### 受け入れ基準

-   ロケーター不一致系エラー（timeout / element not found）で**代替ロケーターを最低 1 つ**提示
-   信頼度スコア（0-1）を付け、**しきい値以上なら自動適用**
-   パッチ適用後に再実行 → 成功なら修復確定（リグレッションがないこと）

### 実装サンプル（抜粋）

```python
# fix_service.py（抜粋）
from __future__ import annotations
import re, difflib, json
from pathlib import Path
from pydantic import BaseModel, Field

class FixProposal(BaseModel):
    confidence: float
    changes: list[dict]
    rationale: str

def propose_locator_fix(log_text: str) -> FixProposal:
    # ざっくり：#id → [data-testid=...] などの代替候補を合成
    candidates = []
    for m in re.finditer(r"selector '([^']+)' not found", log_text):
        old = m.group(1)
        # ダミー候補：本実装ではDOMスナップショット/role/テキストも見る
        candidates.append({"field": "selector", "old_value": old, "new_value": f\"[data-testid='{old.strip('#')}']\"})
    conf = 0.85 if candidates else 0.0
    return FixProposal(confidence=conf, changes=candidates, rationale="Selector fallback")

def apply_patch(spec_path: Path, proposal: FixProposal) -> str:
    original = spec_path.read_text(encoding="utf-8")
    patched = original
    for ch in proposal.changes:
        if ch["field"] == "selector":
            patched = patched.replace(ch["old_value"], ch["new_value"])
    diff = "\n".join(difflib.unified_diff(original.splitlines(), patched.splitlines(), fromfile="a", tofile="b"))
    (spec_path).write_text(patched, encoding="utf-8")
    return diff
```

---

## タスク G：CLI コマンド実装（project/capture/generate/execute/fix）

### 背景

-   Quickstart の利用導線がすでに定義されており（`project create` → `capture start/stop` → `generate` → `execute` → `fix`）、CLI はこの形に沿って作るのが最短です【】【】【】【】。

### 目的/効果

-   `typer` ベースの CLI を `test-helper` として提供、A〜F の機能をワンコマンドで操作可能に。

### 追加する主なファイル

-   `src/test_helper/cli/__init__.py` / `main.py`
-   サブコマンド：`project`, `capture`, `generate`, `execute`, `fix`

### IF / 入出力（例）

-   `test-helper e2e project create --name "...“ --url "..."` → `project_id` と格納先を標準出力【】
-   `test-helper e2e capture start --project <id> --headed` → ブラウザ起動、停止で `session_id`
-   `test-helper e2e generate --project <id> --session <sid>` → `*.spec.ts` 生成【】
-   `test-helper e2e execute --project <id> --all` → HTML/JSON レポートを出力【】
-   `test-helper e2e fix --project <id> --auto-apply` → パッチ適用＆再実行【】

### 受け入れ基準

-   既存 Quickstart の出力例に**ほぼ一致**する標準出力とファイル生成
-   失敗時は非 0 終了コード・分かりやすいメッセージ

### 実装サンプル（抜粋）

```python
# src/test_helper/cli/main.py
import typer
from test_helper.storage.project_store import init_project
from test_helper.services.generator_service import write_spec, render_spec_ts
app = typer.Typer(name="test-helper")

@app.command("project-create")
def project_create(name: str, url: str):
    info = init_project(name, url)
    typer.echo(f"✓ Project created: {info['project_id']}")
    typer.echo(f"✓ Storage: {info['paths']['root']}")

if __name__ == "__main__":
    app()
```

---

## タスク H：OpenAI Agents SDK オーケストレーション（最終出力ツール）

### 背景

-   研究書では Agents SDK を採用し、MCP をツール化して利用するパターンが想定されています【】【】。
-   最終出力ツール（Playwright コード or 修復パッチ）でループを終了する構成にすると、安定動作します（計画/研究の設計文脈に沿う）。

### 目的/効果

-   **Capture Agent**（自然言語 →MCP 操作）、**Generator Agent**（Trace→TS 生成）、**Fix Agent**（ログ → パッチ）を **Agents SDK** で統合し、**最終出力ツール**で Run を終了。
-   将来的に**マルチエージェント**（Usability/Accessibility Agent など）へ拡張しやすくする。

### 追加する主なファイル

-   `src/test_helper/agents/openai_adapter.py`（SDK の run ループ、tool 登録）
-   `src/test_helper/agents/tools.py`（MCPClient/Generator/Fix を function-tool 化）

### IF / 入出力

-   入力：自然言語プロンプト（例：「購入フローを網羅して」）
-   出力：`*.spec.ts` or `patch.diff`（**最終出力ツール**として返却）

### 受け入れ基準

-   MCP の `navigate/click/fill/assert` を function tool 経由で呼び出せる
-   「テストを生成して保存する」or「修復パッチを作る」でループが自然終了（ハングしない）

### 実装サンプル（抜粋）

```python
# agents/main.py (オーケストレーションのサンプル)
# 前提：
# - `test_helper/agents/core.py` に `Agent` と `Runner` クラスが定義されている。
# - `test_helper/agents/tools.py` に各ツール関数が定義されている。

from test_helper.agents.core import Agent, Runner
from test_helper.agents import tools

# === エージェント定義 ===
# 各エージェントの役割と利用可能なツールを定義します。

# Capture Agent: 自然言語の指示に基づきブラウザを操作し、操作履歴を生成します。
capture_agent = Agent(
    name="CaptureAgent",
    instruction="""
    You are an agent that operates a web browser based on natural language instructions 
    to capture a user flow. Use the provided tools to navigate, click, and fill fields. 
    When the instructed flow is complete, output the list of interaction events.
    """,
    tools=[
        tools.browser_navigate, 
        tools.browser_click, 
        tools.browser_fill
    ],
)

# Generator Agent: 操作履歴からテストコードを生成し、最終出力ツールで返します。
generator_agent = Agent(
    name="GeneratorAgent",
    instruction="""
    You are an agent that generates a Playwright test script from a list of browser 
    interaction events. When you are done, use the emit_spec tool to output the final code.
    """,
    tools=[
        tools.emit_spec, # 最終出力ツール
    ],
)


# === オーケストレーション実行 ===
# Runnerを使ってエージェントの実行を連携させます。

async def run_e2e_generation_from_prompt(prompt: str) -> dict:
    """
    CaptureAgentとGeneratorAgentを連携させ、
    自然言語の指示からE2Eテストコードを生成します。
    """
    # 1. Capture Agentを実行し、ブラウザ操作履歴を取得します。
    print("Running Capture Agent...")
    capture_runner = Runner(agent=capture_agent)
    # Runnerは内部で実行ループを処理し、最終的なメッセージや出力を返します。
    capture_result = await capture_runner.run(prompt)
    
    # Runnerの返り値（操作履歴のリストなど）を次のエージェントに渡します。
    interaction_events = capture_result.get("content")
    if not interaction_events:
        raise ValueError("Capture Agent did not produce interaction events.")

    # 2. Generator Agentを実行し、操作履歴からテストコードを生成します。
    print("Running Generator Agent...")
    generator_runner = Runner(agent=generator_agent)
    generation_prompt = f"Generate a Playwright test from the following interaction events: {interaction_events}"
    final_output = await generator_runner.run(generation_prompt)

    # `emit_spec`ツールの結果が最終成果物となります。
    return final_output

```

---

# 補足：設定のすり合わせ（MCP ポート）

-   Compose 内の MCP は `3001`【】、Quickstart の表記は `9000`【】。
-   **対策**：`E2ESettings` に `playwright_mcp_port` を追加（既存の設定群と同様、バリデータ付き）。CLI の `--mcp-port` で上書き可。
-   これで **本番/ローカル差異**や既存表記の不一致を吸収できます。

---

# 次の一手（おすすめの進め方）

1. **E〜H を 4 エージェントに割当**（完全並行可）：

-   Agent-1：a11y 実行・レポート化（E）
-   Agent-2：自己修復（F）
-   Agent-3：CLI 実装（G）
-   Agent-4：Agents SDK オーケストレーション（H）

2. 並行着手のあと、I〜N を **2 スプリント**に分けて段階導入（I/J→K/L→M/N の順がおすすめ）。

---

必要なら、このまま **E〜H のフルコード**を一気に書き出します。
どこから入れるか（例：まずは E ＋ G から、など）指定いただければ、その前提で「差分適用しやすい形のファイル全量」を出します。

以下に、現在のリポジトリ（A ～ D が実装済み）を前提に、残りの機能を再整理し、E ～ H の各後続タスクについて詳細な実装仕様書をまとめます。引用は、リポジトリ中の現行ファイルからの抜粋です。

---

## 現状の補足と確認

-   **Temporal ワークフロー** – `src/test_helper/services/temporal_workflows.py` には最小構成のワークフローとアクティビティが定義されています。`capture_activity` はプレースホルダーとして固定のイベントを返し、`generate_activity` はイベントを順に処理しテストコード文字列を生成しています。`E2ETestWorkflow.run` はこの 2 つのアクティビティを順次実行してコードを返します。
-   **プロジェクト管理** – `src/test_helper/storage/project_store.py` には `project_paths()` と `init_project()` が実装され、UUID の検証を含めたプロジェクトディレクトリの作成と `metadata.json` 保存処理が行われます。

これらを踏まえ、残るタスクを以下のように整理します。

---

## 後続タスク一覧（E〜H）

1. **E: a11y 自動検査統合とレポート出力**
2. **F: 自己修復機構（ロケーター更新／待機調整／パッチ生成）**
3. **G: CLI コマンド群の実装**
4. **H: OpenAI Agents SDK によるマルチエージェント統合**

それぞれ、背景・目的・インターフェース・入出力・受け入れ基準・サンプル実装を以下で詳述します。

---

### タスク E：a11y 自動検査統合 & レポート出力

#### 背景

現在の実行フローはプレーンな Playwright テスト生成までであり、アクセシビリティ検査を行っていません。研究資料では `@axe-core/playwright` による WCAG 準拠の自動検査が推奨されているため、Playwright 実行時に a11y 検査を挿入し、JSON/HTML のレポートとして保存する必要があります。報告対象フォルダは `data/projects/{project_id}/reports/` です。

#### 実装概要

-   **サービス層**：`src/test_helper/services/executor_service.py` を新設し、Playwright テストの実行と a11y 検査を統合。node 側の Playwright 実行後、`@axe-core/playwright` を呼び出してアクセシビリティ違反を検出し、`a11y.json`・`a11y.html` に保存。
-   **レポート生成**：`src/test_helper/reporters/a11y_reporter.py` を追加し、axe の検査結果 JSON を読み取り、HTML 形式へ変換（vue や template で整形）する責務を持たせる。
-   **設定の反映**：`E2ESettings` に `enable_a11y_scan` フラグと `a11y_tags`（例: `wcag2a, wcag2aa, wcag21aa`）を追加し、`init_project` で `metadata.json` に書き出す。この設定が ON の場合にのみ検査を実行。

#### IF/入出力

-   **関数**: `run_tests_with_a11y(project_id: str, spec_paths: list[str]) -> ExecutionResult`
-   **入力**: `project_id`, `spec_paths`（実行対象の spec ファイルパス）
-   **出力**: `ExecutionResult`（各 spec の pass/fail、a11y 結果パス、スクリーンショット/動画パス）
-   **保存先**: `reports/{execution_id}/a11y.json` と `a11y.html`、および Playwright 標準の HTML レポート

#### 受け入れ基準

-   a11y 検査が ON の場合、実行後に WCAG タグ別の違反情報が JSON に含まれる。
-   `a11y.html` には違反箇所の説明と DOM パスが人間に読める形で表示される。
-   a11y 検査が OFF の場合、Playwright 実行のみ行い、レポートファイルは生成しない。

#### 実装サンプル（概略）

```python
# executor_service.py
from pathlib import Path
import subprocess
from test_helper.storage.project_store import project_paths
from test_helper.utils.settings import get_e2e_settings

def run_tests_with_a11y(project_id: str, spec_paths: list[str]) -> dict:
    settings = get_e2e_settings()
    paths = project_paths(project_id)
    run_id = "exec-001"  # 実際はUUIDなど
    report_dir = Path(paths["reports"]) / run_id
    report_dir.mkdir(parents=True, exist_ok=True)

    # Playwright実行
    subprocess.run(["npx", "playwright", "test", *spec_paths, "--reporter", "html"], check=False)

    result = {"run_id": run_id, "reports_dir": str(report_dir)}

    if settings.enable_a11y_scan:
        # nodeのスクリプト等でaxe-coreを実行し、report_dirにJSON出力
        subprocess.run(["node", "scripts/a11y_scan.mjs", str(report_dir)], check=False)
        # a11y_reporter.pyでJSON→HTML変換
        a11y_json = report_dir / "a11y.json"
        a11y_html = report_dir / "a11y.html"
        # convert_to_html関数を使用してHTML生成
        ...
        result["a11y_json"] = str(a11y_json)
        result["a11y_html"] = str(a11y_html)

    return result
```

---

### タスク F：自己修復（ロケーター更新／待機調整／差分パッチ提案）

#### 背景

テストが壊れやすい主因として、DOM 変更によるロケーター破損やロード順の違いによるタイムアウトがあります。研究資料ではデータ属性優先のロケーター戦略とスマートウェイトが提案されています。`tests/conftest.py` の中では修復提案 `fix_proposal` に関するテストフィクスチャがあり、修復ロジックの形式を示唆しています。

#### 目的

-   失敗した Playwright テストのログやスクリーンショット、DOM スナップショットを解析して、新しいロケーターや待機を提案。
-   信頼度スコアを付与し、しきい値以上の場合は自動的にパッチを生成・適用する。しきい値未満の場合は人間のレビューを促す。

#### 実装概要

-   **fix_service.py** を追加し、`propose_fixes(logs: str, snapshot: dict) -> FixProposal` と `apply_patch(spec_path: Path, proposal: FixProposal) -> str` を提供する。
-   **モデル定義**：`FixProposal` を Pydantic で定義し、`changes` に変更の種類（selector 変更、timeout 追加等）と `confidence` を含める。
-   既存の `project_store` で生成される `metadata.json` に `auto_fix_confidence_threshold` があり、これを判定基準として利用する。

#### IF/入出力

-   **関数**:

    -   `propose_fixes(execution_log: str, dom_snapshot: dict) -> FixProposal`
    -   `apply_patch(spec_path: Path, proposal: FixProposal) -> str`

-   **入力**: 失敗ログ（テキスト）、DOM スナップショット（JSON）、対象 spec ファイルパス
-   **出力**: `FixProposal`（confidence・changes・rationale）、および Unified diff 形式のパッチ文字列
-   **保存**: 適用後の spec ファイルと `history/` ディレクトリへのパッチ履歴保存

#### 受け入れ基準

-   セレクター変更候補を必ず生成（例: `'#submit'` → `"[data-testid='submit']"`）し、`confidence` を 0〜1 で計算。
-   パッチ適用後に再実行し、テスト成功なら修復成功とみなす。失敗した場合は、さらなる提案を生成。

#### 実装サンプル（概略）

```python
# fix_service.py
from pydantic import BaseModel
import difflib

class FixProposal(BaseModel):
    confidence: float
    changes: list[dict]  # {line_no: int, old: str, new: str}
    rationale: str

def propose_fixes(execution_log: str, dom_snapshot: dict) -> FixProposal:
    # ロケーター不一致のログを正規表現で抽出し、data-testidを含む候補を作成
    changes = []
    for line in execution_log.splitlines():
        m = re.search(r"selector '([^']+)' not found", line)
        if m:
            old_selector = m.group(1)
            # 仮の代替候補
            new_selector = f"[data-testid='{old_selector.strip('#')}']"
            changes.append({"old": old_selector, "new": new_selector})
    confidence = 0.8 if changes else 0.0
    return FixProposal(confidence=confidence, changes=changes, rationale="Selector fallback")

def apply_patch(spec_path: Path, proposal: FixProposal) -> str:
    content = spec_path.read_text(encoding="utf-8")
    patched = content
    for ch in proposal.changes:
        patched = patched.replace(ch["old"], ch["new"])
    diff = "\n".join(difflib.unified_diff(content.splitlines(), patched.splitlines()))
    spec_path.write_text(patched, encoding="utf-8")
    return diff
```

---

### タスク G：CLI コマンド群の実装

#### 背景

Quickstart の記載では CLI の入出力例が示されており、`project create` → `capture` → `generate` → `execute` → `fix` という操作フローが想定されています。現在は CLI 実装が存在しないため、これを用意しユーザの操作をシンプルにする必要があります。

#### 目的

-   `typer` などを用いて `test-helper` コマンドを実装し、プロジェクト作成からテスト生成・実行・修復までをコマンドラインから呼び出せるようにする。
-   `init_project()`、`project_paths()`、`WorkflowClient.start_capture()` など既存 API を呼び出して下位サービスと統合する。

#### 実装概要

-   `src/test_helper/cli/main.py` を作成。Typer を用いてコマンドグループ `e2e` を定義し、サブコマンド `project-create`, `capture`, `generate`, `execute`, `fix` を実装。
-   `project-create`: `init_project` を呼び、プロジェクト ID とパスを表示。
-   `capture`: Temporal クライアントを初期化し、`WorkflowClient.start_capture` を呼ぶ。必要に応じてブラウザを開く/閉じる。
-   `generate`: キャプチャセッションの結果を `start_generate` に渡し、生成されたテストコードを `write_spec` で保存。
-   `execute`: `executor_service.run_tests_with_a11y` を呼び出し、レポートのパスを出力。
-   `fix`: `fix_service.propose_fixes` と `apply_patch` を呼び出し、必要に応じて再実行。

#### IF/入出力

-   コマンド例（予定）：

    ```bash
    test-helper e2e project-create --name "Demo" --url https://example.com
    test-helper e2e capture --project <id>
    test-helper e2e generate --project <id>
    test-helper e2e execute --project <id>
    test-helper e2e fix --project <id> --auto-apply
    ```

-   各コマンドは標準出力に次のステップや結果ファイルパスをわかりやすく出力する。

#### 受け入れ基準

-   Quickstart の入出力例とほぼ同等の利用体験が得られる。
-   例外発生時は非 0 終了コードとエラーメッセージを出力する。

#### 実装サンプル（概略）

```python
# cli/main.py
import typer
from test_helper.storage.project_store import init_project
from test_helper.services.workflow_client import WorkflowClient
from temporalio import Client

app = typer.Typer()

@app.command("project-create")
def project_create(name: str, url: str):
    info = init_project(name=name, url=url)
    typer.echo(f"Project created: {info['project_id']}")
    typer.echo(f"Paths: {info['paths']}")

@app.command("capture")
def capture(project: str):
    # Temporalクライアント初期化
    client = WorkflowClient(Client.connect(...))
    handle = client.start_capture(project_id=project)
    typer.echo(f"Capture started: {handle.workflow_id}")

# 他のサブコマンドも同様
if __name__ == "__main__":
    app()
```

---

### タスク H：OpenAI Agents SDK オーケストレーション

#### 背景

将来的には自然言語からブラウザ操作やテスト生成を行う複数エージェントを統合し、AI による自動化を強化する計画です。研究資料では Agents SDK を利用し、MCP 操作・コード生成・修復などをツールとして登録するパターンが提案されています。

#### 目的

-   **Capture Agent**：自然言語の指示を受け取り、MCPClient のツールを使ってブラウザを操作し `InteractionEvent` のリストを生成。
-   **Generator Agent**：イベントリストを受け取り、Playwright テストコードを生成して出力ツールで返す。
-   **Fix Agent**：失敗ログを基に修復提案を行い、必要ならパッチを返す。
-   それぞれのエージェントを Agents SDK の run ループに配置し、**最終出力ツール**（例えば `emit_spec` または `emit_patch`）で終了するよう設計。

#### 実装概要

-   `src/test_helper/agents/tools.py` に MCPClient の操作 (`navigate/click/fill/assert_role`) とコード出力 (`emit_spec`)・パッチ出力 (`emit_patch`) を function-tool として定義。
-   `src/test_helper/agents/openai_adapter.py` で run ループを実装し、プロンプトに応じてツールコールを行わせる。ツールが最終出力を返したらループを終了する。
-   CLI からエージェントを起動する場合は `test-helper e2e agent-run --project <id> --prompt "..."` のようにし、結果として生成された spec やパッチを保存。

#### IF/入出力

-   **関数**: `run_agent(prompt: str) -> dict`（最終出力を含む）
-   **ツール一覧**:

    -   `browser_action`: MCPClient の `navigate`, `click`, `fill`, `assert_role` を内包
    -   `emit_spec(code: str)`: 完成した Playwright テストをファイル保存して終了
    -   `emit_patch(diff: str)`: 修復パッチ生成を終了

-   **出力**: テストコード文字列、またはパッチ diff 文字列

#### 受け入れ基準

-   自然言語指示（例：`"ユーザが商品を購入するフローをテストして"`）に対して、ブラウザ操作ツールが適切に呼ばれ、最後に `emit_spec` が実行される。
-   生成されたコードは `render_spec_ts` と同等の品質である。
-   不正なインプットや途中エラーが発生した際は、安全に停止し理由を返す。



---

## まとめ

-   現行のリポジトリは基本的なワークフロー・テスト生成・プロジェクト管理を備えています。
-   **次のステップ**は a11y 検査統合（E）、自己修復（F）、CLI 化（G）、Agents SDK 統合（H）を並行して進めることです。
-   各タスクの実装仕様書に沿ってモジュールを追加・改修することで、E2E テスト自動化エージェントがより実用的になります。
