"""
Simple Web Browser (HTTP Client + HTML Parser)
Pythonでゼロから構築する簡易Webブラウザ

学習ポイント:
1. ソケットプログラミングによるHTTP通信
2. HTMLパーサーの仕組み（字句解析→構文解析→DOM構築）
3. HTTPプロトコルの理解（リクエスト/レスポンス）
4. テキストレンダリングの基礎

実務との関連:
- requests ライブラリの内部動作の理解
- BeautifulSoup / lxml の仕組み
- Webスクレイピングの基礎技術
- API クライアントの設計パターン
"""
import socket
import ssl
import json
from urllib.parse import urlparse, urlencode, urljoin


# ==============================================================
# 第1部: HTTP クライアント（リクエストの送受信）
# ==============================================================

class HTTPResponse:
    """HTTPレスポンスを表すクラス
    
    実務での対応:
    - requests.Response に相当
    - ステータスコード、ヘッダー、ボディを保持
    """
    
    def __init__(self, status_code, headers, body):
        self.status_code = status_code
        self.headers = headers
        self.body = body
    
    @property
    def ok(self):
        """2xx系のステータスコードかどうか"""
        return 200 <= self.status_code < 300
    
    @property
    def text(self):
        """レスポンスボディをテキストとして取得"""
        if isinstance(self.body, bytes):
            return self.body.decode('utf-8', errors='replace')
        return self.body
    
    def json(self):
        """レスポンスボディをJSONとしてパース"""
        return json.loads(self.text)
    
    def __repr__(self):
        return f"HTTPResponse(status={self.status_code}, body_length={len(self.body)})"


class HTTPClient:
    """簡易HTTPクライアント
    
    ソケットを使ったHTTP/1.1通信の実装。
    
    学習ポイント:
    - TCP接続の確立（3ウェイハンドシェイク）
    - HTTPリクエストメッセージのフォーマット
    - HTTPレスポンスのパース
    - Content-Length / Transfer-Encoding の処理
    
    実務での対応:
    - requests.get(), requests.post() の内部実装
    - urllib3 のコネクション管理
    """
    
    DEFAULT_PORTS = {'http': 80, 'https': 443}
    BUFFER_SIZE = 4096
    TIMEOUT = 10
    
    def get(self, url, headers=None):
        """GETリクエストを送信
        
        Args:
            url: リクエスト先URL
            headers: 追加ヘッダー（辞書）
        
        Returns:
            HTTPResponse オブジェクト
        """
        return self._request('GET', url, headers=headers)
    
    def post(self, url, data=None, json_data=None, headers=None):
        """POSTリクエストを送信
        
        Args:
            url: リクエスト先URL
            data: フォームデータ（辞書）
            json_data: JSONデータ（辞書）
            headers: 追加ヘッダー
        
        Returns:
            HTTPResponse オブジェクト
        """
        if headers is None:
            headers = {}
        
        body = None
        if json_data is not None:
            body = json.dumps(json_data).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        elif data is not None:
            body = urlencode(data).encode('utf-8')
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        return self._request('POST', url, headers=headers, body=body)
    
    def _request(self, method, url, headers=None, body=None):
        """HTTPリクエストの実行
        
        処理の流れ:
        1. URLをパース（ホスト名、ポート、パスを分離）
        2. TCPソケット接続を確立
        3. HTTPリクエストメッセージを構築して送信
        4. レスポンスを受信してパース
        
        Args:
            method: HTTPメソッド (GET, POST, etc.)
            url: リクエスト先URL
            headers: HTTPヘッダー辞書
            body: リクエストボディ（バイト列）
        
        Returns:
            HTTPResponse オブジェクト
        """
        if headers is None:
            headers = {}
        
        # URLのパース
        parsed = urlparse(url)
        scheme = parsed.scheme or 'http'
        host = parsed.hostname
        port = parsed.port or self.DEFAULT_PORTS.get(scheme, 80)
        path = parsed.path or '/'
        if parsed.query:
            path += '?' + parsed.query
        
        # ソケットの作成と接続
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.TIMEOUT)
        
        try:
            # HTTPS の場合はSSLでラップ
            if scheme == 'https':
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)
            
            sock.connect((host, port))
            
            # リクエストメッセージの構築
            request_message = self._build_request(
                method, path, host, headers, body
            )
            
            # リクエストの送信
            sock.sendall(request_message)
            
            # レスポンスの受信とパース
            response_data = self._receive_response(sock)
            return self._parse_response(response_data)
        
        except socket.timeout:
            return HTTPResponse(408, {}, b'Request Timeout')
        except ConnectionRefusedError:
            return HTTPResponse(503, {}, b'Connection Refused')
        except Exception as e:
            return HTTPResponse(0, {}, str(e).encode('utf-8'))
        finally:
            sock.close()
    
    def _build_request(self, method, path, host, headers, body):
        """HTTPリクエストメッセージを構築
        
        HTTPリクエストの構造:
        ```
        GET /path HTTP/1.1\\r\\n
        Host: example.com\\r\\n
        Connection: close\\r\\n
        \\r\\n
        (body)
        ```
        
        Args:
            method: HTTPメソッド
            path: リクエストパス
            host: ホスト名
            headers: ヘッダー辞書
            body: リクエストボディ
        
        Returns:
            バイト列のリクエストメッセージ
        """
        # デフォルトヘッダーの設定
        default_headers = {
            'Host': host,
            'Connection': 'close',
            'User-Agent': 'SimpleBrowser/1.0 (Python)',
            'Accept': 'text/html, application/json, */*',
        }
        default_headers.update(headers)
        
        if body:
            default_headers['Content-Length'] = str(len(body))
        
        # リクエスト行
        request_line = f"{method} {path} HTTP/1.1\r\n"
        
        # ヘッダー行
        header_lines = ''.join(
            f"{key}: {value}\r\n" for key, value in default_headers.items()
        )
        
        # 空行（ヘッダーとボディの区切り）
        message = (request_line + header_lines + "\r\n").encode('utf-8')
        
        if body:
            message += body
        
        return message
    
    def _receive_response(self, sock):
        """ソケットからレスポンスデータを受信
        
        バッファリングしながら全データを受信する。
        Connection: close により、サーバーが接続を閉じるまで読み続ける。
        """
        data = b''
        while True:
            try:
                chunk = sock.recv(self.BUFFER_SIZE)
                if not chunk:
                    break
                data += chunk
            except socket.timeout:
                break
        return data
    
    def _parse_response(self, data):
        """HTTPレスポンスをパース
        
        レスポンスの構造:
        ```
        HTTP/1.1 200 OK\\r\\n
        Content-Type: text/html\\r\\n
        Content-Length: 1234\\r\\n
        \\r\\n
        (body)
        ```
        
        Args:
            data: 生のレスポンスバイト列
        
        Returns:
            HTTPResponse オブジェクト
        """
        try:
            # ヘッダーとボディを分離（空行 \r\n\r\n で区切る）
            header_end = data.find(b'\r\n\r\n')
            if header_end == -1:
                return HTTPResponse(0, {}, data)
            
            header_data = data[:header_end].decode('utf-8', errors='replace')
            body = data[header_end + 4:]
            
            # ステータス行のパース
            lines = header_data.split('\r\n')
            status_line = lines[0]
            parts = status_line.split(' ', 2)
            status_code = int(parts[1]) if len(parts) >= 2 else 0
            
            # ヘッダーのパース
            headers = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            return HTTPResponse(status_code, headers, body)
        
        except Exception:
            return HTTPResponse(0, {}, data)


# ==============================================================
# 第2部: HTML パーサー（HTMLの解析とDOM構築）
# ==============================================================

class HTMLNode:
    """HTMLのDOMノードを表すクラス
    
    DOMツリーの各ノードは以下の情報を持つ:
    - タグ名（要素ノードの場合）
    - テキスト内容（テキストノードの場合）
    - 属性（辞書）
    - 子ノードのリスト
    
    実務での対応:
    - BeautifulSoup の Tag / NavigableString
    - DOM API の Element / TextNode
    """
    
    def __init__(self, tag=None, text=None, attributes=None):
        self.tag = tag
        self.text = text
        self.attributes = attributes or {}
        self.children = []
        self.parent = None
    
    def add_child(self, child):
        """子ノードを追加"""
        child.parent = self
        self.children.append(child)
    
    def get_text(self):
        """ノード以下の全テキストを取得（再帰的）
        
        BeautifulSoup の .get_text() に相当
        """
        if self.text:
            return self.text
        return ''.join(child.get_text() for child in self.children)
    
    def find(self, tag):
        """指定タグの最初の要素を検索（深さ優先）
        
        BeautifulSoup の .find() に相当
        """
        if self.tag == tag:
            return self
        for child in self.children:
            result = child.find(tag)
            if result:
                return result
        return None
    
    def find_all(self, tag):
        """指定タグの全要素を検索
        
        BeautifulSoup の .find_all() に相当
        """
        results = []
        if self.tag == tag:
            results.append(self)
        for child in self.children:
            results.extend(child.find_all(tag))
        return results
    
    def get_attribute(self, name):
        """属性値を取得"""
        return self.attributes.get(name)
    
    def __repr__(self):
        if self.text:
            return f"TextNode({self.text[:30]}...)" if len(self.text or '') > 30 else f"TextNode({self.text})"
        return f"Element(<{self.tag}>, children={len(self.children)})"


class HTMLParser:
    """簡易HTMLパーサー
    
    字句解析（トークナイズ）→ 構文解析（ツリー構築）の2段階で処理。
    
    学習ポイント:
    - 字句解析: 文字列をトークン（タグ、テキスト）に分割
    - 構文解析: トークン列からDOMツリーを構築
    - 自己閉じタグ（<br/>, <img/>）の処理
    
    実務での対応:
    - html.parser.HTMLParser の仕組み
    - BeautifulSoup のパース処理
    """
    
    # 自己閉じタグ（子要素を持たないタグ）
    SELF_CLOSING_TAGS = {
        'br', 'hr', 'img', 'input', 'meta', 'link',
        'area', 'base', 'col', 'embed', 'source', 'wbr'
    }
    
    def parse(self, html):
        """HTMLをパースしてDOMツリーを構築
        
        処理の流れ:
        1. トークナイズ（HTML文字列 → トークンリスト）
        2. ツリー構築（トークンリスト → DOMツリー）
        
        Args:
            html: HTML文字列
        
        Returns:
            HTMLNode（ルートノード）
        """
        tokens = self._tokenize(html)
        return self._build_tree(tokens)
    
    def _tokenize(self, html):
        """HTMLを字句解析してトークンに分割
        
        トークンの種類:
        - ('open', tag, attributes): 開きタグ
        - ('close', tag): 閉じタグ
        - ('self_close', tag, attributes): 自己閉じタグ
        - ('text', content): テキスト
        
        アルゴリズム:
        1. '<' を見つけたらタグの解析開始
        2. タグ名と属性を抽出
        3. '>' までがタグ
        4. タグ間のテキストをテキストトークンとして記録
        """
        tokens = []
        pos = 0
        length = len(html)
        
        while pos < length:
            if html[pos] == '<':
                # タグの開始
                end = html.find('>', pos)
                if end == -1:
                    # 閉じ '>' がない場合はテキストとして扱う
                    tokens.append(('text', html[pos:]))
                    break
                
                tag_content = html[pos + 1:end].strip()
                
                if tag_content.startswith('!'):
                    # コメントやDOCTYPEはスキップ
                    pos = end + 1
                    continue
                
                if tag_content.startswith('/'):
                    # 閉じタグ: </tag>
                    tag_name = tag_content[1:].strip().split()[0].lower()
                    tokens.append(('close', tag_name))
                else:
                    # 開きタグまたは自己閉じタグ
                    is_self_closing = tag_content.endswith('/')
                    if is_self_closing:
                        tag_content = tag_content[:-1].strip()
                    
                    # タグ名と属性を分離
                    tag_name, attributes = self._parse_tag(tag_content)
                    tag_name = tag_name.lower()
                    
                    if is_self_closing or tag_name in self.SELF_CLOSING_TAGS:
                        tokens.append(('self_close', tag_name, attributes))
                    else:
                        tokens.append(('open', tag_name, attributes))
                
                pos = end + 1
            else:
                # テキストノード
                next_tag = html.find('<', pos)
                if next_tag == -1:
                    text = html[pos:]
                    pos = length
                else:
                    text = html[pos:next_tag]
                    pos = next_tag
                
                # 空白のみでないテキストを追加
                stripped = text.strip()
                if stripped:
                    tokens.append(('text', stripped))
        
        return tokens
    
    def _parse_tag(self, tag_content):
        """タグの内容をパースしてタグ名と属性を分離
        
        例: 'a href="/posts" class="link"'
        → ('a', {'href': '/posts', 'class': 'link'})
        
        属性の書式:
        - key="value" (ダブルクォート)
        - key='value' (シングルクォート)
        - key (値なし、Trueとして扱う)
        """
        parts = tag_content.split(None, 1)
        tag_name = parts[0]
        attributes = {}
        
        if len(parts) > 1:
            attr_str = parts[1]
            pos = 0
            while pos < len(attr_str):
                # 空白をスキップ
                while pos < len(attr_str) and attr_str[pos].isspace():
                    pos += 1
                if pos >= len(attr_str):
                    break
                
                # 属性名を取得
                name_start = pos
                while pos < len(attr_str) and attr_str[pos] not in ('=', ' ', '>', '/'):
                    pos += 1
                name = attr_str[name_start:pos].strip()
                
                if not name:
                    pos += 1
                    continue
                
                # '=' があれば値を取得
                if pos < len(attr_str) and attr_str[pos] == '=':
                    pos += 1  # '=' をスキップ
                    # 空白をスキップ
                    while pos < len(attr_str) and attr_str[pos].isspace():
                        pos += 1
                    
                    if pos < len(attr_str) and attr_str[pos] in ('"', "'"):
                        # クォートされた値
                        quote = attr_str[pos]
                        pos += 1
                        value_start = pos
                        while pos < len(attr_str) and attr_str[pos] != quote:
                            pos += 1
                        attributes[name] = attr_str[value_start:pos]
                        pos += 1  # 閉じクォートをスキップ
                    else:
                        # クォートなしの値
                        value_start = pos
                        while pos < len(attr_str) and not attr_str[pos].isspace():
                            pos += 1
                        attributes[name] = attr_str[value_start:pos]
                else:
                    # 値なし属性
                    attributes[name] = True
        
        return tag_name, attributes
    
    def _build_tree(self, tokens):
        """トークン列からDOMツリーを構築
        
        スタックベースのアルゴリズム:
        1. ルートノードを作成してスタックに積む
        2. 開きタグ → 新ノードを作成、現在のノードの子に追加、スタックに積む
        3. 閉じタグ → スタックからポップ
        4. テキスト → テキストノードを現在のノードの子に追加
        5. 自己閉じタグ → 新ノードを作成、現在のノードの子に追加（スタックには積まない）
        """
        root = HTMLNode(tag='document')
        stack = [root]
        
        for token in tokens:
            current = stack[-1]
            
            if token[0] == 'open':
                # 開きタグ: 新しい子要素を作成してスタックに積む
                node = HTMLNode(tag=token[1], attributes=token[2])
                current.add_child(node)
                stack.append(node)
            
            elif token[0] == 'close':
                # 閉じタグ: スタックからポップ（対応するタグまで）
                if len(stack) > 1:
                    # 対応する開きタグを探す
                    for i in range(len(stack) - 1, 0, -1):
                        if stack[i].tag == token[1]:
                            stack = stack[:i]
                            break
                    else:
                        # 対応するタグが見つからない場合は単にポップ
                        if len(stack) > 1:
                            stack.pop()
            
            elif token[0] == 'self_close':
                # 自己閉じタグ: 子要素に追加のみ（スタックには積まない）
                node = HTMLNode(tag=token[1], attributes=token[2])
                current.add_child(node)
            
            elif token[0] == 'text':
                # テキストノード
                node = HTMLNode(text=token[1])
                current.add_child(node)
        
        return root


# ==============================================================
# 第3部: テキストレンダラー（HTMLをテキストに変換）
# ==============================================================

class TextRenderer:
    """HTMLのDOMツリーをテキスト表示用に変換
    
    ブラウザのレンダリングエンジンの簡易版。
    DOMツリーを走査して、テキストベースの表示を生成する。
    
    実務での対応:
    - w3m, lynx などのテキストブラウザのレンダリング
    - html2text ライブラリの処理
    """
    
    def render(self, node, indent=0):
        """DOMツリーをテキストに変換
        
        各HTMLタグに応じた表示を生成:
        - <h1>~<h6>: 見出し（=== で装飾）
        - <p>: 段落（前後に空行）
        - <a>: リンク（[テキスト](URL) 形式）
        - <li>: リスト項目（- プレフィックス）
        - <div>: ブロック要素
        """
        if node.text:
            return node.text
        
        lines = []
        tag = node.tag
        
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            text = node.get_text()
            level = int(tag[1])
            prefix = '#' * level
            lines.append(f"\n{prefix} {text}\n")
        
        elif tag == 'p':
            text = node.get_text()
            if text:
                lines.append(f"\n{text}\n")
        
        elif tag == 'a':
            text = node.get_text()
            href = node.get_attribute('href') or ''
            lines.append(f"[{text}]({href})")
        
        elif tag == 'li':
            text = node.get_text()
            lines.append(f"  • {text}")
        
        elif tag in ('ul', 'ol'):
            for child in node.children:
                lines.append(self.render(child, indent))
            lines.append('')
        
        elif tag == 'article':
            lines.append('─' * 50)
            for child in node.children:
                lines.append(self.render(child, indent))
            lines.append('─' * 50)
        
        elif tag == 'span':
            # class="tag" のスパン要素はバッジ風に表示
            css_class = node.get_attribute('class') or ''
            text = node.get_text()
            if 'tag' in css_class:
                lines.append(f"[{text}]")
            else:
                lines.append(text)
        
        elif tag in ('div', 'body', 'html', 'document', 'nav',
                      'header', 'footer', 'section', 'main'):
            for child in node.children:
                lines.append(self.render(child, indent))
        
        elif tag == 'style' or tag == 'script':
            # CSS/JSは表示しない
            pass
        
        elif tag == 'title':
            text = node.get_text()
            lines.append(f"📄 タイトル: {text}\n")
        
        elif tag == 'head':
            for child in node.children:
                if child.tag == 'title':
                    lines.append(self.render(child, indent))
        
        else:
            # その他のタグ: 子要素のみ処理
            for child in node.children:
                lines.append(self.render(child, indent))
        
        return '\n'.join(line for line in lines if line)


# ==============================================================
# 第4部: 簡易ブラウザ（全機能を統合）
# ==============================================================

class Browser:
    """簡易Webブラウザ
    
    HTTPクライアント + HTMLパーサー + テキストレンダラーを統合。
    URLを指定してWebページを取得し、テキストとして表示する。
    
    機能:
    - ページの取得と表示
    - リンクの抽出
    - API呼び出し（JSON）
    - ページ履歴の管理
    
    実務での対応:
    - Webスクレイピングツールの基本構造
    - テストクライアント（Django TestClient, Flask test_client）
    - E2Eテストの内部動作
    """
    
    def __init__(self, base_url=None):
        """ブラウザを初期化
        
        Args:
            base_url: ベースURL（相対URLの解決に使用）
        """
        self.client = HTTPClient()
        self.parser = HTMLParser()
        self.renderer = TextRenderer()
        self.base_url = base_url or ''
        self.history = []        # 閲覧履歴
        self.current_page = None # 現在のページ内容
        self.current_url = None  # 現在のURL
        self.current_dom = None  # 現在のDOMツリー
    
    def navigate(self, url):
        """指定URLに遷移してページを取得・表示
        
        処理の流れ:
        1. HTTPリクエストを送信
        2. レスポンスを受信
        3. HTMLをパース
        4. テキストとしてレンダリング
        
        Args:
            url: 遷移先URL
        
        Returns:
            レンダリング結果のテキスト
        """
        # 相対URLを絶対URLに変換
        if not url.startswith('http'):
            url = urljoin(self.base_url, url)
        
        # 履歴に追加
        if self.current_url:
            self.history.append(self.current_url)
        self.current_url = url
        
        # ページを取得
        response = self.client.get(url)
        
        if not response.ok:
            return f"エラー: {response.status_code}\n{response.text}"
        
        self.current_page = response.text
        
        # Content-Type に応じた処理
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # JSONレスポンスはフォーマットして表示
            try:
                data = response.json()
                return json.dumps(data, indent=2, ensure_ascii=False)
            except Exception:
                return response.text
        
        # HTMLをパースしてレンダリング
        self.current_dom = self.parser.parse(response.text)
        return self.renderer.render(self.current_dom)
    
    def back(self):
        """前のページに戻る"""
        if self.history:
            url = self.history.pop()
            self.current_url = None  # 履歴に追加されないように
            return self.navigate(url)
        return "履歴がありません"
    
    def get_links(self):
        """現在のページからリンクを抽出
        
        Returns:
            (テキスト, URL) のリスト
        """
        if not self.current_dom:
            return []
        
        links = []
        for anchor in self.current_dom.find_all('a'):
            text = anchor.get_text()
            href = anchor.get_attribute('href') or ''
            # 相対URLを絶対URLに変換
            if href and not href.startswith('http'):
                href = urljoin(self.current_url or self.base_url, href)
            links.append((text, href))
        
        return links
    
    def get_title(self):
        """現在のページのタイトルを取得"""
        if not self.current_dom:
            return None
        title_node = self.current_dom.find('title')
        if title_node:
            return title_node.get_text()
        return None
    
    def api_get(self, url, headers=None):
        """APIエンドポイントにGETリクエスト（JSON用）
        
        Args:
            url: APIエンドポイントURL
            headers: 追加ヘッダー
        
        Returns:
            パースされたJSONデータ（辞書/リスト）
        """
        if not url.startswith('http'):
            url = urljoin(self.base_url, url)
        
        response = self.client.get(url, headers=headers)
        if response.ok:
            try:
                return response.json()
            except Exception:
                return {'raw': response.text}
        return {'error': response.status_code}
    
    def api_post(self, url, data=None, headers=None):
        """APIエンドポイントにPOSTリクエスト（JSON用）
        
        Args:
            url: APIエンドポイントURL
            data: 送信するJSONデータ
            headers: 追加ヘッダー
        
        Returns:
            パースされたJSONデータ
        """
        if not url.startswith('http'):
            url = urljoin(self.base_url, url)
        
        response = self.client.post(url, json_data=data, headers=headers)
        if response.ok:
            try:
                return response.json()
            except Exception:
                return {'raw': response.text}
        return {'error': response.status_code}
    
    def view_source(self):
        """現在のページのHTMLソースを表示"""
        return self.current_page or "ページが読み込まれていません"
    
    def get_history(self):
        """閲覧履歴を取得"""
        return self.history.copy()


# ==============================================================
# ユーティリティ関数
# ==============================================================

def fetch_page(url):
    """URLからページを取得してテキスト表示する（便利関数）
    
    Args:
        url: 取得先URL
    
    Returns:
        レンダリングされたテキスト
    """
    browser = Browser()
    return browser.navigate(url)


def parse_html(html_string):
    """HTML文字列をパースしてDOMツリーを返す（便利関数）
    
    Args:
        html_string: HTML文字列
    
    Returns:
        HTMLNode（ルートノード）
    """
    parser = HTMLParser()
    return parser.parse(html_string)


def extract_links(html_string):
    """HTML文字列からリンクを抽出する（便利関数）
    
    Args:
        html_string: HTML文字列
    
    Returns:
        (テキスト, URL) のリスト
    """
    dom = parse_html(html_string)
    links = []
    for anchor in dom.find_all('a'):
        text = anchor.get_text()
        href = anchor.get_attribute('href') or ''
        links.append((text, href))
    return links


def extract_text(html_string):
    """HTML文字列からテキストを抽出する（便利関数）
    
    Args:
        html_string: HTML文字列
    
    Returns:
        抽出されたテキスト
    """
    dom = parse_html(html_string)
    renderer = TextRenderer()
    return renderer.render(dom)
