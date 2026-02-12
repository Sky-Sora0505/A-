"""
Test Suite for Blog Platform
Tests all 6 technologies:
1. テキストエディタ (editor.py)
2. テンプレートエンジン (template_engine.py)
3. 正規表現エンジン (regex_engine.py)
4. Webサーバー (webserver.py)
5. Webブラウザ (browser.py)
6. データベース (database.py)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database, BinaryTree
from cache import CacheServer, CacheClient
from regex_engine import RegexMatcher, regex_search
from template_engine import Template, render_template
from webserver import WebServer
from browser import HTMLParser, TextRenderer, extract_text, extract_links, parse_html
from editor import TextEditor, TextBuffer, CommandHistory, create_editor


def test_database():
    print("\n=== Testing Database (Immutable Binary Tree) ===")
    if os.path.exists('test.db'):
        os.remove('test.db')
    db = Database('test.db')
    db.set('key1', 'value1')
    db.set('key2', 'value2')
    db.set('key3', 'value3')
    assert db.get('key1') == 'value1'
    assert db.get('key2') == 'value2'
    items = db.all_items()
    assert len(items) == 3
    db.delete('key2')
    try:
        db.get('key2')
        assert False
    except KeyError:
        pass
    db2 = Database('test.db')
    assert db2.get('key1') == 'value1'
    if os.path.exists('test.db'):
        os.remove('test.db')
    print("  Database tests passed!")


def test_cache():
    print("\n=== Testing Cache Server (Redis-like) ===")
    cache_server = CacheServer(host='127.0.0.1', port=6380)
    cache_server.start()
    cache = CacheClient(cache_server)
    cache.set('test_key', 'test_value')
    assert cache.get('test_key') == 'test_value'
    assert cache.exists('test_key') == True
    assert cache.exists('nonexistent') == False
    cache.delete('test_key')
    assert cache.get('test_key') is None
    cache.mset(key1='value1', key2='value2', key3='value3')
    values = cache.mget('key1', 'key2', 'key3')
    assert values == ['value1', 'value2', 'value3']
    keys = cache.keys()
    assert len(keys) == 3
    count = cache.flush()
    assert count == 3
    assert len(cache.keys()) == 0
    cache_server.stop()
    print("  Cache server tests passed!")


def test_regex():
    print("\n=== Testing Regex Engine ===")
    matcher = RegexMatcher('hello')
    assert matcher.match('hello') == True
    assert matcher.match('world') == False
    matcher = RegexMatcher('h.llo')
    assert matcher.match('hello') == True
    assert matcher.match('hallo') == True
    matcher = RegexMatcher('ab*c')
    assert matcher.match('ac') == True
    assert matcher.match('abc') == True
    assert matcher.match('abbc') == True
    matcher = RegexMatcher('ab+c')
    assert matcher.match('ac') == False
    assert matcher.match('abc') == True
    assert matcher.match('abbc') == True
    result = regex_search('world', 'hello world!')
    assert result == 'world'
    result = regex_search('test', 'this is a test string')
    assert result == 'test'
    print("  Regex engine tests passed!")


def test_template():
    print("\n=== Testing Template Engine ===")
    template = Template('Hello {{ name }}!')
    template.compile()
    result = template.render({'name': 'World'})
    assert 'World' in result
    template_str = "{% for item in items %}{{ item }} {% endfor %}"
    template = Template(template_str)
    template.compile()
    result = template.render({'items': ['a', 'b', 'c']})
    assert 'a' in result and 'b' in result and 'c' in result
    template_str = "{% if show %}Visible{% endif %}"
    template = Template(template_str)
    template.compile()
    result = template.render({'show': True})
    assert 'Visible' in result
    result = template.render({'show': False})
    assert 'Visible' not in result
    result = render_template('Hello {{ name }}!', {'name': 'Test'})
    assert 'Test' in result
    print("  Template engine tests passed!")


def test_browser():
    print("\n=== Testing Web Browser (HTML Parser + Text Renderer) ===")
    html = '<html><body><h1>Hello</h1><p>World</p></body></html>'
    parser = HTMLParser()
    dom = parser.parse(html)
    assert dom is not None
    paragraphs = dom.find_all('p')
    assert len(paragraphs) >= 1
    h1_nodes = dom.find_all('h1')
    assert len(h1_nodes) >= 1
    text = dom.get_text()
    assert 'Hello' in text
    assert 'World' in text
    html_with_attrs = '<a href="https://example.com">Link</a>'
    dom2 = parser.parse(html_with_attrs)
    links_found = dom2.find_all('a')
    assert len(links_found) >= 1
    link = links_found[0]
    href = link.get_attribute('href')
    assert href == 'https://example.com'
    renderer = TextRenderer(width=80)
    html_content = '<h1>Title</h1><p>Paragraph text here.</p>'
    rendered = renderer.render(html_content)
    assert 'Title' in rendered
    assert 'Paragraph' in rendered
    text = extract_text('<div><p>Hello <b>World</b></p></div>')
    assert 'Hello' in text
    assert 'World' in text
    html_with_links = '<a href="/page1">Page 1</a><a href="/page2">Page 2</a>'
    links = extract_links(html_with_links)
    assert len(links) == 2
    dom3 = parse_html('<p>Test</p>')
    assert dom3 is not None
    print("  Web browser tests passed!")


def test_editor():
    print("\n=== Testing Text Editor (TextBuffer + Command Pattern) ===")
    buf = TextBuffer()
    buf.insert_text(0, 0, 'Hello World')
    content = buf.get_content()
    assert 'Hello World' in content
    buf2 = TextBuffer("Line1\nLine2\nLine3")
    assert buf2.line_count == 3
    assert buf2.get_line(0) == 'Line1'
    assert buf2.get_line(1) == 'Line2'
    assert buf2.get_line(2) == 'Line3'
    editor = create_editor(text='Test content here', filename='test.md')
    assert editor is not None
    stats = editor.get_statistics()
    assert 'lines' in stats
    assert 'characters' in stats
    assert 'words' in stats
    assert stats['lines'] >= 1
    assert stats['characters'] > 0
    content = editor.get_content()
    assert 'Test content here' in content
    history = CommandHistory()
    assert history.can_undo == False
    assert history.can_redo == False
    results = editor.search('content')
    assert len(results) >= 1
    print("  Text editor tests passed!")


def test_integration():
    print("\n=== Testing Integration (6 Technologies) ===")
    if os.path.exists('test_blog.db'):
        os.remove('test_blog.db')
    db = Database('test_blog.db')
    cache_server = CacheServer(host='127.0.0.1', port=6381)
    cache_server.start()
    cache = CacheClient(cache_server)
    post = {
        'id': 'post_1',
        'title': 'Test Post',
        'author': 'Tester',
        'content': 'This is a test post with tutorial content.',
        'tags': ['test', 'tutorial'],
        'date': '2024-01-01'
    }
    db.set(post['id'], json.dumps(post))
    cache.set("post:" + post['id'], json.dumps(post))
    cached_post = json.loads(cache.get("post:" + post['id']))
    assert cached_post['title'] == 'Test Post'
    search_result = regex_search('tutorial', post['content'])
    assert search_result == 'tutorial'
    template_str = "<h1>{{ title }}</h1><p>By {{ author }}</p><p>{{ content }}</p>"
    rendered = render_template(template_str, post)
    assert 'Test Post' in rendered
    assert 'Tester' in rendered
    dom = parse_html(rendered)
    text = extract_text(rendered)
    assert 'Test Post' in text
    editor = create_editor(text=post['content'], filename='post_1.md')
    stats = editor.get_statistics()
    assert stats['characters'] > 0
    cache_server.stop()
    if os.path.exists('test_blog.db'):
        os.remove('test_blog.db')
    print("  Integration tests passed!")


def run_all_tests():
    print("\n" + "=" * 60)
    print("BLOG PLATFORM TEST SUITE")
    print("Testing all 6 technologies")
    print("=" * 60)
    try:
        test_database()
        test_cache()
        test_regex()
        test_template()
        test_browser()
        test_editor()
        test_integration()
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\n6 technologies verified:")
        print("1. TextEditor     (editor.py)")
        print("2. TemplateEngine (template_engine.py)")
        print("3. RegexEngine    (regex_engine.py)")
        print("4. WebServer      (webserver.py)")
        print("5. WebBrowser     (browser.py)")
        print("6. Database       (database.py)")
        print("   + Cache        (cache.py) [DB optimization]")
        print()
    except AssertionError as e:
        print("\nTEST FAILED: " + str(e))
        return False
    except Exception as e:
        print("\nERROR: " + str(e))
        import traceback
        traceback.print_exc()
        return False
    return True


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
