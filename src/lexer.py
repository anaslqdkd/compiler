class TokenType:
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    INTEGER = "INTEGER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    LESS_THAN_EQUAL = "LESS_THAN_EQUAL"
    GREATER_THAN_EQUAL = "GREATER_THAN_EQUAL"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    NOT_EQUAL = "NOT_EQUAL"
    EQUAL = "EQUAL"
    AND = "AND"
    OR = "OR"
    ASSIGN = "ASSIGN"
    SYMBOL = "SYMBOL"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    NEWLINE = "NEWLINE"
    EOF = "EOF"
        
class Token:
    def __init__(self, type_, value, line_number):
        self.type = type_
        self.value = value
        self.line_number = line_number

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line_number})"

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.line_number = 1
        self.indent_stack = [0]
        self.tokens = []

        self.keywords = {"if", "else", "and", "or", "not", "True", "False", "None", "def", "return", "print", "for", "in"}
        self.symbols = {"(", ")", "{", "}", "[", "]", ":", ","}

    def tokenize(self):
        while self.position < len(self.source_code):
            char = self.source_code[self.position]
            
            if char == " " or char == "\t":
                self.position += 1
            elif char == "#":
                self.skip_comment()
            elif char == "\n":
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, None, self.line_number))
                self.line_number += 1
                self.handle_indentation()
            elif char.isalpha() or char == "_":
                self.tokens.append(self.process_identifier())
            elif char.isdigit():
                self.tokens.append(self.process_integer())
            elif char == '"':
                self.tokens.append(self.process_string())
            elif char in {"+", "-", "*", "/", "%", "<", ">", "=", "!"}:
                self.tokens.append(self.process_operator())
            elif char in self.symbols:
                self.tokens.append(Token(TokenType.SYMBOL, char, self.line_number))
                self.advance()
            else:
                raise SyntaxError(f"Unexpected character '{char}' at line {self.line_number}")

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, self.indent_stack[-1], self.line_number))
        
        self.tokens.append(Token(TokenType.EOF, None, self.line_number))
        return self.tokens
    
    def skip_comment(self):
        while self.position < len(self.source_code) and self.source_code[self.position] != "\n":
            self.advance()
            
    def handle_indentation(self):
        indent_level = 0
        while self.position < len(self.source_code) and self.source_code[self.position] == " ":
            indent_level += 1
            self.advance()
        if indent_level % 4 != 0:
            raise SyntaxError(f"Indentation error at line {self.line_number}: Indentation must be multiple of 4")
        
        if indent_level > self.indent_stack[-1]:
            self.indent_stack.append(indent_level)
            self.tokens.append(Token(TokenType.INDENT, indent_level, self.line_number))
        elif indent_level < self.indent_stack[-1]:
            while self.indent_stack and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, self.indent_stack[-1], self.line_number))
            if self.indent_stack[-1] != indent_level:
                raise SyntaxError(f"Indentation error at line {self.line_number}")

    def process_identifier(self):
        start_pos = self.position
        while self.position < len(self.source_code) and (self.source_code[self.position].isalnum() or self.source_code[self.position] == "_"):
            self.advance()
        value = self.source_code[start_pos:self.position]
        token_type = TokenType.KEYWORD if value in self.keywords else TokenType.IDENTIFIER
        return Token(token_type, value, self.line_number)