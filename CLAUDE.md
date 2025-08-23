# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Yakusoku Keeper は MCP (Model Context Protocol) サーバーで、入力回数や経過時間に基づいてLLMにルールベースのプロンプトを提供します。特定の間隔でトリガーされるルールを設定することで、LLMの動作の一貫性を保つことができます。

## アーキテクチャ

### メインコンポーネント

**yakusoku_keeper.py** - FastMCPを使用したMCPサーバーの実装
- `YakusokuKeeper`クラス: ルールの読み込み、入力カウント、時間追跡を管理
- MCPツール:
  - `initial_instructions()`: Claude Codeに対する高優先度の指示（呼び出し必須ルールの説明）
  - `get_rules()`: 現在の入力回数と経過時間に一致するルールを返す
  - `reset()`: カウンターとタイマーをリセット
  - `add_rule()`: 設定ファイルに新しいルールを追加
  - `remove_rule()`: 設定ファイルから既存ルールを削除

### 設定システム

2つのYAML設定ファイルからルールを読み込み（デフォルト動作が逆転）:
- `~/.yakusoku/yakusoku_config.yml` - **全てコメントアウトされた状態**で作成
- `.yakusoku/project.yml` - **有効なルール**が記載された状態で作成

サポートされるルールタイプ:
- `first`: 最初の入力時に適用されるルール
- `every_N_inputs`: N回の入力ごとにトリガーされるルール  
- `every_N_minutes`: N分経過後にトリガーされるルール

## 開発コマンド

```bash
# MCPサーバーの起動
python yakusoku_keeper.py

# テスト実行
python test_mcp_server.py          # 基本機能テスト
python test_load_rules.py          # ルール読み込みテスト
python test_add_rule.py            # ルール追加テスト
python test_remove_rule.py         # ルール削除テスト
python test_time_based.py          # 時間ベースルールテスト（61秒）

# 依存関係のインストール
pip install fastmcp mcp PyYAML
```

## Claude Code接続設定

```json
"yakusoku_keeper": {
  "type": "stdio",
  "command": "python",
  "args": ["C:\\path\\to\\yakusoku_keeper.py"],
  "env": {}
}
```

## 主要な依存関係

- **fastmcp** (2.11.3) - MCPサーバーフレームワーク
- **mcp** (1.13.0) - MCPクライアントライブラリ  
- **PyYAML** (6.0.2) - YAML設定ファイルのパース

## 実装上の重要なポイント

- **強制ルール適用**: `initial_instructions()`ツールがClaude Codeに毎回`get_rules()`を呼び出すよう指示
- ルールは`get_rules()`が呼ばれるたびに再読み込みされ、設定ファイルの変更が即座に反映
- デフォルト設定: プロジェクト固有ルールが有効、グローバルルールはコメントアウト
- 動的管理: MCPツールでリアルタイムにルール追加・削除可能
- 自動クリーンアップ: 空のルールセクションは自動削除