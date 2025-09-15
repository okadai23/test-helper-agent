# Test Helper Agent

AI を用いて Web アプリの E2E テスト（Playwright）を自動生成・保守するエージェントプロジェクトです。自然言語でテスト仕様を記述し、ブラウザ操作の記録から堅牢なテストコードを生成し、UI 変更によるテスト破損も自動的に解析・修復できます。詳細ドキュメントは `docs/` を参照してください。

- 主要ガイド: `docs/quickstart.md`, `docs/installation.md`
- エージェント × Temporal 連携: `docs/guides/temporal_agents.md`

## 特長

- **自然言語 → E2E テスト**: ユーザーフローを文章で記述するだけで包括的な Playwright テストを生成
- **自動テスト生成**: ブラウザ操作の記録をクリーンで決定的な `*.spec.ts` に変換
- **オートヒーリング**: UI 変更（セレクタ更新など）で壊れたテストを自動検出・自動修復
- **ブラックボックス/ホワイトボックス**: 実アプリのクロール（黒箱）とソース解析（白箱）の両モードに対応
- **アクセシビリティ/ユーザビリティ検査**: `@axe-core/playwright` と連携
- **耐久性のあるワークフロー**: Temporal により生成 → 実行 → 修復までを信頼性高く再実行可能にオーケストレーション
- **複数インターフェース**: CLI（`test-helper`）と REST API を提供

## 技術スタック

- **Web フレームワーク**: FastAPI
- **テスト**: pytest, Playwright
- **依存管理**: uv
- **タスクランナー**: nox
- **静的解析/品質**: Ruff, Pyright（strict）
- **バリデーション**: Pydantic v2
- **ワークフローエンジン**: Temporal
- **AI フレームワーク**: OpenAI Agents SDK
- **ブラウザ制御**: Playwright MCP
- **ドキュメンテーション**: MkDocs

各ツールの公式ドキュメントリンクは `CLAUDE.md` を参照してください。

$1

## インストール

### パッケージのインストール

```bash
# プロジェクトをクローン
git clone https://github.com/yourusername/test-helper-agent.git
cd test-helper-agent

# 依存関係をインストール（開発用とエージェント用の両方）
uv pip install -e .[dev,agents]

# Node.js 依存関係をインストール（TypeScript/ESLint用）
npm install

# これで test-helper コマンドが利用可能になります
test-helper --help
```

### 環境設定

`.env` ファイルをプロジェクトルートに作成し、以下を設定：

```bash
# OpenAI API設定
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4  # or gpt-4o-mini

# エージェントバックエンド設定
AGENT_BACKEND=sdk  # 実際のOpenAI APIを使用（mockでモックモード）
```

### CLIの使用方法

#### 基本コマンド

```bash
# ヘルプの表示
test-helper --help

# 設定の確認
test-helper config --show

# カスタム .env ファイルの指定
test-helper --dotenv /path/to/.env config --show
```

#### E2E テスト自動化コマンド

```bash
# キャプチャプランの作成
test-helper e2e capture <project-id> <base-url> --output capture.json

# テストの生成（キャプチャセッションから）
test-helper e2e generate session.json --output test.spec.ts

# TypeScript構文チェック
test-helper e2e syntax-check test.spec.ts

# TypeScript構文の自動修正
test-helper e2e syntax-check test.spec.ts --fix

# テスト失敗の診断
test-helper e2e diagnose error.log

# 失敗したテストの修正提案
test-helper e2e fix test.spec.ts --error-log error.log
```

#### モックモードでの実行

API キーを使用せずにモックモードでテストする場合：

```bash
# モックモードでテスト生成
test-helper e2e generate session.json --output test.spec.ts --mock

# モックモードで構文チェック（AI修正なし）
test-helper e2e syntax-check test.spec.ts --fix --mock
```

### TypeScript/Playwright テストの検証

生成されたテストの構文を検証し、自動修正：

```bash
# TypeScriptコンパイラとESLintでチェック
npm run typecheck
npm run lint

# 自動修正
npm run fix:all

# または test-helper CLI を使用
test-helper e2e syntax-check generated_test.spec.ts --fix
```

## Playwright セットアップ（初回のみ）

Playwright はブラウザ本体のインストールが必要です。uv 経由で以下を実行してください。

```bash
# ブラウザインストール（Chromium 推奨）
uv run playwright install chromium
# もしくは全ブラウザ
uv run playwright install

# トレース/動画/スクリーンショット保存先の権限確認（必要に応じて）
# Linux の場合に追加の OS 依存パッケージが必要となることがあります（下記参照）。
```

Linux で必要になりがちな依存パッケージ（例）:

```bash
# Debian/Ubuntu 系の例
sudo apt-get update
sudo apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
  libxkbcommon0 libxcomposite1 libxrandr2 libxdamage1 libgbm1 libasound2 \
  libxshmfence1 libpango-1.0-0 libpangocairo-1.0-0 libgtk-3-0 fonts-liberation \
  libx11-xcb1 libxcursor1
```

WSL2 での注意:

- `E2E_HEADED=1` で GUI 表示する場合、X サーバ設定が必要です。ヘッドレス実行（`E2E_HEADED` 未設定）を推奨。
- ファイルパスの改行コードや権限に注意してください。

$2

- **テストキャプチャ**: Playwright MCP でユーザー操作を記録
- **テスト生成**: OpenAI Agents SDK で記録から Playwright テストコードを合成
- **テスト解析**: 失敗原因を分析し修正案を提示（セレクタ更新などを自動適用）
- **テスト保管**: ローカル JSON ベースのプロジェクト/テスト階層で管理

ストレージ構造例:

```
data/projects/{project_id}/
├── metadata.json          # プロジェクト設定
├── tests/                 # 生成された Playwright テスト
├── cache/                 # セレクタやパターンのキャッシュ
└── history/               # テストのバージョン履歴
```

最近の変更:

更新履歴は `IMPLEMENTATION_HISTORY.md` に移動しました。今後の更新内容もそちらに記載します。
詳しくは `IMPLEMENTATION_HISTORY.md` を参照してください。

## 開発ワークフロー（厳格 TDD）

本リポジトリは `CLAUDE.md` に定義された 4 フェーズ・TDD 方針に従います。要点のみ抜粋します（詳細は `CLAUDE.md` を参照）。

- フェーズ: Explore → Plan → Implement → Commit（実装前に必ず計画とテスト作成）
- テスト作成順: E2E → API → Unit（抽象 → 具体）
- 実装順: Unit → API → E2E（具体 → 抽象）
- 品質ゲート: Ruff/Pyright を常時実行。抑止コメントの使用は禁止
- 80%以上のカバレッジ必須

便利コマンド（抜粋）:

```bash
# 代表的な実行
nox -s test_unit
nox -s test_api
nox -s test_e2e

# 品質チェック（変更毎に）
nox -s lint
nox -s typing
nox -s format_code
nox -s coverage
```

## リポジトリ構成（概要）

```
project_root/
├── .claude/              # Claude Code 設定とカスタムコマンド
├── .github/workflows/    # CI
├── src/<library_name>/   # アプリケーションコード
├── tests/                # Unit/API/E2E テスト
├── docs/                 # ドキュメント（MkDocs）
├── constraints/          # nox 生成の制約ファイル
├── pyproject.toml        # 設定
├── noxfile.py            # nox タスク
├── README.md             # 本ファイル
└── CLAUDE.md             # 開発規約および詳細ガイド
```

## テスト用サイト（test_sites）

`test_sites/` には E2E テスト対象として使えるサンプル Web サイトが含まれます。セットアップや挙動の詳細は `test_sites/README.md` を参照してください。

- `landing_static/` — HTML/CSS/JS の静的ランディングページ
- `spa_tasks/` — バニラ JS + localStorage のタスク管理 SPA
- `shop_multipage/` — Service Worker でモック API/トークンセッションを提供するマルチページのショップ

ローカルでの提供例:

```bash
cd test_sites
python -m http.server 8000
# アクセス:
# http://localhost:8000/landing_static/
# http://localhost:8000/spa_tasks/
# http://localhost:8000/shop_multipage/
```

## OPENAI_API_KEY を使った実行チュートリアル

以下はサンプルサイトに対して実際にエージェントを動かす最小手順です。

1. 依存関係の準備

```bash
uv sync
```

2. テストサイトの起動

```bash
cd test_sites
python -m http.server 8000 &
cd -
```

3. 環境変数の設定（OpenAI の API キー）

```bash
export OPENAI_API_KEY="<your-api-key>"
# 任意: モデル、ブラウザ可視化など
export OPENAI_MODEL="gpt-5"
export E2E_HEADED=1        # ヘッドあり表示
export E2E_SLOWMO=250      # 動作を 250ms スローモー
```

4. プロジェクト作成とキャプチャ → 生成 → 実行（CLI）

```bash
# プロジェクト作成
uv run test-helper project create --project-name "demo-shop"

# キャプチャ（shop のログインシナリオ例）
uv run test-helper capture --project-name "demo-shop" \
  --url "http://localhost:8000/shop_multipage/" \
  --prompt "ログインページに移動し、email に 'user@example.com'、password に 'password' を入力してログインしてください。その後、Products ページで最初の商品をカートに追加してください。"

# テストコード生成
uv run test-helper generate --project-name "demo-shop"

# テスト実行（Playwright テストの実行）
uv run test-helper execute --project-name "demo-shop"
```

5. 直接 pytest でエージェント E2E を実行する場合

```bash
# 環境変数 OPENAI_API_KEY が必須。なければ tests/e2e_web は skip されます
pytest tests/e2e_web/ -m agent_browser -v
```

補足:

- 使える CLI サブコマンドや詳細オプションは `docs/guides/cli.md` を参照
- Temporal を用いたワークフロー実行は `docs/guides/temporal_agents.md` を参照

## ドキュメント

- インデックス: `docs/index.md`
- インストール: `docs/installation.md`
- クイックスタート: `docs/quickstart.md`
- 開発ガイド: `docs/development/contributing.md`, `docs/development/testing.md`, `docs/development/code-style.md`
- API/ガイド: `docs/guides/cli.md`, `docs/guides/restapi.md`, `docs/guides/temporal_agents.md`

## ライセンス

本プロジェクトは `LICENSE` の内容に従います。
