class SyntaxError(Exception):
    def __int__(self, message, line):
        super().__init__(f"Syntax Error on line {line}: message")
