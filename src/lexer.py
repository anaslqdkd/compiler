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
