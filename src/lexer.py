class TokenType:
    lexicon = {
        1: "BEGIN", 2: "END", 3: "NEWLINE", 4: "EOF",
        10: "IDENTIFIER", 11: "INTEGER", 12: "STRING",
        20: "if", 21: "else", 22: "and", 23: "or", 24: "not", 
        25: "True", 26: "False", 27: "None", 28: "def", 
        29: "return", 30: "print", 31: "for", 32: "in",
        40: "+", 41: "-", 42: "*", 43: "//", 44: "%", 
        45: "<=", 46: ">=", 47: ">", 48: "<", 
        49: "!=", 50: "==", 51: "=", 52: "/", 53: "!",
        60: "(", 61: ")", 62: "[", 63: "]", 64: ":", 65: ","
    }
    
    @classmethod
    def get_key_by_value(cls, value):
        for key, val in cls.lexicon.items():
            if val == value:
                return key
        return None
    
    @classmethod
    def get_token_category(cls, token_number):
        """
        Determine the category of a token based on its number.
        
        Args:
            token_number (int): The number of the token
        
        Returns:
            str: The category of the token
        """
        if 1 <= token_number <= 4:
            return "STRUCTURE"
        elif 10 <= token_number <= 12:
            return "VALUE"
        elif 20 <= token_number <= 32:
            return "KEYWORDS"
        elif 40 <= token_number <= 53:
            return "OPERATORS"
        elif 60 <= token_number <= 67:
            return "SYMBOLS"
        else:
            return "UNKNOWN"

class Token:
    def __init__(self, number, line, value=None):
        self.number = number
        self.value = value
        self.line = line
        self.category = TokenType.get_token_category(number)

    def __repr__(self):
        return f"Token({self.number}, {self.value}, line={self.line})"

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.line_number = 1
        self.indent_stack = [0]
        
        # Two separate lexicons
        self.identifier_lexicon = {}
        self.constant_lexicon = {}
        
        # Counters for lexicon indices
        self.next_identifier_index = 1
        self.next_constant_index = 1

        self.expect_indent = False

    def get_next_token(self, advance_cursor=True):
        original_position = self.position
        original_line_number = self.line_number

        try:
            while self.position < len(self.source_code):
                # Handle indentation at the beginning of lines
                if self.position == 0 or (self.position > 0 and self.source_code[self.position - 1] == "\n"):
                    indent_token = self.handle_indentation()
                    if indent_token:
                        return indent_token
                    
                char = self.source_code[self.position]
                
                if char in " \t":
                    self.advance()
                elif char == "#":
                    self.skip_comment()
                elif char == "\n":
                    self.advance()
                    token = Token(3, self.line_number)  # NEWLINE token
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
                elif char in ['+', '-', '*', '/', '%', '=', '<', '>', '!']:
                    token = self.process_operator()
                    break
                elif char in ['(', ')', '{', '}', '[', ']', ':', ',']:
                    token = self.process_symbol()
                    break
                else:
                    raise SyntaxError(f"Unexpected character '{char}' at line {self.line_number}")

            else:
                token = Token(4, self.line_number)  # EOF token

            # If we don't want to advance, we reposition
            if not advance_cursor:
                self.position = original_position
                self.line_number = original_line_number

            return token

        except Exception as e:
            # In case of error, reposition
            self.position = original_position
            self.line_number = original_line_number
            raise e

    def process_identifier(self):
        start_pos = self.position
        while self.position < len(self.source_code) and (self.source_code[self.position].isalnum() or self.source_code[self.position] == "_"):
            self.advance()
        value = self.source_code[start_pos:self.position]
        
        # Check if it's a keyword
        for token_num, token_value in TokenType.lexicon.items():
            if value == token_value and 20 <= token_num <= 32:
                return Token(token_num, self.line_number, value)
        
        # Otherwise, it's an identifier
        if value not in self.identifier_lexicon.values():
            self.identifier_lexicon[self.next_identifier_index] = value
            index = self.next_identifier_index
            self.next_identifier_index += 1
        else:
            # Find existing index
            index = next(k for k, v in self.identifier_lexicon.items() if v == value)
        
        return Token(10, self.line_number, index)

    def process_integer(self):
        start_pos = self.position
        while self.position < len(self.source_code) and self.source_code[self.position].isdigit():
            self.advance()
        value = int(self.source_code[start_pos:self.position])
        
        # Add to constant lexicon if not already present
        if value not in self.constant_lexicon.values():
            self.constant_lexicon[self.next_constant_index] = value
            index = self.next_constant_index
            self.next_constant_index += 1
        else:
            # Find existing index
            index = next(k for k, v in self.constant_lexicon.items() if v == value)
        
        return Token(11, self.line_number, index)

    def process_string(self):
        self.advance()
        string_value = ""
        while self.position < len(self.source_code):
            char = self.source_code[self.position]
            if char == '"':
                self.advance()
                
                # Add to constant lexicon if not already present
                full_string = f'"{string_value}"'
                if full_string not in self.constant_lexicon.values():
                    self.constant_lexicon[self.next_constant_index] = full_string
                    index = self.next_constant_index
                    self.next_constant_index += 1
                else:
                    # Find existing index
                    index = next(k for k, v in self.constant_lexicon.items() if v == full_string)
                
                return Token(12, self.line_number, index)
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

        # Check for two-character operators first
        if two_char_op in TokenType.lexicon.values():
            token_number = TokenType.get_key_by_value(two_char_op)
            self.advance(2)
            return Token(token_number, self.line_number)
        
        # Single character operators
        single_char_op = self.source_code[start_pos]
        if single_char_op in TokenType.lexicon.values():
            token_number = TokenType.get_key_by_value(single_char_op)
            self.advance()
            return Token(token_number, self.line_number, single_char_op)
        
        raise SyntaxError(f"Unexpected operator '{self.source_code[start_pos]}' at line {self.line_number}")


    def process_symbol(self):
        char = self.source_code[self.position]
        
        if char in TokenType.lexicon.values():
            token_number = TokenType.get_key_by_value(char)
            self.advance()
            # Set expect_indent flag when we see a colon
            if char == ':':
                self.expect_indent = True
            return Token(token_number, self.line_number, char)
        
        raise SyntaxError(f"Unexpected symbol '{char}' at line {self.line_number}")


    def skip_comment(self):
        while self.position < len(self.source_code) and self.source_code[self.position] != "\n":
            self.advance()
            
    def peek_next_token(self):
        return self.get_next_token(advance_cursor=False)

    def advance(self, steps=1):
        self.position += steps
        if self.position > 0 and self.source_code[self.position - steps] == "\n":
            self.line_number += 1

    def handle_indentation(self):
        current_indent = 0
        
        # Count spaces at the beginning of the line
        while self.position < len(self.source_code) and self.source_code[self.position] in " \t":
            if self.source_code[self.position] == " ":
                current_indent += 1
            elif self.source_code[self.position] == "\t":
                current_indent += 4
            self.advance()
        
        # If this is just a blank line or comment, ignore indentation
        if (self.position < len(self.source_code) and 
            (self.source_code[self.position] == "\n" or self.source_code[self.position] == "#")):
            return None
            
        # Check for required indentation after colon
        if self.expect_indent and current_indent <= self.indent_stack[-1]:
            raise IndentationError(f"Expected an indented block at line {self.line_number}")
        
        self.expect_indent = False  # Reset the flag
        
        # Rest of the existing handle_indentation code...
        prev_indent = self.indent_stack[-1]
        
        if current_indent > prev_indent:
            self.indent_stack.append(current_indent)
            return Token(1, self.line_number)  # BEGIN token
        elif current_indent < prev_indent:
            if current_indent not in self.indent_stack:
                raise IndentationError(f"Invalid indentation at line {self.line_number}")
            while self.indent_stack[-1] > current_indent:
                self.indent_stack.pop()
                return Token(2, self.line_number)  # END token
        return None