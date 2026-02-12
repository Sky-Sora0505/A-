"""
Web-based Text Editor
ブラウザ上で動作するテキストエディタ機能

学習ポイント:
1. テキスト操作のアルゴリズム（挿入、削除、検索、置換）
2. Undo/Redo のコマンドパターン実装
3. 行番号管理とカーソル位置の追跡
4. テンプレートエンジン・正規表現との連携

実務との関連:
- VS Code のような Web エディタの基本構造
- コマンドパターンによる操作履歴管理
- テキスト処理ユーティリティの設計
- Web API を通じた編集機能の提供
"""
import json
import re
from datetime import datetime


# ==============================================================
# 第1部: テキストバッファ（エディタの中核データ構造）
# ==============================================================

class TextBuffer:
    """テキストバッファ: エディタのテキストデータを管理
    
    行ベースでテキストを保持し、基本的な編集操作を提供する。
    
    学習ポイント:
    - テキストエディタの基本データ構造
    - 行の挿入/削除の効率的な実装
    - カーソル位置（行, 列）の管理
    
    実務での対応:
    - VS Code の TextBuffer / PieceTree
    - vim の内部テキストバッファ
    """
    
    def __init__(self, text=''):
        """バッファを初期化
        
        Args:
            text: 初期テキスト
        """
        self.lines = text.split('\n') if text else ['']
        self.cursor_line = 0
        self.cursor_col = 0
    
    @property
    def text(self):
        """全テキストを結合して返す"""
        return '\n'.join(self.lines)
    
    @text.setter
    def text(self, value):
        """テキストを設定"""
        self.lines = value.split('\n') if value else ['']
    
    @property
    def line_count(self):
        """行数を返す"""
        return len(self.lines)
    
    def get_line(self, line_num):
        """指定行の内容を取得（0-indexed）"""
        if 0 <= line_num < len(self.lines):
            return self.lines[line_num]
        return ''
    
    def insert_text(self, line, col, text):
        """指定位置にテキストを挿入
        
        Args:
            line: 行番号（0-indexed）
            col: 列番号（0-indexed）
            text: 挿入するテキスト
        
        Returns:
            (新しい行, 新しい列) の位置
        """
        if line < 0 or line >= len(self.lines):
            return line, col
        
        current = self.lines[line]
        col = min(col, len(current))
        
        # 挿入テキストに改行が含まれる場合
        new_text = current[:col] + text + current[col:]
        new_lines = new_text.split('\n')
        
        # 現在の行を新しい行で置換
        self.lines[line:line + 1] = new_lines
        
        # カーソル位置を更新
        if len(new_lines) == 1:
            return line, col + len(text)
        else:
            new_line = line + len(new_lines) - 1
            new_col = len(new_lines[-1]) - len(current[col:])
            return new_line, new_col
    
    def delete_range(self, start_line, start_col, end_line, end_col):
        """指定範囲のテキストを削除
        
        Args:
            start_line, start_col: 削除開始位置
            end_line, end_col: 削除終了位置
        
        Returns:
            削除されたテキスト
        """
        if start_line == end_line:
            # 同じ行内の削除
            line = self.lines[start_line]
            deleted = line[start_col:end_col]
            self.lines[start_line] = line[:start_col] + line[end_col:]
            return deleted
        
        # 複数行にまたがる削除
        first_part = self.lines[start_line][:start_col]
        last_part = self.lines[end_line][end_col:]
        
        # 削除されるテキストを保存
        deleted_lines = [self.lines[start_line][start_col:]]
        for i in range(start_line + 1, end_line):
            deleted_lines.append(self.lines[i])
        deleted_lines.append(self.lines[end_line][:end_col])
        deleted = '\n'.join(deleted_lines)
        
        # 行を結合
        self.lines[start_line:end_line + 1] = [first_part + last_part]
        
        return deleted
    
    def get_range(self, start_line, start_col, end_line, end_col):
        """指定範囲のテキストを取得"""
        if start_line == end_line:
            return self.lines[start_line][start_col:end_col]
        
        parts = [self.lines[start_line][start_col:]]
        for i in range(start_line + 1, end_line):
            parts.append(self.lines[i])
        parts.append(self.lines[end_line][:end_col])
        return '\n'.join(parts)


# ==============================================================
# 第2部: コマンドパターン（Undo/Redo）
# ==============================================================

class EditCommand:
    """テキスト編集コマンドの基底クラス
    
    コマンドパターン (Command Pattern) の実装。
    各編集操作を「実行」と「取り消し」のペアで管理する。
    
    学習ポイント:
    - デザインパターン: コマンドパターン
    - Undo/Redo の実装原理
    
    実務での対応:
    - VS Code の UndoRedoService
    - テキストエディタ全般のUndo機能
    """
    
    def execute(self, buffer):
        """コマンドを実行"""
        raise NotImplementedError
    
    def undo(self, buffer):
        """コマンドを取り消し"""
        raise NotImplementedError
    
    def describe(self):
        """コマンドの説明を返す"""
        return self.__class__.__name__


class InsertCommand(EditCommand):
    """テキスト挿入コマンド"""
    
    def __init__(self, line, col, text):
        self.line = line
        self.col = col
        self.text = text
        self.end_line = None
        self.end_col = None
    
    def execute(self, buffer):
        self.end_line, self.end_col = buffer.insert_text(
            self.line, self.col, self.text
        )
    
    def undo(self, buffer):
        buffer.delete_range(
            self.line, self.col, self.end_line, self.end_col
        )
    
    def describe(self):
        return f"Insert '{self.text[:20]}...' at ({self.line}, {self.col})"


class DeleteCommand(EditCommand):
    """テキスト削除コマンド"""
    
    def __init__(self, start_line, start_col, end_line, end_col):
        self.start_line = start_line
        self.start_col = start_col
        self.end_line = end_line
        self.end_col = end_col
        self.deleted_text = None
    
    def execute(self, buffer):
        self.deleted_text = buffer.delete_range(
            self.start_line, self.start_col,
            self.end_line, self.end_col
        )
    
    def undo(self, buffer):
        if self.deleted_text is not None:
            buffer.insert_text(
                self.start_line, self.start_col, self.deleted_text
            )
    
    def describe(self):
        return f"Delete from ({self.start_line}, {self.start_col}) to ({self.end_line}, {self.end_col})"


class ReplaceCommand(EditCommand):
    """テキスト置換コマンド"""
    
    def __init__(self, start_line, start_col, end_line, end_col, new_text):
        self.start_line = start_line
        self.start_col = start_col
        self.end_line = end_line
        self.end_col = end_col
        self.new_text = new_text
        self.old_text = None
        self.new_end_line = None
        self.new_end_col = None
    
    def execute(self, buffer):
        self.old_text = buffer.delete_range(
            self.start_line, self.start_col,
            self.end_line, self.end_col
        )
        self.new_end_line, self.new_end_col = buffer.insert_text(
            self.start_line, self.start_col, self.new_text
        )
    
    def undo(self, buffer):
        buffer.delete_range(
            self.start_line, self.start_col,
            self.new_end_line, self.new_end_col
        )
        buffer.insert_text(
            self.start_line, self.start_col, self.old_text
        )
    
    def describe(self):
        return f"Replace at ({self.start_line}, {self.start_col})"


class CommandHistory:
    """コマンド履歴の管理（Undo/Redo スタック）
    
    2つのスタックで履歴を管理:
    - undo_stack: 実行済みコマンド（Undo用）
    - redo_stack: 取り消したコマンド（Redo用）
    
    新しいコマンドを実行するとredo_stackはクリアされる。
    """
    
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
    
    def execute(self, command, buffer):
        """コマンドを実行して履歴に追加"""
        command.execute(buffer)
        self.undo_stack.append(command)
        self.redo_stack.clear()  # 新しい操作で Redo 履歴をクリア
    
    def undo(self, buffer):
        """最後のコマンドを取り消し"""
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo(buffer)
            self.redo_stack.append(command)
            return True
        return False
    
    def redo(self, buffer):
        """取り消したコマンドを再実行"""
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute(buffer)
            self.undo_stack.append(command)
            return True
        return False
    
    @property
    def can_undo(self):
        return len(self.undo_stack) > 0
    
    @property
    def can_redo(self):
        return len(self.redo_stack) > 0


# ==============================================================
# 第3部: テキストエディタ本体
# ==============================================================

class TextEditor:
    """Web対応テキストエディタ
    
    テキストバッファ + コマンド履歴 + 検索/置換 を統合。
    Web APIから呼び出せるインターフェースを提供する。
    
    機能:
    - テキストの挿入・削除・置換
    - Undo / Redo
    - 正規表現による検索・置換
    - テンプレートの適用
    - ドキュメントの統計情報
    
    実務での対応:
    - CMS のリッチテキストエディタ
    - Wiki のテキスト編集機能
    - ブログの記事エディタ
    """
    
    def __init__(self, text=''):
        self.buffer = TextBuffer(text)
        self.history = CommandHistory()
        self.filename = None
        self.modified = False
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def get_content(self):
        """エディタの全内容を取得"""
        return self.buffer.text
    
    def set_content(self, text):
        """エディタの内容を全置換"""
        old_text = self.buffer.text
        self.buffer.text = text
        self.modified = True
        self.updated_at = datetime.now().isoformat()
    
    def insert(self, line, col, text):
        """テキストを挿入"""
        cmd = InsertCommand(line, col, text)
        self.history.execute(cmd, self.buffer)
        self.modified = True
        self.updated_at = datetime.now().isoformat()
    
    def delete(self, start_line, start_col, end_line, end_col):
        """テキストを削除"""
        cmd = DeleteCommand(start_line, start_col, end_line, end_col)
        self.history.execute(cmd, self.buffer)
        self.modified = True
        self.updated_at = datetime.now().isoformat()
    
    def replace_range(self, start_line, start_col, end_line, end_col, new_text):
        """テキストを置換"""
        cmd = ReplaceCommand(start_line, start_col, end_line, end_col, new_text)
        self.history.execute(cmd, self.buffer)
        self.modified = True
        self.updated_at = datetime.now().isoformat()
    
    def undo(self):
        """操作を取り消し"""
        result = self.history.undo(self.buffer)
        if result:
            self.updated_at = datetime.now().isoformat()
        return result
    
    def redo(self):
        """操作をやり直し"""
        result = self.history.redo(self.buffer)
        if result:
            self.updated_at = datetime.now().isoformat()
        return result
    
    def search(self, pattern, use_regex=False):
        """テキスト内を検索
        
        Args:
            pattern: 検索パターン
            use_regex: 正規表現を使用するか
        
        Returns:
            マッチ位置のリスト [(line, col, length), ...]
        """
        results = []
        text = self.buffer.text
        
        try:
            if use_regex:
                for match in re.finditer(pattern, text, re.MULTILINE):
                    # マッチ位置を (行, 列, 長さ) に変換
                    start = match.start()
                    line, col = self._offset_to_position(start)
                    results.append({
                        'line': line,
                        'col': col,
                        'length': match.end() - match.start(),
                        'text': match.group()
                    })
            else:
                # 単純な文字列検索
                start = 0
                pattern_lower = pattern.lower()
                text_lower = text.lower()
                while True:
                    idx = text_lower.find(pattern_lower, start)
                    if idx == -1:
                        break
                    line, col = self._offset_to_position(idx)
                    results.append({
                        'line': line,
                        'col': col,
                        'length': len(pattern),
                        'text': text[idx:idx + len(pattern)]
                    })
                    start = idx + 1
        except re.error:
            pass
        
        return results
    
    def search_and_replace(self, pattern, replacement, use_regex=False):
        """検索して置換
        
        Args:
            pattern: 検索パターン
            replacement: 置換文字列
            use_regex: 正規表現を使用するか
        
        Returns:
            置換された回数
        """
        text = self.buffer.text
        try:
            if use_regex:
                new_text, count = re.subn(pattern, replacement, text)
            else:
                count = text.lower().count(pattern.lower())
                # 大文字小文字を無視して置換
                new_text = re.sub(
                    re.escape(pattern), replacement, text, flags=re.IGNORECASE
                )
        except re.error:
            return 0
        
        if count > 0:
            self.set_content(new_text)
        
        return count
    
    def get_statistics(self):
        """ドキュメントの統計情報を取得"""
        text = self.buffer.text
        lines = self.buffer.lines
        words = text.split()
        
        return {
            'lines': len(lines),
            'words': len(words),
            'characters': len(text),
            'characters_no_spaces': len(text.replace(' ', '').replace('\n', '')),
            'modified': self.modified,
            'can_undo': self.history.can_undo,
            'can_redo': self.history.can_redo,
            'undo_count': len(self.history.undo_stack),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def _offset_to_position(self, offset):
        """テキストオフセットを (行, 列) に変換"""
        text = self.buffer.text
        line = text[:offset].count('\n')
        last_newline = text.rfind('\n', 0, offset)
        col = offset - last_newline - 1 if last_newline != -1 else offset
        return line, col
    
    def to_dict(self):
        """エディタの状態をJSONシリアライズ可能な辞書に変換"""
        return {
            'content': self.buffer.text,
            'filename': self.filename,
            'modified': self.modified,
            'statistics': self.get_statistics(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


# ==============================================================
# 第4部: エディタ用HTMLテンプレート（WebUI生成）
# ==============================================================

EDITOR_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>ブログエディタ - {{ title }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e2e; color: #cdd6f4; }
        .editor-container { max-width: 900px; margin: 20px auto; padding: 20px; }
        
        .toolbar {
            background: #313244; border-radius: 8px 8px 0 0;
            padding: 10px 15px; display: flex; gap: 8px; flex-wrap: wrap;
            border-bottom: 2px solid #45475a;
        }
        .toolbar button {
            background: #585b70; color: #cdd6f4; border: none;
            padding: 6px 12px; border-radius: 4px; cursor: pointer;
            font-size: 13px; transition: background 0.2s;
        }
        .toolbar button:hover { background: #7f849c; }
        .toolbar .separator { width: 1px; background: #45475a; margin: 0 4px; }
        
        .editor-area {
            display: flex; background: #1e1e2e;
            border: 1px solid #45475a; min-height: 400px;
        }
        .line-numbers {
            background: #181825; color: #585b70; padding: 15px 10px;
            text-align: right; font-family: 'Consolas', monospace;
            font-size: 14px; line-height: 1.6; user-select: none;
            min-width: 50px; border-right: 1px solid #313244;
        }
        .text-content {
            flex: 1; padding: 15px; font-family: 'Consolas', monospace;
            font-size: 14px; line-height: 1.6; white-space: pre-wrap;
            word-wrap: break-word; outline: none;
        }
        
        .statusbar {
            background: #313244; padding: 6px 15px;
            border-radius: 0 0 8px 8px; display: flex;
            justify-content: space-between; font-size: 12px;
            color: #a6adc8; border-top: 1px solid #45475a;
        }
        
        .search-bar {
            background: #313244; padding: 10px 15px;
            border-bottom: 1px solid #45475a; display: flex;
            gap: 8px; align-items: center;
        }
        .search-bar input {
            background: #45475a; color: #cdd6f4; border: 1px solid #585b70;
            padding: 5px 10px; border-radius: 4px; font-size: 13px;
        }
        .search-bar label { font-size: 13px; }
        
        h2 { color: #cba6f7; margin-bottom: 15px; }
        .highlight { background: #f9e2af; color: #1e1e2e; padding: 1px 2px; border-radius: 2px; }
    </style>
</head>
<body>
    <div class="editor-container">
        <h2>{{ title }}</h2>
        <div class="toolbar">
            <button onclick="editorAction('undo')">↩ Undo</button>
            <button onclick="editorAction('redo')">↪ Redo</button>
            <div class="separator"></div>
            <button onclick="editorAction('save')">💾 保存</button>
            <button onclick="editorAction('search')">🔍 検索</button>
            <button onclick="editorAction('replace')">🔄 置換</button>
            <div class="separator"></div>
            <button onclick="editorAction('template')">📝 テンプレート適用</button>
            <button onclick="editorAction('stats')">📊 統計</button>
        </div>
        
        <div class="search-bar" id="searchBar" style="display:none;">
            <input type="text" id="searchInput" placeholder="検索...">
            <input type="text" id="replaceInput" placeholder="置換...">
            <label><input type="checkbox" id="regexCheck"> 正規表現</label>
            <button onclick="doSearch()">検索</button>
            <button onclick="doReplace()">全て置換</button>
        </div>
        
        <div class="editor-area">
            <div class="line-numbers">{{ line_numbers }}</div>
            <div class="text-content" contenteditable="true" id="editor">{{ content }}</div>
        </div>
        
        <div class="statusbar">
            <span>{{ stats_left }}</span>
            <span>{{ stats_right }}</span>
        </div>
    </div>
</body>
</html>
"""

EDITOR_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>記事の編集</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .editor-form { max-width: 800px; margin: 0 auto; background: white; 
                       padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-bottom: 20px; }
        label { display: block; font-weight: bold; margin: 15px 0 5px; color: #555; }
        input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ddd; 
                             border-radius: 4px; font-size: 14px; }
        textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;
                   font-family: 'Consolas', monospace; font-size: 14px; min-height: 300px; resize: vertical; }
        .btn { padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;
               font-size: 14px; margin-right: 10px; margin-top: 15px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn:hover { opacity: 0.9; }
        .tag-input { display: flex; gap: 8px; }
        .tag-input input { flex: 1; }
        .stats { background: #f8f9fa; padding: 10px 15px; border-radius: 4px; 
                 margin-top: 15px; font-size: 13px; color: #666; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        nav { margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="editor-form">
        <nav><a href="/">← ホーム</a> | <a href="/posts">記事一覧</a></nav>
        <h1>{{ page_title }}</h1>
        <form method="POST" action="{{ form_action }}">
            <label for="title">タイトル</label>
            <input type="text" id="title" name="title" value="{{ post_title }}" required>
            
            <label for="author">著者</label>
            <input type="text" id="author" name="author" value="{{ post_author }}">
            
            <label for="content">本文</label>
            <textarea id="content" name="content">{{ post_content }}</textarea>
            
            <label for="tags">タグ（カンマ区切り）</label>
            <input type="text" id="tags" name="tags" value="{{ post_tags }}">
            
            <div class="stats" id="stats">
                文字数: <span id="charCount">0</span> | 
                単語数: <span id="wordCount">0</span> | 
                行数: <span id="lineCount">0</span>
            </div>
            
            <button type="submit" class="btn btn-primary">{{ submit_text }}</button>
            <a href="/" class="btn btn-secondary" style="text-decoration:none; display:inline-block; text-align:center;">キャンセル</a>
        </form>
    </div>
    
    <script>
    // テキストエリアの統計をリアルタイム更新
    const textarea = document.getElementById('content');
    const charCount = document.getElementById('charCount');
    const wordCount = document.getElementById('wordCount');
    const lineCount = document.getElementById('lineCount');
    
    function updateStats() {
        const text = textarea.value;
        charCount.textContent = text.length;
        wordCount.textContent = text.trim() ? text.trim().split(/\\s+/).length : 0;
        lineCount.textContent = text.split('\\n').length;
    }
    
    textarea.addEventListener('input', updateStats);
    updateStats();
    </script>
</body>
</html>
"""


# ==============================================================
# 第5部: ユーティリティ関数
# ==============================================================

def create_editor(text='', filename=None):
    """エディタインスタンスを作成する便利関数
    
    Args:
        text: 初期テキスト
        filename: ファイル名
    
    Returns:
        TextEditor インスタンス
    """
    editor = TextEditor(text)
    editor.filename = filename
    return editor


def render_editor_html(editor, title='エディタ'):
    """エディタの内容をHTMLに変換（テンプレートエンジン連携用）
    
    Args:
        editor: TextEditor インスタンス
        title: ページタイトル
    
    Returns:
        HTML文字列
    """
    stats = editor.get_statistics()
    lines = editor.buffer.lines
    
    line_numbers = '\n'.join(str(i + 1) for i in range(len(lines)))
    content = editor.get_content()
    stats_left = f"行: {stats['lines']} | 文字: {stats['characters']} | 単語: {stats['words']}"
    stats_right = f"{'● 変更あり' if stats['modified'] else '保存済み'} | Undo: {stats['undo_count']}"
    
    # 簡易テンプレート置換
    html = EDITOR_HTML_TEMPLATE
    html = html.replace('{{ title }}', title)
    html = html.replace('{{ line_numbers }}', line_numbers)
    html = html.replace('{{ content }}', content)
    html = html.replace('{{ stats_left }}', stats_left)
    html = html.replace('{{ stats_right }}', stats_right)
    
    return html
