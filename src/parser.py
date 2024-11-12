from lexer import *


if __name__ == "__main__":
    with open("/home/ash/pcl-grp31/tests/source_code.txt") as file:
        source_code = file.read()
        lexer = Lexer(source_code)
# tokens = lexer.tokenize()


class Parser:
    "lsdkfj"

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.tokenize()[0]
        self.index = 0
        self.tokens = self.lexer.tokenize()

    def move_forward(self):
        "lsdkfj"
        self.index += 1
        if self.index < len(self.lexer.tokens):
            self.current_token = self.tokens[self.index]

    def parse(self):
        "Axiome"
        return self.parse_s()

    def parse_s(self):
        "S"
        token = self.current_token()

        if token.type == TokenType.NEWLINE:
            self.move_forward()
            return self.parse_s_1()

        if token.type in [
            TokenType.DEF,
            TokenType.LSQUARE,
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.IF,
            TokenType.FOR,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.INTEGER,
        ]:

            return self.parse_s_1()
        return False

    def parse_s_1(self):
        "S'"
        token = self.current_token()

        if token.type == TokenType.DEF:
            self.parse_a()
            self.parse_s_1()
        self.parse_d()
        self.parse_s_2()
        # question pour " et string

    def parse_s_2(self):
        "S''"
        token = self.current_token()

        if token.type == TokenType.EOF:
            return True
        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LSQUARE,
            TokenType.LPAREN,
            TokenType.IF,
            TokenType.FOR,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.INTEGER,
        ]:
            self.parse_d()
            self.parse_s_2()
        else:
            return False

    def parse_a(self):
        "A"
        token = self.current_token()

        if token.type == TokenType.DEF:
            self.move_forward()
            # on ajoute def ident (I) à l'arbre
            self.parse_i()
            # on ajoute : aussi
            self.parse_b()
        else:
            return False

    def parse_i(self):
        "I"
        token = self.current_token()
        if token.type == TokenType.IDENTIFIER:
            self.move_forward()
            self.parse_i_1()
        return False

    def parse_i_1(self):
        "I'"
        token = self.current_token()
        if token.type == TokenType.COMMA:
            self.move_forward()
            self.parse_i_1()
        # if token.type == TokenType.LPAREN:
        #     self.move_forward()
        # idk ici I'->''
        else:
            return False

    def parse_b(self):
        "B"
        token = self.current_token()
        if token.type == TokenType.NEWLINE:
            self.move_forward()
            # on ajoute newline begin à l'arbre
            self.parse_d()
            self.parse_b_1()
            # on ajoute end à l'arbre
        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.IF,
            TokenType.FOR,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.INTEGER,
        ]:
            self.parse_c()
            # on ajoute Newline dans l'arbre après
        else:
            return False

    def parse_b_1(self):
        "B1"
        token = self.current_token()
        if token.type == TokenType.NEWLINE:
            self.move_forward()
            self.parse_d()
            self.parse_b_1()
        if token.type == TokenType.END:
            self.move_forward()
        else:
            return False

    def parse_c(self):
        "C"
        token = self.current_token()
        if token.type == TokenType.RETURN:
            self.move_forward()
            self.parse_e()
        if token.type == TokenType.IDENTIFIER:
            self.move_forward()
            self.parse_c_2()
        if token.type == TokenType.PRINT:
            self.move_forward()
            # on ajoute ( à l'arbre
            self.parse_e()
            # on ajoute ) à l'arbre
        if token.type in [
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.IF,
            TokenType.FOR,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.INTEGER,
        ]:
            self.parse_e()
            self.parse_c_1()
        else:
            return False

    def parse_c_1(self):
        "C'"
        token = self.current_token()
