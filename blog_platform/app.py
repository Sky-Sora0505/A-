"""
Blog Platform Application
6つのPython技術を統合したWebアプリケーション

====================================================
統合された6つの技術:
1. テキストエディタ (editor.py)     - 記事の作成・編集
2. テンプレートエンジン (template_engine.py) - HTML動的生成
3. 正規表現エンジン (regex_engine.py)      - 記事検索
4. Webサーバー (webserver.py)             - HTTPリクエスト処理
5. Webブラウザ (browser.py)              - HTTPクライアント・HTMLパース
6. データベース (database.py)             - データ永続化
====================================================

※ キャッシュ (cache.py) はデータベース層の最適化として併用

学習ポイント:
- 複数の独立したモジュールを統合するアーキテクチャ設計
- MVC (Model-View-Controller) パターンの実践
- REST API 設計とルーティング
- キャッシュ戦略（Cache-Aside パターン）
- 各レイヤーの責務分離

"""
#ターミナルで実行
#サーバー切断lsof -ti :8000 | xargs kill -9


# ======================================
# インポート: 6つの技術モジュール
# ======================================
from database import Database                                    # 技術6: データベース
from cache import CacheServer, CacheClient                       # (DB最適化: キャッシュ)
from regex_engine import regex_search                            # 技術3: 正規表現エンジン
from template_engine import (Template, HTML_TEMPLATE,            # 技術2: テンプレートエンジン
                             BLOG_POST_TEMPLATE, BLOG_LIST_TEMPLATE)
from webserver import WebServer                                  # 技術4: Webサーバー
from browser import Browser, HTMLParser, extract_text             # 技術5: Webブラウザ
from editor import (TextEditor, create_editor,                   # 技術1: テキストエディタ
                    render_editor_html, EDITOR_PAGE_TEMPLATE)

import json
from datetime import datetime
import os


class BlogPlatform:
    """ブログプラットフォーム: 6つの技術の統合アプリケーション
    
    アーキテクチャ概要:
    ┌─────────────────────────────────────────────┐
    │              BlogPlatform (app.py)           │
    │   Controller: リクエスト処理・ビジネスロジック  │
    ├─────────────────────────────────────────────┤
    │  WebServer    │ Browser     │ Editor        │
    │  (技術4)      │ (技術5)     │ (技術1)       │
    │  HTTPサーバー  │ HTTPクライアント│ テキスト編集  │
    ├─────────────────────────────────────────────┤
    │  Template     │ Regex       │               │
    │  (技術2)      │ (技術3)     │               │
    │  HTML生成     │ 検索処理     │               │
    ├─────────────────────────────────────────────┤
    │  Database (技術6) + Cache (最適化)           │
    │  データ永続化 + インメモリキャッシュ           │
    └─────────────────────────────────────────────┘
    """
    
    def __init__(self, db_path='blog_data.db', port=8000):
        """プラットフォームを初期化
        
        各技術コンポーネントをインスタンス化して連携させる。
        """
        # --- 技術6: データベース ---
        self.db = Database(db_path)
        
        # --- キャッシュ (DB最適化) ---
        self.cache_server = CacheServer(host='127.0.0.1', port=6379)
        self.cache_server.start()
        self.cache = CacheClient(self.cache_server)
        
        # --- 技術4: Webサーバー ---
        self.web = WebServer(host='127.0.0.1', port=port)
        
        # --- 技術5: Webブラウザ (テスト・プレビュー用) ---
        self.browser = Browser(base_url=f'http://127.0.0.1:{port}')
        
        # --- 技術1: テキストエディタ (記事編集用) ---
        self.editors = {}  # post_id -> TextEditor のマッピング
        
        # 初期データの投入
        self._initialize_db()
        
        # ルーティングの設定
        self._setup_routes()
    
    # ==========================================================
    # 初期化
    # ==========================================================
    
    def _initialize_db(self):
        """データベースにサンプルデータを投入（技術6: Database）"""
        try:
            self.db.get('post_counter')
        except KeyError:
            self.db.set('post_counter', 0)
            
            sample_posts = [
                {
                    'title': 'Pythonでデータベースを自作する',
                    'author': '山田太郎',
                    'content': ('イミュータブルなバイナリツリーを使って、'
                                'キー/バリューストアを実装する方法を解説します。\n\n'
                                'データ構造の不変性を保つことで、並行処理での安全性が高まります。'
                                'また、コピーオンライトにより効率的なメモリ使用が可能です。'),
                    'tags': ['Python', 'Database', 'Tutorial'],
                    'date': '2024-01-01'
                },
                {
                    'title': 'テンプレートエンジンの仕組み',
                    'author': '佐藤花子',
                    'content': ('テンプレートをPythonコードにコンパイルする手法を紹介します。\n\n'
                                'Jinja2やDjangoテンプレートの内部で使われている技術を、'
                                'ゼロから実装して理解を深めましょう。変数展開、ループ、条件分岐を'
                                'サポートするテンプレートエンジンを作ります。'),
                    'tags': ['Python', 'Template', 'Web開発'],
                    'date': '2024-01-15'
                },
                {
                    'title': '正規表現エンジンを作って学ぶ',
                    'author': '鈴木一郎',
                    'content': ('正規表現の内部実装を理解するために、'
                                'パーサーとマッチャーをスクラッチで作成します。\n\n'
                                'ASTの構築、バックトラッキングアルゴリズム、'
                                '量子化子(*, +, ?)の実装方法を学びます。'),
                    'tags': ['Python', 'Regex', 'Compiler'],
                    'date': '2024-02-01'
                },
            ]
            
            for post in sample_posts:
                self._create_post(post)
    
    # ==========================================================
    # ルーティング設定（技術4: WebServer）
    # ==========================================================
    
    def _setup_routes(self):
        """URLルーティングの設定（技術4: デコレータベースルーティング）"""
        
        @self.web.route('/')
        def index(request, query):
            return self._render_index()
        
        @self.web.route('/posts')
        def list_posts(request, query):
            return self._render_post_list()
        
        @self.web.route('/post/<id>')
        def view_post(request, query):
            post_id = request.path.split('/')[-1]
            return self._render_post(post_id)
        
        @self.web.route('/search')
        def search(request, query):
            search_query = query.get('q', [''])[0]
            return self._render_search_results(search_query)
        
        @self.web.route('/editor')
        def new_editor(request, query):
            """新規記事エディタ（技術1: テキストエディタ）"""
            return self._render_editor_page()
        
        @self.web.route('/editor/<id>')
        def edit_post(request, query):
            """記事編集エディタ（技術1: テキストエディタ）"""
            post_id = request.path.split('/')[-1]
            return self._render_editor_page(post_id)
        
        @self.web.route('/preview/<id>')
        def preview_post(request, query):
            """記事プレビュー（技術5: ブラウザのHTMLパース）"""
            post_id = request.path.split('/')[-1]
            return self._render_preview(post_id)
        
        # --- APIルート ---
        
        @self.web.route('/api/posts', method='GET')
        def api_list_posts(request, query):
            return self._get_all_posts()
        
        @self.web.route('/api/post', method='POST')
        def api_create_post(request, data):
            return self._create_post(data)
        
        @self.web.route('/api/post/<id>', method='GET')
        def api_get_post(request, query):
            post_id = request.path.split('/')[-1]
            return self._get_post(post_id)
        
        @self.web.route('/api/search', method='GET')
        def api_search(request, query):
            search_query = query.get('q', [''])[0]
            return self._search_posts(search_query)
        
        @self.web.route('/api/stats', method='GET')
        def api_stats(request, query):
            return self._get_stats()
        
        @self.web.route('/post/create', method='POST')
        def create_post_form(request, data):
            """フォームからの記事作成"""
            return self._handle_post_form(data)
    
    # ==========================================================
    # 記事の CRUD 操作（技術6: Database + キャッシュ）
    # ==========================================================
    
    def _create_post(self, post_data):
        """記事を作成してデータベースに保存（技術6）
        
        Cache-Aside パターンでキャッシュを無効化。
        """
        counter = self.db.get('post_counter')
        post_id = f"post_{counter}"
        counter += 1
        self.db.set('post_counter', counter)
        
        if isinstance(post_data, dict):
            post = post_data.copy()
        else:
            post = {}
            for key, value in post_data.items():
                post[key] = value[0] if isinstance(value, list) else value
        
        if 'tags' in post and isinstance(post['tags'], str):
            post['tags'] = [t.strip() for t in post['tags'].split(',') if t.strip()]
        
        if 'date' not in post:
            post['date'] = datetime.now().strftime('%Y-%m-%d')
        if 'id' not in post:
            post['id'] = post_id
        
        self.db.set(post_id, json.dumps(post))
        self.cache.delete('all_posts')
        
        return {'success': True, 'id': post_id, 'post': post}
    
    def _get_post(self, post_id):
        """記事を取得（Cache-Aside パターン: キャッシュ → DB）"""
        cached = self.cache.get(f"post:{post_id}")
        if cached:
            return json.loads(cached)
        
        try:
            post_json = self.db.get(post_id)
            post = json.loads(post_json)
            self.cache.set(f"post:{post_id}", post_json)
            return post
        except KeyError:
            return None
    
    def _get_all_posts(self):
        """全記事を取得（キャッシュ付き）"""
        cached = self.cache.get('all_posts')
        if cached:
            return json.loads(cached)
        
        posts = []
        for key, value in self.db.all_items():
            if key.startswith('post_') and key != 'post_counter':
                try:
                    post = json.loads(value)
                    posts.append(post)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        posts.sort(key=lambda x: x.get('date', ''), reverse=True)
        self.cache.set('all_posts', json.dumps(posts))
        
        return posts
    
    # ==========================================================
    # 検索機能（技術3: 正規表現エンジン）
    # ==========================================================
    
    def _search_posts(self, query):
        """正規表現エンジンで記事を検索（技術3）"""
        if not query:
            return []
        
        posts = self._get_all_posts()
        results = []
        
        for post in posts:
            title_match = regex_search(query.lower(), post.get('title', '').lower())
            content_match = regex_search(query.lower(), post.get('content', '').lower())
            
            if title_match or content_match:
                results.append(post)
        
        return results
    
    # ==========================================================
    # テキストエディタ機能（技術1: TextEditor）
    # ==========================================================
    
    def _get_editor(self, post_id=None):
        """記事用テキストエディタを取得/作成（技術1）"""
        if post_id and post_id in self.editors:
            return self.editors[post_id]
        
        if post_id:
            post = self._get_post(post_id)
            if post:
                editor = create_editor(
                    text=post.get('content', ''),
                    filename=f"{post_id}.md"
                )
                self.editors[post_id] = editor
                return editor
        
        return create_editor(text='', filename='new_post.md')
    
    def _handle_post_form(self, data):
        """エディタからのフォーム送信を処理（技術1 + 技術6）"""
        post_data = {}
        for key, value in data.items():
            post_data[key] = value[0] if isinstance(value, list) else value
        
        if 'tags' in post_data and isinstance(post_data['tags'], str):
            post_data['tags'] = [t.strip() for t in post_data['tags'].split(',') if t.strip()]
        
        result = self._create_post(post_data)
        
        editor = create_editor(text=post_data.get('content', ''))
        stats = editor.get_statistics()
        
        template = Template(HTML_TEMPLATE)
        template.compile()
        
        content = f"""
        <div style="text-align:center; padding: 40px;">
            <h1>✅ 記事を作成しました！</h1>
            <p>ID: {result['id']}</p>
            <p>文字数: {stats['characters']} | 行数: {stats['lines']} | 単語数: {stats['words']}</p>
            <p style="margin-top: 20px;">
                <a href="/post/{result['id']}">記事を見る</a> |
                <a href="/editor">新しい記事を書く</a> |
                <a href="/posts">記事一覧</a>
            </p>
        </div>
        """
        
        return template.render({'title': '記事作成完了', 'content': content})
    
    # ==========================================================
    # HTMLレンダリング（技術2: テンプレートエンジン）
    # ==========================================================
    
    def _render_index(self):
        """トップページ（技術2: テンプレートエンジン）"""
        posts = self._get_all_posts()[:5]
        
        content = """
        <div class="header">
            <h1>📝 ブログプラットフォーム</h1>
            <p>6つのPython技術で構築されたWebアプリケーション</p>
            <nav style="margin: 15px 0;">
                <a href="/posts">📚 記事一覧</a> |
                <a href="/editor">✏️ 新規作成</a> |
                <a href="/search?q=Python">🔍 検索</a> |
                <a href="/api/stats">📊 統計</a>
            </nav>
            <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3>🔧 使用技術</h3>
                <ol>
                    <li><b>テキストエディタ</b> - 記事の作成・編集（Undo/Redo対応）</li>
                    <li><b>テンプレートエンジン</b> - HTML動的生成（変数展開・ループ・条件分岐）</li>
                    <li><b>正規表現エンジン</b> - 記事検索（AST構築・バックトラッキング）</li>
                    <li><b>Webサーバー</b> - HTTPリクエスト処理（ルーティング・REST API）</li>
                    <li><b>Webブラウザ</b> - HTMLパース・テキストレンダリング</li>
                    <li><b>データベース</b> - イミュータブル二分木による永続化</li>
                </ol>
            </div>
        </div>
        <div class="posts"><h2>最新の記事</h2>
        """
        
        for post in posts:
            tags_html = ''.join(
                f'<span class="tag">{tag}</span>' for tag in post.get('tags', [])
            )
            content += f"""
            <div class="post-preview" style="border:1px solid #ddd;padding:15px;margin:10px 0;border-radius:8px;">
                <h3><a href="/post/{post['id']}">{post['title']}</a></h3>
                <div class="meta">By {post.get('author', '匿名')} | {post.get('date', '')}</div>
                <p>{post.get('content', '')[:150]}...</p>
                <div>{tags_html}</div>
                <div style="margin-top:8px;">
                    <a href="/editor/{post['id']}">✏️ 編集</a> |
                    <a href="/preview/{post['id']}">👁 プレビュー</a>
                </div>
            </div>
            """
        
        content += "</div>"
        
        template = Template(HTML_TEMPLATE)
        template.compile()
        return template.render({'title': 'ブログプラットフォーム', 'content': content})
    
    def _render_post_list(self):
        """記事一覧ページ（技術2）"""
        posts = self._get_all_posts()
        
        content = """
        <nav><a href="/">← ホーム</a> | <a href="/editor">✏️ 新規作成</a></nav>
        <h1>📚 全記事一覧</h1><div class='posts'>
        """
        
        for post in posts:
            tags_html = ''.join(
                f'<span class="tag">{tag}</span>' for tag in post.get('tags', [])
            )
            content += f"""
            <div class="post-preview" style="border:1px solid #ddd;padding:15px;margin:10px 0;border-radius:8px;">
                <h3><a href="/post/{post['id']}">{post['title']}</a></h3>
                <div class="meta">By {post.get('author', '匿名')} | {post.get('date', '')}</div>
                <div>{tags_html}</div>
                <div style="margin-top:8px;">
                    <a href="/editor/{post['id']}">✏️ 編集</a> |
                    <a href="/preview/{post['id']}">👁 プレビュー</a>
                </div>
            </div>
            """
        
        content += "</div>"
        
        template = Template(HTML_TEMPLATE)
        template.compile()
        return template.render({'title': '全記事一覧', 'content': content})
    
    def _render_post(self, post_id):
        """記事詳細ページ（技術2: テンプレートエンジン）"""
        post = self._get_post(post_id)
        
        if not post:
            return "<h1>記事が見つかりません</h1>"
        
        template = Template(BLOG_POST_TEMPLATE)
        template.compile()
        post_html = template.render(post)
        
        nav = f"""
        <nav style="margin-bottom:15px;">
            <a href="/">← ホーム</a> |
            <a href="/posts">記事一覧</a> |
            <a href="/editor/{post_id}">✏️ 編集</a> |
            <a href="/preview/{post_id}">👁 テキストプレビュー</a>
        </nav>
        """
        
        page_template = Template(HTML_TEMPLATE)
        page_template.compile()
        return page_template.render({'title': post['title'], 'content': nav + post_html})
    
    def _render_search_results(self, query):
        """検索結果ページ（技術2 + 技術3）"""
        results = self._search_posts(query)
        
        content = f"""
        <nav><a href="/">← ホーム</a></nav>
        <h1>🔍 検索結果: "{query}"</h1>
        <p>{len(results)} 件の記事が見つかりました</p>
        <form action="/search" method="GET" style="margin:15px 0;">
            <input type="text" name="q" value="{query}" 
                   style="padding:8px;width:300px;border:1px solid #ccc;border-radius:4px;">
            <button type="submit" style="padding:8px 16px;">検索</button>
        </form>
        <div class='posts'>
        """
        
        for post in results:
            content += f"""
            <div class="post-preview" style="border:1px solid #ddd;padding:15px;margin:10px 0;border-radius:8px;">
                <h3><a href="/post/{post['id']}">{post['title']}</a></h3>
                <div class="meta">By {post.get('author', '匿名')} | {post.get('date', '')}</div>
                <p>{post.get('content', '')[:200]}...</p>
            </div>
            """
        
        content += "</div>"
        
        template = Template(HTML_TEMPLATE)
        template.compile()
        return template.render({'title': f'検索: {query}', 'content': content})
    
    def _render_editor_page(self, post_id=None):
        """記事エディタページ（技術1 + 技術2）"""
        editor = self._get_editor(post_id)
        
        post = None
        if post_id:
            post = self._get_post(post_id)
        
        context = {
            'page_title': f'記事の編集: {post["title"]}' if post else '新しい記事を作成',
            'form_action': '/post/create',
            'post_title': post.get('title', '') if post else '',
            'post_author': post.get('author', '') if post else '',
            'post_content': post.get('content', '') if post else '',
            'post_tags': ', '.join(post.get('tags', [])) if post else '',
            'submit_text': '更新する' if post else '投稿する',
        }
        
        template = Template(EDITOR_PAGE_TEMPLATE)
        template.compile()
        return template.render(context)
    
    # ==========================================================
    # プレビュー機能（技術5: Webブラウザ）
    # ==========================================================
    
    def _render_preview(self, post_id):
        """記事のテキストプレビュー（技術5: HTMLパーサー + テキストレンダラー）"""
        post = self._get_post(post_id)
        if not post:
            return "<h1>記事が見つかりません</h1>"
        
        # 記事をHTMLにレンダリング（技術2）
        post_template = Template(BLOG_POST_TEMPLATE)
        post_template.compile()
        post_html = post_template.render(post)
        
        # 技術5: HTMLパーサーでDOMツリー構築 + テキストレンダリング
        parser = HTMLParser()
        dom = parser.parse(post_html)
        text_preview = extract_text(post_html)
        
        # DOM構造の可視化
        dom_info = self._visualize_dom(dom)
        
        # リンク抽出（技術5）
        links = []
        for anchor in dom.find_all('a'):
            text = anchor.get_text()
            href = anchor.get_attribute('href') or ''
            links.append(f'  <li><a href="{href}">{text}</a> → {href}</li>')
        links_html = '\n'.join(links) if links else '  <li>リンクなし</li>'
        
        content = f"""
        <nav>
            <a href="/">← ホーム</a> |
            <a href="/post/{post_id}">通常表示</a> |
            <a href="/editor/{post_id}">✏️ 編集</a>
        </nav>
        
        <h1>👁 テキストプレビュー: {post['title']}</h1>
        <p style="color:#666;">技術5: Webブラウザ（HTMLパーサー + テキストレンダラー）によるプレビュー</p>
        
        <h2>📄 テキスト表示（テキストブラウザ風）</h2>
        <pre style="background:#1e1e2e;color:#cdd6f4;padding:20px;border-radius:8px;white-space:pre-wrap;font-family:monospace;line-height:1.6;">{text_preview}</pre>
        
        <h2>🌳 DOM ツリー構造</h2>
        <pre style="background:#f5f5f5;padding:20px;border-radius:8px;font-family:monospace;font-size:13px;overflow-x:auto;">{dom_info}</pre>
        
        <h2>🔗 抽出されたリンク</h2>
        <ul>{links_html}</ul>
        """
        
        template = Template(HTML_TEMPLATE)
        template.compile()
        return template.render({'title': f'プレビュー: {post["title"]}', 'content': content})
    
    def _visualize_dom(self, node, indent=0):
        """DOMツリーを可視化"""
        prefix = '  ' * indent
        lines = []
        
        if node.text:
            text = node.text[:50] + '...' if len(node.text) > 50 else node.text
            lines.append(f'{prefix}📝 TEXT: "{text}"')
        elif node.tag:
            attrs = ''
            if node.attributes:
                attrs = ' ' + ' '.join(f'{k}="{v}"' for k, v in node.attributes.items())
            lines.append(f'{prefix}🏷️  <{node.tag}{attrs}>')
            for child in node.children:
                lines.append(self._visualize_dom(child, indent + 1))
            lines.append(f'{prefix}🏷️  </{node.tag}>')
        
        return '\n'.join(lines)
    
    # ==========================================================
    # 統計情報
    # ==========================================================
    
    def _get_stats(self):
        """プラットフォームの統計情報"""
        posts = self._get_all_posts()
        
        return {
            'total_posts': len(posts),
            'cache_keys': len(self.cache.keys()),
            'database_keys': len(self.db.keys()),
            'active_editors': len(self.editors),
            'technologies': {
                '1_テキストエディタ': 'editor.py - 記事作成・編集（Undo/Redo対応）',
                '2_テンプレートエンジン': 'template_engine.py - HTML動的生成',
                '3_正規表現エンジン': 'regex_engine.py - 記事検索',
                '4_Webサーバー': 'webserver.py - HTTPリクエスト処理',
                '5_Webブラウザ': 'browser.py - HTMLパース・テキストレンダリング',
                '6_データベース': 'database.py - イミュータブル二分木',
            }
        }
    
    # ==========================================================
    # サーバー起動
    # ==========================================================
    
    def start(self):
        """ブログプラットフォームを起動"""
        print("=" * 60)
        print("📝 BLOG PLATFORM - 6つのPython技術で構築")
        print("=" * 60)
        print()
        print("使用技術:")
        print("  1. ✅ テキストエディタ     (editor.py)")
        print("  2. ✅ テンプレートエンジン  (template_engine.py)")
        print("  3. ✅ 正規表現エンジン     (regex_engine.py)")
        print("  4. ✅ Webサーバー         (webserver.py)")
        print("  5. ✅ Webブラウザ         (browser.py)")
        print("  6. ✅ データベース         (database.py)")
        print()
        base = f"http://{self.web.host}:{self.web.port}"
        print("エンドポイント:")
        print(f"  {base}/           - トップページ")
        print(f"  {base}/posts      - 記事一覧")
        print(f"  {base}/editor     - 新規記事作成")
        print(f"  {base}/search?q=  - 検索")
        print(f"  {base}/api/stats  - 統計(JSON)")
        print()
        print("Ctrl+C でサーバーを停止")
        print("=" * 60)
        print()
        
        self.web.start()


if __name__ == '__main__':
    app = BlogPlatform(port=8000)
    app.start()
