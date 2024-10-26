class TokenType:
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NONE = "NONE"
    DEF = "DEF"
    RETURN = "RETURN"
    PRINT = "PRINT"
    IF = "IF"
    ELSE = "ELSE"
    FOR = "FOR"
    IN = "IN"
    
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    FLOOR_DIVIDE = "FLOOR_DIVIDE"
    MODULO = "MODULO"
    GREATER = "GREATER"
    LESS = "LESS"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    EQUALS = "EQUALS"

    LPAREN =  "LPAREN"
    RPAREN = "RPAREN"
    LCURLY = "LCURLY"
    RCURLY = "RCURLY"
    LSQUARE = "LSQUARE"
    RSQUARE = "RSQUARE"
    COLON = "COLON"
    COMMA = "COMMA"

    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    INTEGER = "INTEGER"

    BEGIN = "BEGIN"
    END = "END"

    NEWLINE = "NEWLINE"

    EOF = "EOF"
        
class Token:
    def __init__(self, type, line_number, value = None):
        self.type = type
        self.line_number = line_number
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value}, line={self.line_number})" if self.value else f"Token({self.type}, line={self.line_number})"

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.line_number = 1
        self.indent_stack = [0]
        self.tokens = []

        self.keywords = {"if", "else", "and", "or", "not", "True", "False", "None", "def", "return", "print", "for", "in"}
        self.operators = {"+", "-", "*", "/", "%", "<", ">", "=", "!"}
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
                self.tokens.append(Token(TokenType.NEWLINE, self.line_number))
                self.line_number += 1
                self.handle_indentation()
            elif char.isalpha() or char == "_":
                self.tokens.append(self.process_identifier())
            elif char.isdigit():
                self.tokens.append(self.process_integer())
            elif char == '"':
                self.tokens.append(self.process_string())
            elif char in self.operators:
                self.tokens.append(self.process_operator())
            elif char in self.symbols:
                self.tokens.append(self.process_symbol())
            else:
                raise SyntaxError(f"Unexpected character '{char}' at line {self.line_number}")

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.END, self.indent_stack[-1], self.line_number))
        
        self.tokens.append(Token(TokenType.EOF, self.line_number))
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
            self.tokens.append(Token(TokenType.BEGIN, self.line_number, indent_level))
        elif indent_level < self.indent_stack[-1]:
            while self.indent_stack and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.END, self.line_number, self.indent_stack[-1]))
            if self.indent_stack[-1] != indent_level:
                raise SyntaxError(f"Indentation error at line {self.line_number}")

    def process_identifier(self):
        keyword_tokens = {
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "not": TokenType.NOT,
            "True": TokenType.TRUE,
            "False": TokenType.FALSE,
            "None": TokenType.NONE,
            "def": TokenType.DEF,
            "return": TokenType.RETURN,
            "print": TokenType.PRINT,
            "for": TokenType.FOR,
            "in": TokenType.IN
        }

        start_pos = self.position
        while self.position < len(self.source_code) and (self.source_code[self.position].isalnum() or self.source_code[self.position] == "_"):
            self.advance()
        value = self.source_code[start_pos:self.position]
        token_type = keyword_tokens[value] if value in self.keywords else TokenType.IDENTIFIER
        return Token(token_type, self.line_number, value)
    
    def process_integer(self):
        start_pos = self.position
        while self.position < len(self.source_code) and self.source_code[self.position].isdigit():
            self.advance()
        value = int(self.source_code[start_pos:self.position])
        return Token(TokenType.INTEGER, self.line_number, value)
    
    def process_string(self):
        self.advance()
        string_value = ""
        while self.position < len(self.source_code):
            char = self.source_code[self.position]
            if char == '"':
                self.advance()
                return Token(TokenType.STRING, self.line_number, f"\"{string_value}\"")
            elif char == "\\":
                self.advance()
                next_char = self.source_code[self.position]
                if next_char == '"':
                    string_value += '\\"'
                elif next_char == "n":
                    string_value += "\\n"
                else:
                    raise SyntaxError(f"Invalid escape sequence at line {self.line_number}")
            else:
                string_value += char
            self.advance()
        raise SyntaxError(f"Unterminated string literal at line {self.line_number}")
    
    def process_operator(self):
        operator_tokens = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "//": TokenType.FLOOR_DIVIDE,
            "%": TokenType.MODULO,
            "<=": TokenType.LESS_EQUAL,
            ">=": TokenType.GREATER_EQUAL,
            ">": TokenType.GREATER,
            "<": TokenType.LESS,
            "!=": TokenType.NOT_EQUAL,
            "==": TokenType.EQUAL_EQUAL,
            "=": TokenType.EQUALS
        }

        char = self.source_code[self.position]
        next_char = self.source_code[self.position + 1] if self.position + 1 < len(self.source_code) else ""

        two_char_op = char + next_char
        if two_char_op in operator_tokens:
            token_type = operator_tokens[two_char_op]
            self.advance()

        elif char in operator_tokens:
            token_type = operator_tokens[char]
        else:
            raise SyntaxError(f"Unexpected operator '{char}' at line {self.line_number}")

        self.advance()
        return Token(token_type, self.line_number)

    def process_symbol(self):
        symbols_tokens = {
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LCURLY,
            "}": TokenType.RCURLY,
            "[": TokenType.LSQUARE,
            "]": TokenType.RSQUARE,
            ":": TokenType.COLON,
            ",": TokenType.COMMA
        }
        char = self.source_code[self.position]

        self.advance()
        return Token(symbols_tokens[char], self.line_number)

    
    def advance(self):
        self.position += 1
