# Blog Platform - 6つのPython技術を統合したWebアプリケーション

このプロジェクトは、以下の6つの技術をすべてスクラッチで実装し、統合したブログプラットフォームです。

## 使用技術（6つ）

### 1. テキストエディタ (`editor.py`)
- コマンドパターンによるUndo/Redo機能
- TextBufferによる行ベースのテキスト管理
- 検索・置換機能
- 文字数・行数・単語数のリアルタイム統計

### 2. テンプレートエンジン (`template_engine.py`)
- テンプレートをPythonコードにコンパイル
- 変数展開、ループ、条件分岐をサポート
- ドット記法によるオブジェクトアクセス

### 3. 正規表現エンジン (`regex_engine.py`)
- ASTベースの正規表現パーサー
- バックトラッキングによるマッチング
- ブログ記事の検索機能に使用

### 4. Webサーバー (`webserver.py`)
- デコレータベースのルーティング
- GET/POSTリクエストのハンドリング
- 動的ルートと REST API の提供

### 5. Webブラウザ (`browser.py`)
- ソケットベースのHTTPクライアント
- HTMLパーサー（トークナイザ + ツリービルダー）
- DOMツリーの構築と操作
- テキストレンダラー（HTMLをターミナル表示用に変換）

### 6. データベース (`database.py`)
- イミュータブルバイナリツリーによるキー/バリューストア
- コピーオンライトによる効率的なメモリ使用
- ディスクへの永続化（pickle）

### + キャッシュ (`cache.py`) [データベース最適化]
- Redisライクなインメモリキャッシュ
- Cache-Asideパターンでデータベースの読み取りを高速化

## 機能

- ブログ記事の作成・編集（テキストエディタ）
- 記事のHTMLプレビュー（テンプレートエンジン）
- 正規表現による記事検索
- テキストブラウザ風プレビュー（Webブラウザ）
- DOM構造の可視化
- キャッシュによる高速化
- RESTful API
- 統計情報の表示

## 実行方法

Python 3.7以降（外部ライブラリ不要）

    cd blog_platform
    python3 app.py

テストの実行:

    python3 test_app.py

デモの実行:

    python3 demo.py

## エンドポイント

- http://127.0.0.1:8000/ - トップページ
- http://127.0.0.1:8000/posts - 記事一覧
- http://127.0.0.1:8000/editor - 新規記事作成（技術1）
- http://127.0.0.1:8000/post/post_0 - 記事表示（技術2）
- http://127.0.0.1:8000/preview/post_0 - テキストプレビュー（技術5）
- http://127.0.0.1:8000/search?q=Python - 記事検索（技術3）
- http://127.0.0.1:8000/api/stats - 統計(JSON)
- http://127.0.0.1:8000/api/posts - 記事一覧(JSON)

## プロジェクト構造

    blog_platform/
    app.py              - メインアプリケーション（6技術統合）
    editor.py           - 技術1: テキストエディタ
    template_engine.py  - 技術2: テンプレートエンジン
    regex_engine.py     - 技術3: 正規表現エンジン
    webserver.py        - 技術4: Webサーバー
    browser.py          - 技術5: Webブラウザ
    database.py         - 技術6: データベース
    cache.py            - DB最適化: キャッシュ
    test_app.py         - テストスイート
    demo.py             - インタラクティブデモ
    README.md           - このファイル

## 学習ポイント

- テキストエディタ: コマンドパターン、Undo/Redo、テキストバッファ管理
- テンプレートエンジン: コンパイラの基礎、コード生成、動的HTML
- 正規表現エンジン: AST構築、バックトラッキング、パターンマッチ
- Webサーバー: HTTPプロトコル、ソケット、ルーティング
- Webブラウザ: HTMLパース、DOMツリー、レンダリング
- データベース: イミュータブルデータ構造、永続化、B-Tree
- キャッシュ: Cache-Asideパターン、パフォーマンス最適化
- 統合: MVC設計、REST API、モジュール連携

## 参考資料

- AOSA Book - 500 Lines or Less (http://aosabook.org/en/500L/)
- Build Your Own X (https://build-your-own.org/)
- Web Browser Engineering (https://browser.engineering/)

教育目的のデモプロジェクトです。
