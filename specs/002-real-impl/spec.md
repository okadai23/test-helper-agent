やりたいこと、めちゃ良いです。
以下に「最新の事例とベストプラクティスの調査 ⇒ 改修対象機能リスト化 ⇒ 既存リポジトリの状況を踏まえたアーキテクチャ／機能仕様／実装方針／タスクリスト」を一気通貫でまとめました。日付は日本時間での最新情報（2025-09-11）を反映しています。

---

# ゴール

-   **自然言語 → 網羅的な E2E テスト実装**（Playwright MCP 操作）
-   **操作ログ → 確定的な Playwright コードに落とす**（コード生成・エクスポート）
-   **既存 E2E がある場合は自動修正**／**ない場合は新規生成**
-   **ブラックボックス／ホワイトボックスの両モード**対応
-   **ユーザビリティ/アクセシビリティ検証**も同一基盤で実施
-   **Temporal** でエージェントと外部実行を **durable** に編成（失敗に強く再実行／バージョニング）

---

## 1) 最新動向・ベストプラクティス（要点）

-   **Playwright MCP** は LLM から実ブラウザを操作する **MCP サーバ**。DOM を「ピクセル」ではなく **アクセシビリティスナップショット（a11y ツリー）** として扱えるのが強み（選択子安定性・画面解像度非依存）([GitHub][1])。
-   **OpenAI Agents SDK** は最小プリミティブでエージェントとツール呼び出しを構成し、マルチエージェント/最終出力ツール/ループ制御などの基本を提供（Assistants API からの移行の流れも）([OpenAI GitHub Pages][2])。
    また、**公式実践ガイド**は「run ループ」「終了条件」「最終出力ツール」の設計を推奨([OpenAI][3])。
-   **Temporal** は長時間実行・再実行・決定論的リプレイ・バージョニングが前提。**非決定的コードを避け、Workflow と Activity を分離**、リプレイ互換のための **Versioning** が重要（TS/Go SDK の耐久実行ベストプラクティス）([learn.temporal.io][4])。
    一方で **ワークフロー変更時のバージョニング負債や過剰リプレイ**の落とし穴も最近の実務談で指摘されているため、**型付きバージョニングとメトリクス監視**を前提に設計すべき([Medium][5])。
-   **テストコードへの落とし込み（Codegen）** は Playwright 公式の **codegen**／**Recorder** が堅い選択。ロール/テキスト/`data-testid` を優先して**堅牢なロケーター**を自動生成、認証状態の保存/再利用、デバイス・ビューポートのエミュレーションも可能([Playwright][6])。
-   **AI での E2E 生成**は「完全自動はまだ早いが“初期ドラフト”として有用」な評価。生成 → 人手レビュー → 安定化の**二段運用**が推奨されつつある([Checkly][7])。
-   **アクセシビリティ/ユーザビリティ** は `@axe-core/playwright` による **自動 a11y 検査**を Playwright に統合し、**WCAG タグ指定**や**一部除外/ルール抑制**、**レポート添付**まで公式で解説。**自動検査は限界があるため手動評価の併用**が前提([Playwright][8])。
-   **テストデータ戦略/フレーク対策**では、**データ分離・リトライ/スマートウェイト・選択子安定化**・履歴/レポートの体系化が近年のプラクティス([momentic.ai][9])。

---

## 2) 改修対象「機能リスト」（調査反映）

1. **自然言語 → 網羅テスト生成（MCP 操作）**

    - a11y スナップショットを解析 → 主要フローの**サイトマッピング**／ゴール指向探索（ログイン → 購入など）([Playwright][10])
    - 失敗時の**探索再開戦略**（要素再特定・待機調整・フォールバックロケーター）

2. **操作ログ →Playwright 確定コード**

    - MCP の操作列を **Playwright codegen 互換のイベント**に正規化し、`*.spec.ts` を出力（`data-testid` 優先、コード書式と `test.step` の粒度基準）([Playwright][6])

3. **既存テストの自動修復**

    - 失敗ログから**差分生成（ロケーター更新／待機追加／ネットワーク待機）**→PR 提案

4. **ブラックボックス／ホワイトボックス統合**

    - **BB**: クローラ＋ a11y ツリーから**フロー推定**
    - **WB**: ルーティング/コンポーネント/`data-testid` の静的解析で\*\*テスト種（経路網羅・重要 UI）\*\*を優先度付け

5. **ユーザビリティ/アクセシビリティ検証**

    - `@axe-core/playwright` による **WCAG 自動検査＋ JSON/HTML レポート添付**、しきい値を Temporal でガードレール化([Playwright][8])

6. **レポート/可観測性**

    - **テスト実行レポート＋ a11y レポート**、MCP セッションの**操作タイムライン**、**スクショ/動画**添付

7. **Temporal ワークフロー**

    - **準備 → 探索 → 生成 → 実行 → 診断/修復** を **Activity** 分割
    - **Workflow Versioning** と**決定論的 I/O**のガイドライン徹底([learn.temporal.io][4])

8. **CI/CD 統合**

    - 生成/修復結果を PR 化、**差分プレビュー**と**レポートコメント**の Bot 投稿

9. **セキュリティ/安全策**

    - URL/パス検証・プロファイル隔離（コンテキスト分離）・レート制限・秘匿情報の赤入れ（a11y レポート）([Playwright][8])

---

## 3) 既存リポジトリの現状（重要ポイント）

-   **docker-compose** には Temporal/Postgres/Temporal UI と **playwright-mcp** サービスが既に定義（MCP: `mckaywrigley/playwright-mcp:latest`）。
-   **Temporal クライアント（WorkflowClient）** は **未実装の例外**を投げる状態（Capture/Generate の start が `NotImplementedError`）→ ここを最優先で実装する。
-   プロジェクトの **技術スタック** と参照 URL は明文化済み（OpenAI Agents SDK／Temporal／Playwright MCP 等）。
-   **設定** に OpenAI モデルバリデーション、Temporal/Agents の **mock / sdk 切替**があり、SDK 実装差し替えの設計ができている。
-   **仕様・設計文書**（research/plan/quickstart）が雛形として整備済。CLI コマンドやストレージ構成、サービス分割の方針が記載済み。

---

## 4) 推奨アーキテクチャ

### 4.1 論理構成（エージェント × ワークフロー）

-   **Capture Agent**（MCP 操作）

    -   目的：自然言語の指示からブラウザ操作・サイトマップ生成
    -   出力：**Interaction Trace**（正規化イベント列＋要素メタ）
    -   実装：Agents SDK の tool 呼び出しで MCP の **navigate/click/input/assert** などの関数を公開（a11y ツリーを一次情報に）([Playwright][10])

-   **Generator Agent**（コード化）

    -   目的：Trace → `*.spec.ts`（Playwright Test）
    -   ルール：`data-testid` 最優先／`getByRole` 次点・待機は `locator.waitFor()`／`expect` を要所で自動付与（公式 Codegen ルールに倣う）([Playwright][6])

-   **Executor & Reporter**

    -   目的：テスト実行、レポート（HTML/JSON）、スクショ/動画、a11y スキャン添付（axe）([Playwright][8])

-   **Fix Agent**（自己修復）

    -   目的：失敗ログ → 差分パッチ（ロケーター更新／待機／フレーク緩和）

-   **Usability/Accessibility Agent**

    -   目的：**WCAG タグ**ベースの自動検査、**ヒューリスティック**（Fitts の法則近傍・低コントラスト・フォーカス可視性）レポート化([Playwright][8])

### 4.2 Temporal ワークフロー（TypeScript/Python どちらでも）

**Workflow: E2ETestLifecycle(projectId, mode\[BB/WB])**

1. **Prepare**（アプリ起動確認/ログイン準備/プロファイル用意）
2. **Explore/Capture**（Capture Agent 活動＝ MCP Activity）
3. **Generate**（Generator Agent Activity → `*.spec.ts` 保存）
4. **Execute**（Playwright 実行／a11y スキャン）
5. **Diagnose & Fix**（Fix Agent→PR 提案）
6. **Publish Report**（HTML/JSON・Temporal UI にリンク）

> ベストプラクティス：**Activity に副作用を寄せ、Workflow は決定論的に**。外部 I/O は Activity 経由、**Workflow Versioning** を採用([learn.temporal.io][4])。

---

## 5) 機能仕様（抜粋）

### 5.1 準備フェーズ

-   対象 URL、認証情報（必要なら）と **モード（BB/WB）** を受け取る
-   **BB**: サイトマップ探索深さ・robots 尊重／**WB**: ルーティング/コンポーネント走査（`data-testid` 推奨化）
-   デバイス/ビューポート/言語/タイムゾーンの**エミュレーション**設定（codegen と合わせる）([Playwright][6])

### 5.2 テスト実施フェーズ

-   **自然言語テスト指定**：「“購入フローを一通り”」「“エラー状態を確認”」
-   **生成物**：

    -   `tests/{scenario}.spec.ts`
    -   `reports/{executionId}/index.html`（Playwright）
    -   `reports/{executionId}/a11y.json/html`（axe）([Playwright][8])
    -   `history/`（バージョン履歴）

### 5.3 エクスポート/再現

-   **MCP 操作ログ → 確定コード**：トレース →AST 変換 → テンプレートで整形（`test.step` のまとまり、`expect`付与）
-   **Codegen 併用**：必要に応じて `playwright codegen` を\*\*部分差し込み（Record at Cursor）\*\*で補完([Playwright][6])。

### 5.4 a11y/ユーザビリティ

-   `AxeBuilder.withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa'])` を既定、**違反ゼロ**を初期しきい値に([Playwright][8])。
-   既知の例外は `exclude()`/`disableRules()` を**テストフィクスチャ**で集中管理（レポートに注記）([Playwright][8])。

---

## 6) 実装方針（既存構成に沿って）

### 6.1 OpenAI Agents SDK 統合

-   既存の **adapter** ファクトリに基づき、SDK 実体を差し込み（`agent_backend: "sdk"`）。
-   エージェントには **“最終出力ツール”** を定義（Playwright テストコード or 修復パッチ生成でループ終了）([OpenAI][3])。

### 6.2 MCP クライアント

-   `lib/playwright_mcp.py`（既存設計の空所）に **MCP ツール定義**（`navigate(url)`, `click(selector)`, `fill(selector, value)`, `assert(role/text/testid)` など）を実装し、Agents SDK 側に **function tool** として公開。
    ※ a11y スナップショットベースの要素解決を優先([Playwright][10])。

### 6.3 Temporal Workflow 実装

-   **WorkflowClient** の `start_capture` / `start_generate` を SDK 実装で置換（現状 `NotImplementedError`）。
-   Activities: `prepare_activity` / `capture_activity` / `generate_activity` / `execute_activity` / `diagnose_fix_activity` / `publish_report_activity`。
-   **Versioning ポリシー**（`WORKFLOW_VERSION = 1` → 変更時は `workflow.get_version('step', 1, 2)`）を採用([learn.temporal.io][4])。

### 6.4 コード生成

-   **イベント正規化** → Playwright **テストテンプレート**に流し込む。
-   ロケーター生成規約：`getByTestId` > `getByRole(name=)` > `getByText` > CSS/XPath（最後の手段）([Playwright][6])。
-   認証フローは `--save-storage/--load-storage` の運用をサポート（記録/再利用）([Playwright][6])。

### 6.5 a11y 統合

-   `@axe-core/playwright` を実行時に組み込み、**違反の JSON を test attachment として保存**（公式手順）([Playwright][8])。

---

## 7) データ/ストレージ設計（既存方針を踏襲）

-   `data/projects/{id}/tests/*.spec.ts`, `history/`, `cache/selectors.json`, `reports/…`（現状の設計書に一致）。

---

## 8) 具体タスクリスト（優先度順）

### フェーズ A：下回り実装（Temporal/MCP/Agents）

1. **Temporal SDK 配線**：`WorkflowClient` に `start_capture` / `start_generate` を実装（Temporal Client 経由の `start_workflow` 呼び出し）。
2. **Workflows/Activities 追加**：`lib/temporal_workflows.py` に上記ワークフロー定義（決定論的処理、I/O は Activity）([learn.temporal.io][4])。
3. **MCP クライアント層**：`lib/playwright_mcp.py` に MCP 接続とツール群。a11y スナップショット API の結果をイベント正規化([Playwright][10])。
4. **Agents SDK 統合**：`agents/openai_adapter.py` の run ループに **最終出力ツール**と **MCP ツール**を組込（モデル名は設定の許可一覧に従う）。

### フェーズ B：生成/実行/修復

5. **コード生成器**：`services/generator_service.py` に Trace→AST→`*.spec.ts` 出力（ロケーター規約/`test.step`/`expect` 挿入）([Playwright][6])。
6. **既存テスト修復器**：`services/fix_service.py` に失敗ログ → 差分パッチ（`locator` 更新・待機・リトライ）。PR 用パッチ/要約を生成。
7. **実行&レポート**：`services/executor_service.py` に Playwright 実行、**a11y スキャンと JSON/HTML 添付**、スクショ/動画保存([Playwright][8])。

### フェーズ C：BB/WB モード

8. **BB 探索**：サイトマップ探索（深さ/同一ドメイン制約）→ 代表ユーザフロー抽出。
9. **WB 解析**：フレームワーク別（Next.js/React Router 等）ルーティング・`data-testid` 検出 → **カバレッジ優先度**付与。

### フェーズ D：ガードレール/運用

10. **Workflow Versioning/メトリクス**：ワークフローバージョンの導入、**過剰リプレイ検知**のメトリクス/アラート([learn.temporal.io][4])。
11. **CI/CD 統合**：GitHub Actions でテスト生成/修復の PR 化、レポート URL 貼付。
12. **ドキュメント更新**：`quickstart.md` のポート・コマンド（MCP のポート表記差異修正）／ `CLAUDE.md` の最近の変更追記（Agents SDK 明記）。

---

## 9) 追加の改善提案（“採用すると効く”やつ）

-   **テストデータの戦略**：疎結合な**シード/ファクトリ**、**idempotent** な前提状態、**並列実行**への耐性（近年のベストプラクティス）([momentic.ai][9])。
-   **探索の停止条件**：**時間/遷移数/未訪問率**でヒューリスティクス、**404/500** の自動報告。
-   **可視化**：MCP イベントの **タイムライン可視化**（DOM スナップショット、ハイライトリプレイ）。
-   **多言語 UI**：ロール/テスト ID 優先で**言語依存を最小化**（テキスト依存を回避）([Playwright][6])。

---

## 10) 参考リンク（主要一次情報）

-   Playwright MCP（公式/解説）([GitHub][1])
-   Playwright Test generator / Codegen（公式）([Playwright][6])
-   OpenAI Agents SDK（公式）([OpenAI GitHub Pages][2])
-   OpenAI「実践ガイド：エージェント構築」([OpenAI][3])
-   Temporal「Durable Execution」ベストプラクティス（TS/Go）([learn.temporal.io][4])
-   Temporal コミュニティのワークフロー設計 Tips（最近）([Temporal][11])
-   AI×Playwright テスト生成の実務的評価（2025-07）([Checkly][7])
-   a11y テスト（axe 公式統合ガイド）([Playwright][8])

---

### 補足：リポジトリ内のドキュメント・設計物（該当箇所）

-   docker-compose（Temporal/MCP 定義）
-   Temporal クライアント未実装箇所（要実装）
-   技術スタック一覧（Agents/Temporal/Playwright MCP）
-   仕様計画（モジュール構成/CLI/ストレージ）

---

## 11) 次アクション（私がこの場で出せる具体アウトプット）

-   **Workflow 定義ひな型（Python or TS）**、**MCP ツール定義スキーマ**、**生成テンプレート（`*.spec.ts`）**、**axe スキャン組込例**など、初回コミット案をすぐに書けます。
-   もし Python/TS どちらで Temporal を実装するか希望があれば、**その言語での最小実装**をここで提示します（コードとファイル配置まで）。

ご希望があれば、**まずは Python 版 Temporal Workflow + MCP クライアント + 生成テンプレート**のスケルトンをこの場で作ります。どちらで進めますか？（なにも指定がなければ **Python** で用意します）

[1]: https://github.com/microsoft/playwright-mcp?utm_source=chatgpt.com "microsoft/playwright-mcp: Playwright MCP server"
[2]: https://openai.github.io/openai-agents-python/?utm_source=chatgpt.com "OpenAI Agents SDK"
[3]: https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf?utm_source=chatgpt.com "A practical guide to building agents"
[4]: https://learn.temporal.io/tutorials/typescript/background-check/durable-execution/?utm_source=chatgpt.com "Develop code that durably executes - TypeScript SDK dev ..."
[5]: https://medium.com/%40qlong/workflow-should-be-code-but-durable-execution-is-not-the-only-way-519f7682360c?utm_source=chatgpt.com "Workflow Should be Code, but Durable Execution is NOT ..."
[6]: https://playwright.dev/docs/codegen?utm_source=chatgpt.com "Test generator | Playwright"
[7]: https://www.checklyhq.com/blog/generate-end-to-end-tests-with-ai-and-playwright/?utm_source=chatgpt.com "Generating end-to-end tests with AI and Playwright MCP"
[8]: https://playwright.dev/docs/accessibility-testing?utm_source=chatgpt.com "Accessibility testing | Playwright"
[9]: https://momentic.ai/resources/mastering-playwright-test-data-a-comprehensive-guide-to-resilient-e2e-testing?utm_source=chatgpt.com "Mastering Playwright Test Data: A Comprehensive Guide ..."
[10]: https://playwright.dev/agents?utm_source=chatgpt.com "Introduction to Playwright MCP"
[11]: https://community.temporal.io/t/best-practices-for-structuring-complex-go-workflows/17329?utm_source=chatgpt.com "Best practices for structuring complex Go workflows"

必要に応じて、このレポートに基づいて具体的なコードやワークフロー設計の実装を進めることも可能です。ご要望があればいつでもお知らせください。

---

# report

E2E Test Automation AI Agent: Research & Implementation Plan

1. 背景と目的
   本機能は、既存の Web アプリケーションの E2E テスト自動化を AI によって支援するものです。具体的には、Playwright MCP でユーザー操作を自然言語で指定し、OpenAI Agents SDK を使ったエージェントがその操作をブラウザで実行して テストシナリオを生成し、それを確定的な Playwright テストコードに落とします。また既存テストの修正やフレーク対策、アクセシビリティ検査なども自動化し、Temporal を利用して耐障害性の高いワークフローとして実行します。さらにブラックボックス (BB)／ホワイトボックス (WB) の両モードで利用可能とし、ユーザビリティ検証も含めた総合的なテスト支援を目的とします。
2. 既存コードと技術スタックの把握
   2.1 コンテナ構成
   docker-compose.yml には Temporal サーバ、Temporal UI、PostgreSQL、Redis、および playwright‑mcp サービスが定義されています。Playwright MCP サービスは mckaywrigley/playwright-mcp:latest イメージを使用し、ポート 3001 を公開してブラウザ自動操作を提供します[1]。Temporal サーバは gRPC 用に 7233 番ポート、UI 用に 8080 番ポートで起動しています[2]。
   2.2 サービスクライアントと設定
   WorkflowClient クラスは Temporal ワークフローのスタブですが、start_capture と start_generate は未実装で NotImplementedError を送出しています[3][4]。エージェント設定 (E2ESettings) では OpenAI モデルやバックエンドの切替ができ、許可されるモデル名は gpt‑4o から gpt‑5‑nano までであると検証されています[5]。設定により Agents SDK と Temporal SDK どちらを使用するか（mock／sdk）を切り替えることも可能です[6]。
   2.3 ドキュメント
   既存の research.md は、OpenAI Agents SDK, Temporal, Playwright MCP, Pydantic を採用する決定とその理由を記述しています。[7] には Agents SDK を選んだ理由（マルチエージェント対応、ツール呼び出しなど）、[8] には Temporal を用いる理由（リトライと補償、バージョニングなど）、[9]には Playwright MCP の長所がまとめられています。ストレージは階層型ファイルシステム＋ JSON メタデータとし[10]、テストシナリオやステップのデータモデルには Pydantic の discriminated union を用いる方針です[11]。Quickstart ガイドでは CLI を用いてプロジェクト作成、キャプチャ、テスト生成、実行、修復を行う流れが示されており[12][13]、失敗時には e2e fix --auto-apply で自動修復が可能なことが説明されています[14]。
3. 最新動向・ベストプラクティス調査
   3.1 Playwright MCP とコード生成
   • MCP (Model Context Protocol) は Playwright サーバ経由でブラウザを操作するプロトコルで、LLM から DOM 要素を読み取り・操作する。アクセシビリティツリーを参照するため視覚的なレイアウトに依存せず、data-testid や ARIA ロールを優先したセレクタ生成が推奨されている。
   • Playwright codegen/Recorder を併用し、ユーザー操作を Playwright テストコード (\*.spec.ts) に変換する。公式ツールは getByTestId → getByRole → getByText → CSS の優先順でセレクタを生成し、認証情報の保存 (--save-storage)／読み込み (--load-storage) により認証フローを安定化させる。
   • アクセシビリティ検証には @axe-core/playwright が使われ、WCAG 2.1 レベル A/AA のタグ指定で自動レポートを生成できる。自動検査の限界を理解し、手動評価やデザインレビューの補助として位置付ける。
   3.2 OpenAI Agents SDK
   • Agents SDK は Structured tool calling と multi-agent orchestration をネイティブにサポートしており、会話メモリと中間出力を管理できる。実践ガイドではツール呼び出しのループ制御と「最終出力ツール」の設定を推奨している。
   • LLM によるテスト生成は初期ドラフトとして有用だが、完全自動は難しい。人によるレビューと自動生成のハイブリッド運用が推奨されている。
   3.3 Temporal
   • Temporal は 長時間・リトライを伴うワークロードに適しており、非決定的な処理を Activity として分離し、ワークフロー本体は決定論的ロジックに限定すべきである。
   • Workflow versioning を用いて変更点をバージョン管理し、過去の実行と互換性を保つ。過剰なリプレイや無制限のバージョン増加を避けるため、メトリクス監視とリソース管理が必要である。
   3.4 テスト生成・修復の課題
   • セレクタ安定性: data-testid を導入できない画面では ARIA ロール＋テキストの組み合わせや複数戦略を使用する。
   • 動的コンテンツ・フレーク対策: スマートウェイト (locator.waitFor/expect(...)) とリトライにより DOM の変化に対応し、タイミング問題を軽減する。
   • アクセシビリティ/ユーザビリティ検証: コントラスト比やフォーカス可視性などヒューリスティックチェックは axe と併用し、重大度の高い違反が残った場合は失敗として扱う。手動評価を補完する。
4. 改修対象機能リスト
5. 自然言語からの E2E テスト生成
6. Playwright MCP 経由でブラウザを操作し、サイトマップ探索と主要ユーザーフローを抽出。操作イベントを正規化し、失敗時の再試行やフォールバックロケータ戦略を実装。
7. a11y ツリーの解析により、UI 要素のロールや data-testid を収集し、BB モードでも安定したセレクタを生成する。
8. 操作ログからの Playwright コード生成
9. MCP 操作トレースを Playwright Test の AST に変換し、\*.spec.ts を出力。test.step で論理的なまとまりを表現し、expect アサーションを自動挿入。生成ルールは getByTestId → getByRole → getByText → CSS を順守する。
10. 既存テストの自動修復
11. 失敗ログと DOM 差分を解析し、ロケータ変更・待機追加・リトライ処理などのパッチを生成。信頼度に応じて自動適用／手動レビューを切り替える。
12. ブラックボックス／ホワイトボックスモード
13. BB: クローラでサイトマップを構築し、深さ制限やドメイン制限を設けながらユーザーフローを探索。
14. WB: ルーティングやコンポーネント定義を静的解析し、data-testid の有無を検出して重要な UI パスを優先的にテスト。React Router 等のフレームワーク特性を利用。
15. ユーザビリティ／アクセシビリティ検証
16. @axe-core/playwright を統合し、WCAG 2.1 A/AA タグで自動レポートを生成。重大な違反がある場合はテスト失敗として扱い、JSON/HTML レポートを出力。
17. レポートと可観測性
18. テスト実行時にスクリーンショット・動画・操作タイムラインを保存し、HTML レポートに埋め込む。アクセシビリティレポートも添付。Temporal Workflow の各 Activity にログとメトリクスを付与し、UI から状態を把握できるようにする。
19. Temporal ワークフロー
20. prepare → explore/capture → generate → execute → diagnose/fix → publish report を一つの Workflow とし、各ステージを独立した Activity に分離。Workflow バージョニングと決定論的ロジックの遵守、リトライ/タイムアウト設定を行う。
21. CI/CD 統合
22. 生成されたテストや修復パッチを GitHub Pull Request として提出し、自動で差分を確認できるようにする。テスト結果やアクセシビリティレポートを PR コメントに添付する GitHub Action を追加する。
23. セキュリティと隔離
24. URL やファイルパスの検証、ブラウザコンテキストの分離、リクエストのレート制限を実装。アクセシビリティレポートに個人情報が含まれないようフィルタリングし、機密情報を扱う場合はトークナイズやマスキングを行う。
25. 提案アーキテクチャ
    5.1 エージェント構成
    エージェント/サービス 役割 実装ポイント
    Capture Agent MCP の navigate/click/input/assert などのツールを通じてブラウザ操作を行い、ユーザー指示や探索アルゴリズムに従ってインタラクショントレースを収集 OpenAI Agents SDK で function ツールとして公開。a11y ツリーに基づく要素解決を実装。
    Generator Agent インタラクショントレースを Playwright テストコードに変換。セレクタ生成規則・待機挿入・expect 付与を行う services/generator_service.py に実装し、テンプレートベースで \*.spec.ts を出力
    Executor/Reporter テスト実行・アクセシビリティスキャン・スクリーンショット/動画取得・HTML/JSON レポート生成 services/executor_service.py に実装し、@axe-core/playwright を統合
    Fix Agent テスト失敗時のログ解析と自動修正パッチ生成。ロケータ変更や待機追加などを提案 services/fix_service.py に実装し、信頼度に応じて自動適用・手動レビューを区別
    Usability/Accessibility Agent ユーザビリティ指標（Fitts の法則、フォーカス可視性など）やアクセシビリティ違反の検出 アクセシビリティレポートを拡張し、ヒューリスティックチェックを追加
    5.2 Temporal ワークフロー
    @workflow.defn
    class E2ETestLifecycle:
    @workflow.run
    async def run(self, project_id: str, mode: str) -> TestResult: # 1. 準備フェーズ
    await workflow.execute_activity(prepare_activity, project_id, mode,
    start_to_close_timeout=timedelta(minutes=5)) # 2. 探索・キャプチャ
    capture_result = await workflow.execute_activity(capture_activity, project_id, mode,
    start_to_close_timeout=timedelta(minutes=15)) # 3. テストコード生成
    test_files = await workflow.execute_activity(generate_activity, capture_result,
    start_to_close_timeout=timedelta(minutes=5)) # 4. テスト実行＋アクセシビリティ検査
    exec_report = await workflow.execute_activity(execute_activity, test_files,
    start_to_close_timeout=timedelta(minutes=10)) # 5. 診断・修復
    await workflow.execute_activity(diagnose_and_fix_activity, exec_report,
    start_to_close_timeout=timedelta(minutes=5)) # 6. レポート公開
    await workflow.execute_activity(publish_report_activity, exec_report,
    start_to_close_timeout=timedelta(minutes=2))
    return exec_report
    • 各 Activity は非決定的操作（ブラウザ操作、ファイル I/O、API 呼び出し）を担当し、ワークフロー本体は決定論的に保つ。
    • バージョン変更時は workflow.get_version("E2ETestLifecycle", 1, 2) を用いて下位互換を保持する。
    • タイムアウト・リトライは Temporal のオプションで設定し、障害時に自動再実行されるようにする。
    5.3 ストレージ構成
    • data/projects/{project_id}/metadata.json – プロジェクト設定。
    • tests/{test_id}.spec.ts – 生成された Playwright テストコード。[15]
    • {test_id}.meta.json – テストメタデータ（生成日時、対象 URL、アサーション数など）。
    • cache/captures.json – キャプチャセッションのイベントトレース。[16]
    • cache/selectors.json – 各要素に対する候補セレクタと信頼度。
    • history/{timestamp}/ – 過去のテストバージョン。
    • reports/{execution_id}/index.html – テスト実行＆アクセシビリティレポート。
26. 実装方針
    6.1 MCP クライアント
    lib/playwright_mcp.py で MCP サーバとの接続をラップし、navigate(url), click(selector), fill(selector, value), assert_role(role, name) 等のメソッドを公開する。これらを Agents SDK の function ツールとして登録することで、エージェントがブラウザ操作を呼び出せるようにする。a11y ツリーを取得して要素候補を返すメソッドも追加する。
    6.2 Agents SDK の統合
    agents/openai_adapter.py において、実行時に使用するツールリストを構築し、agent_backend 設定に応じて SDK 実装 (openai.beta.agents) を呼び出す。システムプロンプトには "ユーザーの自然言語要求からテスト手順を抽出し、MCP ツールを適切に呼び出す" といった指示を与える。また、Conversation ループ終了時の「最終出力ツール」としてテストコード生成や修復パッチ生成を定義する。
    6.3 Temporal アダプタ
    WorkflowClient の start_capture と start_generate を実装し、Temporal クライアント経由で E2ETestLifecycle ワークフローを起動できるようにする。設定で temporal_backend='sdk' の場合は実 SDK を用い、mock の場合は同期的な疑似実行を行う。
    6.4 コード生成器
    services/generator_service.py でキャプチャイベントを解析し、Playwright AST を生成する。セレクタ生成規則に従って getByTestId 等を選択し、test.step() で手順のまとまりを記述し、expect(locator).toHaveText(...) などのアサーションを挿入する。コードテンプレートには TypeScript 用のヘッダー (import { test, expect } from '@playwright/test') とデフォルト設定 (headless, viewport, storageState) を含める。
    6.5 実行・レポート・修復
    services/executor_service.py では Playwright テストを実行し、失敗した場合はスクリーンショットや動画を保存する。@axe-core/playwright によるアクセシビリティスキャン結果を JSON/HTML で出力し、違反数が閾値を超えた場合はテスト失敗として扱う。services/fix_service.py では失敗ログと DOM スナップショットを比較し、セレクタ変更や待機挿入の提案を生成する。
    6.6 BB/WB モード解析
    • BB モード: Selenium/Playwright ライクなクローラを実装し、ページ遷移を BFS/DFS で探索。リンクやフォームをたどりながらサイトマップを構築し、主要フロー候補を抽出。探索深さや遷移回数の上限を設定する。
    • WB モード: React/Next.js 等のルーティングファイルやコンポーネントツリーを解析し、各ページに存在する data-testid を抽出。エッジ (リンクやフォーム遷移) のグラフを構築し、経路網羅や CRUD 操作などのテスト優先度を算出する。
    6.7 CI/CD 統合
    GitHub Actions で e2e generate と e2e fix を定期実行し、生成されたテストや修復パッチを PR として投稿するワークフローを追加する。テスト実行結果とアクセシビリティレポートへのリンクを PR コメントに挿入し、レビュー担当者が変更内容を確認できるようにする。
27. タスクリスト (推奨実施順)
28. Temporal SDK 配線: WorkflowClient.start_capture/start_generate を Temporal クライアントで実装し、E2ETestLifecycle ワークフローを起動できるようにする[3][4]。
29. Workflows/Activities 実装: lib/temporal_workflows.py に prepare_activity, capture_activity, generate_activity, execute_activity, diagnose_and_fix_activity, publish_report_activity を実装。Activity ごとにタイムアウトとリトライを設定。
30. MCP クライアントとツール登録: lib/playwright_mcp.py に MCP ツール群を実装し、Agents SDK で function ツールとして登録。a11y ツリー取得関数を含める。
31. Generator サービス: キャプチャトレースから Playwright AST を生成するコードを generator_service.py に実装。セレクタ戦略とアサーション挿入のロジックを組み込む。
32. Executor/Reporter サービス: テスト実行・スクリーンショット/動画取得・axe スキャン・HTML/JSON レポート生成を executor_service.py に実装。
33. Fix サービス: 失敗時のログ解析と修復パッチ提案を fix_service.py に実装。confidence 閾値によって自動適用とレビュー提案を切り替える。
34. BB/WB 解析モジュール: クローラおよび静的解析器を実装し、ユーザーモードによって呼び出す。対象言語 (React/Next.js など) ごとにパース処理を追加。
35. Agents SDK 統合とプロンプト設計: openai_adapter.py を拡張し、エージェントのシステムプロンプトとツールセットを設計。Agents SDK のループ制御と最終出力ツールを設定する。
36. CLI インターフェース拡張: cli/ 配下のコマンド (project, capture, generate, execute, fix) に BB/WB モード選択、アクセシビリティオプション、レポート出力先などのパラメータを追加。
37. CI/CD ワークフロー: GitHub Actions 用ワークフローファイルを作成し、e2e generate と e2e fix を自動実行して PR を作成。テスト結果とアクセシビリティレポートを PR コメントに添付。
38. おわりに
    本ドキュメントでは、Playwright MCP と OpenAI Agents SDK、Temporal に基づく E2E テスト自動化エージェントの研究結果、既存リポジトリの現状、最新のベストプラクティスを整理し、改修対象機能リスト、アーキテクチャ設計、実装方針、タスクリストを提示しました。既存コードでは Temporal ワークフローが未実装であり、ここを起点に下回りのインフラを構築する必要があります。最新動向を取り入れながら、段階的に実装を進めることで、耐障害性と実用性を備えたテスト自動化基盤を構築できるでしょう。

---

[1] [2] raw.githubusercontent.com
https://raw.githubusercontent.com/daisuke19891023/test-helper-agent/07acdc2a14fa0278a60f64635c956c0fa68a79b4/docker-compose.yml
[3] [4] raw.githubusercontent.com
https://raw.githubusercontent.com/daisuke19891023/test-helper-agent/07acdc2a14fa0278a60f64635c956c0fa68a79b4/src/test_helper/services/workflow_client.py
[5] [6] raw.githubusercontent.com
https://raw.githubusercontent.com/daisuke19891023/test-helper-agent/07acdc2a14fa0278a60f64635c956c0fa68a79b4/src/test_helper/utils/settings.py
[7] [8] [9] [10] [11] [15] [16] raw.githubusercontent.com
https://raw.githubusercontent.com/daisuke19891023/test-helper-agent/07acdc2a14fa0278a60f64635c956c0fa68a79b4/specs/001-e2e-ai-agent/research.md
[12] [13] [14] raw.githubusercontent.com
https://raw.githubusercontent.com/daisuke19891023/test-helper-agent/07acdc2a14fa0278a60f64635c956c0fa68a79b4/specs/001-e2e-ai-agent/quickstart.md

---
