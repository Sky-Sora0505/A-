"""
Simple Regular Expression Engine for Search
Based on regex parsing and backtracking concepts
"""


class RegexParser:
    """Parse simple regex patterns"""
    
    def __init__(self, pattern):
        self.pattern = pattern
        self.pos = 0
    
    def parse(self):
        """Parse the regex pattern into AST"""
        return self._parse_expr()
    
    def _parse_expr(self):
        """Parse expression (sequence of terms)"""
        terms = []
        while self.pos < len(self.pattern):
            char = self.pattern[self.pos]
            if char == ')':
                break
            terms.append(self._parse_term())
        return ('SEQ', terms) if len(terms) > 1 else (terms[0] if terms else ('EMPTY',))
    
    def _parse_term(self):
        """Parse a single term"""
        atom = self._parse_atom()
        
        if self.pos < len(self.pattern):
            char = self.pattern[self.pos]
            if char == '*':
                self.pos += 1
                return ('STAR', atom)
            elif char == '+':
                self.pos += 1
                return ('PLUS', atom)
            elif char == '?':
                self.pos += 1
                return ('OPTIONAL', atom)
        
        return atom
    
    def _parse_atom(self):
        """Parse an atom (character or group)"""
        if self.pos >= len(self.pattern):
            return ('EMPTY',)
        
        char = self.pattern[self.pos]
        self.pos += 1
        
        if char == '.':
            return ('ANY',)
        elif char == '(':
            expr = self._parse_expr()
            if self.pos < len(self.pattern) and self.pattern[self.pos] == ')':
                self.pos += 1
            return expr
        elif char == '\\' and self.pos < len(self.pattern):
            escaped = self.pattern[self.pos]
            self.pos += 1
            return ('CHAR', escaped)
        elif char in '*+?)|':
            self.pos -= 1
            return ('EMPTY',)
        else:
            return ('CHAR', char)


class RegexMatcher:
    """Match strings against regex patterns using backtracking"""
    
    def __init__(self, pattern):
        parser = RegexParser(pattern)
        self.ast = parser.parse()
    
    def match(self, text):
        """Check if text matches the pattern"""
        return self._match(self.ast, text, 0) is not None
    
    def search(self, text):
        """Search for pattern in text"""
        for i in range(len(text) + 1):
            result = self._match(self.ast, text, i)
            if result is not None:
                return (i, result)
        return None
    
    def _match(self, pattern, text, pos):
        """Match pattern against text starting at pos"""
        ptype = pattern[0]
        
        if ptype == 'EMPTY':
            return pos
        
        elif ptype == 'CHAR':
            if pos < len(text) and text[pos] == pattern[1]:
                return pos + 1
            return None
        
        elif ptype == 'ANY':
            if pos < len(text):
                return pos + 1
            return None
        
        elif ptype == 'SEQ':
            current_pos = pos
            for sub_pattern in pattern[1]:
                result = self._match(sub_pattern, text, current_pos)
                if result is None:
                    return None
                current_pos = result
            return current_pos
        
        elif ptype == 'STAR':
            # Try matching 0 times first
            result = pos
            while True:
                next_result = self._match(pattern[1], text, result)
                if next_result is None or next_result == result:
                    break
                result = next_result
            return result
        
        elif ptype == 'PLUS':
            # Must match at least once
            result = self._match(pattern[1], text, pos)
            if result is None:
                return None
            while True:
                next_result = self._match(pattern[1], text, result)
                if next_result is None or next_result == result:
                    break
                result = next_result
            return result
        
        elif ptype == 'OPTIONAL':
            # Try matching once
            result = self._match(pattern[1], text, pos)
            if result is not None:
                return result
            return pos
        
        return None


def regex_search(pattern, text):
    """Simple regex search function"""
    try:
        matcher = RegexMatcher(pattern)
        result = matcher.search(text)
        if result:
            start, end = result
            return text[start:end]
        return None
    except:
        # Fallback to simple string search
        if pattern in text:
            return pattern
        return None


def regex_match(pattern, text):
    """Simple regex match function"""
    try:
        matcher = RegexMatcher(pattern)
        return matcher.match(text)
    except:
        return text.startswith(pattern)
