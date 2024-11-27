class TokenType:
    # Numérotation des tokens
    TOKEN_NUMBERS = {
        "STRUCTURE": {
            "BEGIN": 1, "END": 2, "NEWLINE": 3, "EOF": 4
        },
        "VALUE": {
            "IDENTIFIER": 10, "INTEGER": 11, "STRING": 12
        },
        "KEYWORDS": {
            "if": 20, "else": 21, "and": 22, "or": 23, "not": 24, 
            "True": 25, "False": 26, "None": 27, "def": 28, 
            "return": 29, "print": 30, "for": 31, "in": 32
        },
        "OPERATORS": {
            "+": 40, "-": 41, "*": 42, "//": 43, "%": 44, 
            "<=": 45, ">=": 46, ">": 47, "<": 48, 
            "!=": 49, "==": 50, "=": 51, "/": 52, "!": 53
        },
        "SYMBOLS": {
            "(": 60, ")": 61, "{": 62, "}": 63, 
            "[": 64, "]": 65, ":": 66, ",": 67
        }
    }

    # Méthode pour récupérer les numéros de token
    @classmethod
    def get_token_number(cls, category, token):
        return cls.TOKEN_NUMBERS[category].get(token)

class Token:
    def __init__(self, type, line_number, token_number, value=None):
        self.type = type
        self.line_number = line_number
        self.token_number = token_number
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.token_number}, {self.value}, line={self.line_number})"

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.line_number = 1
        self.indent_stack = [0]
        
        # Deux lexiques séparés
        self.identifier_lexicon = {}
        self.constant_lexicon = {}
        
        # Compteurs pour les indices des lexiques
        self.next_identifier_index = 1
        self.next_constant_index = 1

    def get_next_token(self, advance_cursor=True):
        original_position = self.position
        original_line_number = self.line_number

        try:
            while self.position < len(self.source_code):
                char = self.source_code[self.position]
                
                if char in " \t":
                    self.advance()
                elif char == "#":
                    self.skip_comment()
                elif char == "\n":
                    self.advance()
                    token = Token("NEWLINE", self.line_number, 
                                 TokenType.get_token_number('STRUCTURE', 'NEWLINE'))
                    break
                elif char.isalpha() or char == "_":
                    token = self.process_identifier()
                    break
                elif char.isdigit():
                    token = self.process_integer()
                    break
                elif char == '"':
                    token = self.process_string()
                    break
                elif char in TokenType.TOKEN_NUMBERS['OPERATORS']:
                    token = self.process_operator()
                    break
                elif char in TokenType.TOKEN_NUMBERS['SYMBOLS']:
                    token = self.process_symbol()
                    break
                else:
                    raise SyntaxError(f"Unexpected character '{char}' at line {self.line_number}")

            else:
                token = Token("EOF", self.line_number, 
                             TokenType.get_token_number('STRUCTURE', 'EOF'))

            # Si on ne veut pas avancer, on repositionne
            if not advance_cursor:
                self.position = original_position
                self.line_number = original_line_number

            return token

        except Exception as e:
            # En cas d'erreur, repositionner
            self.position = original_position
            self.line_number = original_line_number
            raise e

    def process_identifier(self):
        start_pos = self.position
        while self.position < len(self.source_code) and (self.source_code[self.position].isalnum() or self.source_code[self.position] == "_"):
            self.advance()
        value = self.source_code[start_pos:self.position]
        
        # Vérifier si c'est un mot-clé
        if value in TokenType.TOKEN_NUMBERS['KEYWORDS']:
            token_number = TokenType.get_token_number('KEYWORDS', value)
            return Token(value, self.line_number, token_number, value)
        
        # Sinon c'est un IDENTIFIER
        if value not in self.identifier_lexicon.values():
            self.identifier_lexicon[self.next_identifier_index] = value
            index = self.next_identifier_index
            self.next_identifier_index += 1
        else:
            # Trouver l'index existant
            index = next(k for k, v in self.identifier_lexicon.items() if v == value)
        
        return Token("IDENTIFIER", self.line_number, 
                     TokenType.get_token_number('VALUE', 'IDENTIFIER'), 
                     index)

    def process_integer(self):
        start_pos = self.position
        while self.position < len(self.source_code) and self.source_code[self.position].isdigit():
            self.advance()
        value = int(self.source_code[start_pos:self.position])
        
        # Ajouter au lexique des constantes si pas déjà présent
        if value not in self.constant_lexicon.values():
            self.constant_lexicon[self.next_constant_index] = value
            index = self.next_constant_index
            self.next_constant_index += 1
        else:
            # Trouver l'index existant
            index = next(k for k, v in self.constant_lexicon.items() if v == value)
        
        return Token("INTEGER", self.line_number, 
                     TokenType.get_token_number('VALUE', 'INTEGER'), 
                     index)

    def process_string(self):
        self.advance()
        string_value = ""
        while self.position < len(self.source_code):
            char = self.source_code[self.position]
            if char == '"':
                self.advance()
                
                # Ajouter au lexique des constantes si pas déjà présent
                full_string = f'"{string_value}"'
                if full_string not in self.constant_lexicon.values():
                    self.constant_lexicon[self.next_constant_index] = full_string
                    index = self.next_constant_index
                    self.next_constant_index += 1
                else:
                    # Trouver l'index existant
                    index = next(k for k, v in self.constant_lexicon.items() if v == full_string)
                
                return Token("STRING", self.line_number, 
                             TokenType.get_token_number('VALUE', 'STRING'), 
                             index)
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

        if two_char_op in TokenType.TOKEN_NUMBERS['OPERATORS']:
            self.advance(2)
            return Token("OPERATOR", self.line_number, 
                         TokenType.get_token_number('OPERATORS', two_char_op))
        elif self.source_code[start_pos] in TokenType.TOKEN_NUMBERS['OPERATORS']:
            op = self.source_code[start_pos]
            self.advance()
            return Token("OPERATOR", self.line_number, 
                         TokenType.get_token_number('OPERATORS', op))
        else:
            raise SyntaxError(f"Unexpected operator '{self.source_code[start_pos]}' at line {self.line_number}")

    def process_symbol(self):
        char = self.source_code[self.position]
        self.advance()
        return Token("SYMBOL", self.line_number, 
                     TokenType.get_token_number('SYMBOLS', char))

    def skip_comment(self):
        while self.position < len(self.source_code) and self.source_code[self.position] != "\n":
            self.advance()
            
    def peek_next_token(self):
        return self.get_next_token(advance_cursor=False)

    def advance(self, steps=1):
        self.position += steps
        if self.position > 0 and self.source_code[self.position - steps] == "\n":
            self.line_number += 1