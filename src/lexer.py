class TokenType:
    KEYWORDS = {
        "if": "IF",
        "else": "ELSE",
        "and": "AND",
        "or": "OR",
        "not": "NOT",
        "True": "TRUE",
        "False": "FALSE",
        "None": "NONE",
        "def": "DEF",
        "return": "RETURN",
        "print": "PRINT",
        "for": "FOR",
        "in": "IN"
    }

    OPERATORS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "MULTIPLY",
        "/": "DIVIDE", # Unused
        "//": "FLOOR_DIVIDE",
        "%": "MODULO",
        "<=": "LESS_EQUAL",
        ">=": "GREATER_EQUAL",
        ">": "GREATER",
        "<": "LESS",
        "!": "NOT", # Unused
        "!=": "NOT_EQUAL",
        "==": "EQUAL_EQUAL",
        "=": "EQUALS"
    }

    SYMBOLS = {
        "(": "LPAREN",
        ")": "RPAREN",
        "{": "LCURLY",
        "}": "RCURLY",
        "[": "LSQUARE",
        "]": "RSQUARE",
        ":": "COLON",
        ",": "COMMA"
    }

    # Add BEGIN, END, NEWLINE, INTEGER, STRING, IDENTIFIER, EOF tokens as needed by the lexer
    BEGIN = "BEGIN"
    END = "END"
    NEWLINE = "NEWLINE"
    INTEGER = "INTEGER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    EOF = "EOF"

class Token:
    def __init__(self, type, line_number, value=None):
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
        self.identifier_lexicon = {}
        self.next_identifier_index = 1

    def get_next_token(self):
        while self.position < len(self.source_code):
            char = self.source_code[self.position]
            
            if char in " \t":
                self.advance()
            elif char == "#":
                self.skip_comment()
            elif char == "\n":
                self.advance()
                return Token(TokenType.NEWLINE, self.line_number)
            elif char.isalpha() or char == "_":
                return self.process_identifier()
            elif char.isdigit():
                return self.process_integer()
            elif char == '"':
                return self.process_string()
            elif char in TokenType.OPERATORS:
                return self.process_operator()
            elif char in TokenType.SYMBOLS:
                return self.process_symbol()
            else:
                raise SyntaxError(f"Unexpected character '{char}' at line {self.line_number}")

        return Token(TokenType.EOF, self.line_number)

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
            return Token(TokenType.BEGIN, self.line_number, indent_level)
        elif indent_level < self.indent_stack[-1]:
            tokens = []
            while self.indent_stack and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.END, self.line_number))
            if self.indent_stack[-1] != indent_level:
                raise SyntaxError(f"Indentation error at line {self.line_number}")
            return tokens

    def process_identifier(self):
        start_pos = self.position
        while self.position < len(self.source_code) and (self.source_code[self.position].isalnum() or self.source_code[self.position] == "_"):
            self.advance()
        value = self.source_code[start_pos:self.position]
        
        token_type = TokenType.KEYWORDS.get(value, TokenType.IDENTIFIER)
        if token_type == TokenType.IDENTIFIER:
            if value not in self.identifier_lexicon:
                self.identifier_lexicon[value] = self.next_identifier_index
                self.next_identifier_index += 1
            return Token(token_type, self.line_number, self.identifier_lexicon[value])
        else:
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
        start_pos = self.position
        two_char_op = self.source_code[self.position:self.position + 2]

        if two_char_op in TokenType.OPERATORS:
            self.advance(2)
            return Token(TokenType.OPERATORS[two_char_op], self.line_number)
        elif self.source_code[start_pos] in TokenType.OPERATORS:
            op = self.source_code[start_pos]
            self.advance()
            return Token(TokenType.OPERATORS[op], self.line_number)
        else:
            raise SyntaxError(f"Unexpected operator '{self.source_code[start_pos]}' at line {self.line_number}")

    def process_symbol(self):
        char = self.source_code[self.position]
        self.advance()
        return Token(TokenType.SYMBOLS[char], self.line_number)

    def advance(self, steps=1):
        self.position += steps
        if self.source_code[self.position - steps] == "\n":
            self.line_number += 1
