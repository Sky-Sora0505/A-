"""
Simple Web Server with routing and request handling
Based on simple web server concepts
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
from datetime import datetime


class RequestHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests"""
    
    # Store routes and application instance
    routes = {}
    app = None
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        # Find matching route
        handler = self._find_route(path)
        
        if handler:
            try:
                response = handler(self, query)
                self._send_response(200, response)
            except Exception as e:
                self._send_error(500, str(e))
        else:
            self._send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Parse JSON or form data
        try:
            if self.headers.get('Content-Type') == 'application/json':
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = urllib.parse.parse_qs(post_data.decode('utf-8'))
        except:
            data = {}
        
        # Find matching route
        handler = self._find_route(path, method='POST')
        
        if handler:
            try:
                response = handler(self, data)
                self._send_response(200, response)
            except Exception as e:
                self._send_error(500, str(e))
        else:
            self._send_error(404, "Not Found")
    
    def _find_route(self, path, method='GET'):
        """Find route handler for path"""
        route_key = f"{method}:{path}"
        if route_key in self.routes:
            return self.routes[route_key]
        
        # Try pattern matching for dynamic routes
        for registered_route, handler in self.routes.items():
            if not registered_route.startswith(method):
                continue
            route_path = registered_route.split(':', 1)[1]
            if self._match_route(route_path, path):
                return handler
        
        return None
    
    def _match_route(self, pattern, path):
        """Match route pattern with path"""
        pattern_parts = pattern.split('/')
        path_parts = path.split('/')
        
        if len(pattern_parts) != len(path_parts):
            return False
        
        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith('<') and pattern_part.endswith('>'):
                continue
            if pattern_part != path_part:
                return False
        
        return True
    
    def _send_response(self, status, content):
        """Send HTTP response"""
        if isinstance(content, dict):
            content = json.dumps(content, ensure_ascii=False)
            content_type = 'application/json; charset=utf-8'
        else:
            content = str(content)
            content_type = 'text/html; charset=utf-8'
        
        content_bytes = content.encode('utf-8')
        
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(content_bytes))
        self.end_headers()
        self.wfile.write(content_bytes)
    
    def _send_error(self, status, message):
        """Send error response"""
        content = {
            'error': message,
            'status': status
        }
        self._send_response(status, content)
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


class WebServer:
    """Simple web server with routing"""
    
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port
        self.routes = {}
        self.server = None
    
    def route(self, path, method='GET'):
        """Decorator to register routes"""
        def decorator(func):
            route_key = f"{method}:{path}"
            self.routes[route_key] = func
            return func
        return decorator
    
    def add_route(self, path, handler, method='GET'):
        """Add a route programmatically"""
        route_key = f"{method}:{path}"
        self.routes[route_key] = handler
    
    def start(self):
        """Start the web server"""
        RequestHandler.routes = self.routes
        RequestHandler.app = self
        
        self.server = HTTPServer((self.host, self.port), RequestHandler)
        print(f"Web server running on http://{self.host}:{self.port}")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.server.shutdown()
    
    def stop(self):
        """Stop the web server"""
        if self.server:
            self.server.shutdown()
