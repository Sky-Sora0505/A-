"""
Interactive Demo Script for Blog Platform
Demonstrates all 6 technologies without starting the web server:
1. テキストエディタ (editor.py)
2. テンプレートエンジン (template_engine.py)
3. 正規表現エンジン (regex_engine.py)
4. Webサーバー (webserver.py)
5. Webブラウザ (browser.py)
6. データベース (database.py)
"""
import json
import os
from database import Database
from cache import CacheServer, CacheClient
from regex_engine import regex_search, RegexMatcher
from template_engine import render_template
from browser import HTMLParser, TextRenderer, extract_text, extract_links
from editor import create_editor


def demo():
    print("\n" + "=" * 70)
    print("BLOG PLATFORM DEMO - 6つの技術の実演")
    print("=" * 70)
    
    # Cleanup old data
    if os.path.exists('demo.db'):
        os.remove('demo.db')
    
    # 1. DATABASE DEMO
    print("\n【1】イミュータブルバイナリツリーデータベース")
    print("-" * 70)
    db = Database('demo.db')
    
    print("✓ データベースを作成")
    print("✓ ブログ記事を保存...")
    
    posts = [
        {
            'id': 'post_1',
            'title': 'Pythonでデータベースを作る',
            'author': '山田太郎',
            'content': 'イミュータブルなバイナリツリーを使って、シンプルなデータベースを実装しました。',
            'tags': ['Python', 'Database', 'Tutorial']
        },
        {
            'id': 'post_2',
            'title': 'Redisの仕組みを理解する',
            'author': '佐藤花子',
            'content': 'インメモリキャッシュの実装方法とその利点について解説します。',
            'tags': ['Redis', 'Cache', 'Performance']
        },
        {
            'id': 'post_3',
            'title': '正規表現エンジンの実装',
            'author': '鈴木一郎',
            'content': 'バックトラッキングを使った正規表現マッチングの実装方法を紹介。',
            'tags': ['Regex', 'Compiler', 'Tutorial']
        }
    ]
    
    for post in posts:
        db.set(post['id'], json.dumps(post))
        print(f"  - 保存: {post['title']}")
    
    print(f"\n✓ 合計 {len(db.keys())} 件の記事を保存しました")
    
    # 2. CACHE DEMO
    print("\n【2】Redisライクなキャッシュサーバー")
    print("-" * 70)
    cache_server = CacheServer(host='127.0.0.1', port=6382)
    cache_server.start()
    cache = CacheClient(cache_server)
    
    print("✓ キャッシュサーバーを起動")
    print("✓ 記事をキャッシュに保存...")
    
    for post in posts:
        cache.set(f"post:{post['id']}", json.dumps(post))
        print(f"  - キャッシュ: {post['title']}")
    
    print(f"\n✓ キャッシュに {len(cache.keys())} 件のエントリがあります")
    
    # Retrieve from cache
    cached_post = json.loads(cache.get('post:post_1'))
    print(f"✓ キャッシュから取得: {cached_post['title']}")
    
    # 3. REGEX DEMO
    print("\n【3】正規表現エンジンで検索")
    print("-" * 70)
    
    search_terms = ['Tutorial', 'Python', 'Redis']
    
    for term in search_terms:
        print(f"\n検索語: '{term}'")
        found_posts = []
        
        for post in posts:
            content = post['title'] + ' ' + post['content']
            if regex_search(term.lower(), content.lower()):
                found_posts.append(post)
        
        print(f"✓ {len(found_posts)} 件の記事が見つかりました:")
        for post in found_posts:
            print(f"  - {post['title']} (by {post['author']})")
    
    # 4. TEMPLATE DEMO
    print("\n【4】テンプレートエンジンでHTML生成")
    print("-" * 70)
    
    template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ blog_title }}</title>
</head>
<body>
    <h1>{{ blog_title }}</h1>
    <p>合計 {{ post_count }} 件の記事</p>
    
    {% for post in posts %}
    <article>
        <h2>{{ post.title }}</h2>
        <p class="author">著者: {{ post.author }}</p>
        <p>{{ post.content }}</p>
        <div class="tags">
            {% for tag in post.tags %}
            <span class="tag">{{ tag }}</span>
            {% endfor %}
        </div>
    </article>
    {% endfor %}
</body>
</html>
"""
    
    context = {
        'blog_title': 'テクノロジーブログ',
        'post_count': len(posts),
        'posts': posts
    }
    
    html = render_template(template_str, context)
    print("✓ HTMLを生成しました")
    print(f"✓ 生成されたHTMLのサイズ: {len(html)} 文字")
    
    # Save to file
    demo_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(demo_dir, 'demo_output.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ demo_output.html に保存しました")
    
    # 5. INTEGRATION DEMO
    print("\n【5】全技術の統合デモ")
    print("-" * 70)
    
    print("\nシナリオ: ユーザーが記事を検索して表示")
    print()
    
    # Step 1: Search
    search_query = 'tutorial'
    print(f"1. ユーザーが '{search_query}' で検索")
    
    # Step 2: Check cache
    cache_key = f"search:{search_query}"
    cached_results = cache.get(cache_key)
    
    if cached_results:
        print("2. ✓ キャッシュにヒット！")
        search_results = json.loads(cached_results)
    else:
        print("2. キャッシュミス - データベースから検索")
        
        # Step 3: Search in database
        search_results = []
        for key, value in db.all_items():
            if key.startswith('post_'):
                post = json.loads(value)
                content = post['title'] + ' ' + post['content']
                if regex_search(search_query.lower(), content.lower()):
                    search_results.append(post)
        
        # Step 4: Cache results
        cache.set(cache_key, json.dumps(search_results))
        print("3. ✓ 検索結果をキャッシュに保存")
    
    print(f"4. ✓ {len(search_results)} 件の記事が見つかりました")
    
    # Step 5: Render with template
    result_template = """
<h1>検索結果: "{{ query }}"</h1>
<p>{{ result_count }} 件の記事が見つかりました</p>
{% for post in results %}
<div class="result">
    <h3>{{ post.title }}</h3>
    <p>{{ post.content }}</p>
</div>
{% endfor %}
"""
    
    result_html = render_template(result_template, {
        'query': search_query,
        'result_count': len(search_results),
        'results': search_results
    })
    
    print("5. ✓ テンプレートを使ってHTMLを生成")
    print()
    
    for post in search_results:
        print(f"  📄 {post['title']}")
        print(f"     著者: {post['author']}")
        print()
    
    # 6. BROWSER DEMO
    print("\n【6】Webブラウザ（HTMLパーサー + テキストレンダラー）")
    print("-" * 70)
    
    print("✓ HTMLをパースしてDOMツリーを構築...")
    parser = HTMLParser()
    dom = parser.parse(html)
    print(f"  ルートタグ: <{dom.tag}>")
    
    h2_nodes = dom.find_all('h2')
    print(f"  見つかった<h2>タグ: {len(h2_nodes)} 個")
    for h2 in h2_nodes:
        print(f"    - {h2.get_text().strip()}")
    
    links = extract_links(html)
    print(f"  抽出されたリンク: {len(links)} 個")
    
    print("\n✓ テキストブラウザ風にレンダリング...")
    text_preview = extract_text(result_html)
    print("  --- テキストプレビュー ---")
    for line in text_preview.split('\n')[:10]:
        if line.strip():
            print(f"  | {line.strip()}")
    print("  --- ここまで ---")
    
    # 7. EDITOR DEMO
    print("\n【7】テキストエディタ（コマンドパターン + Undo/Redo）")
    print("-" * 70)
    
    editor = create_editor(text=posts[0]['content'], filename='post_1.md')
    print(f"✓ エディタを作成: {editor.filename}")
    
    stats_editor = editor.get_statistics()
    print(f"  行数: {stats_editor['lines']}")
    print(f"  文字数: {stats_editor['characters']}")
    print(f"  単語数: {stats_editor['words']}")
    
    search_results_editor = editor.search('データベース')
    print(f"\n✓ 'データベース' を検索: {len(search_results_editor)} 件ヒット")
    
    print("✓ エディタ機能: テキスト挿入、削除、検索、置換、Undo/Redo")
    
    # 8. STATISTICS
    print("\n【8】統計情報")
    print("-" * 70)
    
    stats = {
        'データベースのキー数': len(db.keys()),
        'キャッシュのエントリ数': len(cache.keys()),
        '記事の総数': len(posts),
        '使用している6つの技術': [
            'テキストエディタ (editor.py)',
            'テンプレートエンジン (template_engine.py)',
            '正規表現エンジン (regex_engine.py)',
            'Webサーバー (webserver.py)',
            'Webブラウザ (browser.py)',
            'データベース (database.py)',
        ]
    }
    
    for key, value in stats.items():
        if isinstance(value, list):
            print(f"\n{key}:")
            for i, item in enumerate(value, 1):
                print(f"  {i}. {item}")
        else:
            print(f"{key}: {value}")
    
    # Cleanup
    cache_server.stop()
    
    print("\n" + "=" * 70)
    print("デモ完了！")
    print("=" * 70)
    print("\n次のステップ:")
    print("  python3 app.py を実行してWebサーバーを起動")
    print("  ブラウザで http://127.0.0.1:8000 にアクセス")
    print()


if __name__ == '__main__':
    demo()
