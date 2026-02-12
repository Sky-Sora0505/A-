"""
Simple Template Engine
Based on template engine concepts with compilation
"""
import re


class Template:
    """Simple template engine that compiles templates to Python code"""
    
    def __init__(self, template_string):
        self.template = template_string
        self.code = []
        self.vars = set()
    
    def render(self, context=None):
        """Render the template with given context"""
        if context is None:
            context = {}
        
        # Simple direct rendering without compilation
        result = []
        tokens = re.split(r'(\{\{.*?\}\}|\{%.*?%\})', self.template)
        
        stack = [context]  # Context stack for nested loops
        skip_until = None
        indent_level = 0
        
        i = 0
        while i < len(tokens):
            token = tokens[i].strip()
            
            if not token:
                i += 1
                continue
            
            if token.startswith('{{') and token.endswith('}}'):
                # Variable substitution
                if skip_until is None:
                    expr = token[2:-2].strip()
                    value = self._eval_expr(expr, stack[-1])
                    result.append(str(value) if value is not None else '')
            
            elif token.startswith('{%') and token.endswith('%}'):
                content = token[2:-2].strip()
                words = content.split()
                
                if not words:
                    i += 1
                    continue
                
                if words[0] == 'for':
                    # {% for item in items %}
                    if skip_until is None and len(words) >= 4 and words[2] == 'in':
                        var = words[1]
                        collection_name = words[3]
                        collection = self._eval_expr(collection_name, stack[-1])
                        
                        if collection:
                            # Find endfor
                            endfor_pos = i + 1
                            depth = 1
                            while endfor_pos < len(tokens) and depth > 0:
                                t = tokens[endfor_pos].strip()
                                if t.startswith('{%') and 'for' in t and 'end' not in t:
                                    depth += 1
                                elif t.startswith('{%') and 'endfor' in t:
                                    depth -= 1
                                endfor_pos += 1
                            
                            # Process loop body for each item
                            for item in collection:
                                new_context = stack[-1].copy()
                                new_context[var] = item
                                stack.append(new_context)
                                
                                # Process tokens in loop body
                                j = i + 1
                                while j < endfor_pos - 1:
                                    inner_token = tokens[j].strip()
                                    if inner_token.startswith('{{'):
                                        expr = inner_token[2:-2].strip()
                                        value = self._eval_expr(expr, stack[-1])
                                        result.append(str(value) if value is not None else '')
                                    elif not inner_token.startswith('{%'):
                                        result.append(inner_token)
                                    j += 1
                                
                                stack.pop()
                            
                            i = endfor_pos
                            continue
                
                elif words[0] == 'if':
                    # {% if condition %}
                    if skip_until is None:
                        condition = ' '.join(words[1:])
                        if not self._eval_condition(condition, stack[-1]):
                            skip_until = 'endif'
                
                elif words[0] == 'endif':
                    if skip_until == 'endif':
                        skip_until = None
            
            else:
                # Literal text
                if skip_until is None:
                    result.append(token)
            
            i += 1
        
        return ''.join(result)
    
    def _eval_expr(self, expr, context):
        """Evaluate an expression in context"""
        try:
            # Handle dot notation
            if '.' in expr:
                parts = expr.split('.')
                value = context.get(parts[0], '')
                for part in parts[1:]:
                    if isinstance(value, dict):
                        value = value.get(part, '')
                    else:
                        value = getattr(value, part, '')
                return value
            else:
                return context.get(expr, '')
        except:
            return ''
    
    def _eval_condition(self, condition, context):
        """Evaluate a condition"""
        try:
            # Simple evaluation
            for key, value in context.items():
                condition = condition.replace(key, repr(value))
            return eval(condition)
        except:
            return False
    
    def compile(self):
        """Compile the template"""
        tokens = re.split(r'(\{\{.*?\}\}|\{%.*?%\})', self.template)
        
        indent_level = 0
        
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            
            if token.startswith('{{') and token.endswith('}}'):
                # Variable substitution - handle dot notation
                expr = token[2:-2].strip()
                self._add_variable(expr)
                
                # Convert dot notation to dictionary/attribute access
                if '.' in expr:
                    parts = expr.split('.')
                    access_expr = parts[0]
                    for part in parts[1:]:
                        access_expr = f"({access_expr}.get('{part}') if isinstance({parts[0]}, dict) else getattr({access_expr}, '{part}', ''))"
                    self.code.append('    ' * indent_level + f"append({access_expr})")
                else:
                    self.code.append('    ' * indent_level + f"append({expr})")
            
            elif token.startswith('{%') and token.endswith('%}'):
                # Control structure
                content = token[2:-2].strip()
                words = content.split()
                
                if not words:
                    continue
                
                if words[0] == 'for':
                    # {% for item in items %}
                    if len(words) >= 4 and words[2] == 'in':
                        var = words[1]
                        collection = words[3]
                        self._add_variable(collection)
                        self.code.append('    ' * indent_level + f"for {var} in {collection}:")
                        indent_level += 1
                
                elif words[0] == 'if':
                    # {% if condition %}
                    condition = ' '.join(words[1:])
                    for word in words[1:]:
                        if word.isalpha() and word not in ['and', 'or', 'not', 'in', 'is']:
                            self._add_variable(word)
                    self.code.append('    ' * indent_level + f"if {condition}:")
                    indent_level += 1
                
                elif words[0] == 'else':
                    # {% else %}
                    indent_level -= 1
                    self.code.append('    ' * indent_level + "else:")
                    indent_level += 1
                
                elif words[0] == 'endif' or words[0] == 'endfor':
                    # {% endif %} or {% endfor %}
                    indent_level -= 1
            
            else:
                # Literal text
                self.code.append('    ' * indent_level + f"append({repr(token)})")
        
        return self
    
    def _add_variable(self, expr):
        """Extract variable names from expression"""
        # Handle dot notation (e.g., post.title)
        if '.' in expr:
            # Only add the root variable
            root = expr.split('.')[0]
            if root and root not in ['and', 'or', 'not', 'in', 'is', 'True', 'False', 'None']:
                self.vars.add(root)
        else:
            # Simple variable extraction
            parts = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expr)
            for part in parts:
                if part not in ['and', 'or', 'not', 'in', 'is', 'True', 'False', 'None']:
                    self.vars.add(part)


def render_template(template_string, context):
    """Quick template rendering function"""
    template = Template(template_string)
    template.compile()
    return template.render(context)


# Pre-defined templates for blog platform
BLOG_POST_TEMPLATE = """
<article class="blog-post">
    <h2>{{ title }}</h2>
    <div class="meta">
        <span class="author">By {{ author }}</span>
        <span class="date">{{ date }}</span>
    </div>
    <div class="content">
        {{ content }}
    </div>
    <div class="tags">
        {% for tag in tags %}
        <span class="tag">{{ tag }}</span>
        {% endfor %}
    </div>
</article>
"""

BLOG_LIST_TEMPLATE = """
<div class="blog-list">
    <h1>Blog Posts</h1>
    {% for post in posts %}
    <div class="post-preview">
        <h3>{{ post.title }}</h3>
        <p>{{ post.excerpt }}</p>
        <a href="/post/{{ post.id }}">Read more</a>
    </div>
    {% endfor %}
</div>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .blog-post { border: 1px solid #ccc; padding: 20px; margin: 20px 0; }
        .meta { color: #666; margin: 10px 0; }
        .tag { background: #e0e0e0; padding: 3px 8px; margin: 2px; display: inline-block; }
    </style>
</head>
<body>
    {{ content }}
</body>
</html>
"""
