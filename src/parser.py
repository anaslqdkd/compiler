from lexer import *

with open("../tests/source_code.txt", "r") as file:
    source_code = file.read()

lexer = Lexer(source_code)


# print(parser.lexer.get_next_token())
# print(parser.current_token)
# print(parser.next_token())
# current_token = parser.next_token()
# print(parser.current_token)


class Parser:
    "Parser class"

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def next_token(self):
        self.current_token = self.lexer.get_next_token()

    def get_token(self):
        return self.current_token

    def parse(self):
        "Axiome"
        return self.parse_s()

    def parse_s(self):
        "S"
        # ajouter S à l'arbre
        token = self.get_token()
        if token.type == TokenType.NEWLINE:
            # ajouter token à l'arbre
            self.next_token()
            return self.parse_s_1()

        if token.type in [
            TokenType.DEF,
            TokenType.LSQUARE,
            TokenType.IDENTIFIER,
            TokenType.RETURN,
            TokenType.LPAREN,
            TokenType.PRINT,
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
        # ajouter S' à l'arbre
        token = self.get_token()

        if token.type == TokenType.DEF:
            # ajouter token à l'arbre
            self.parse_a()
            self.parse_s_1()
        if token.type in [
            TokenType.LSQUARE,
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.RETURN,
            TokenType.PRINT,
            TokenType.IF,
            TokenType.FOR,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.INTEGER,
        ]:
            print("BUUU")
            # ajouter token à l'arbre
            self.parse_d()
            self.parse_s_2()

        return False

    def parse_s_2(self):
        "S''"
        # ajout S'' à l'arbre
        token = self.get_token()

        if token.type == TokenType.EOF:
            # ajout token à l'arbre
            return True

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LSQUARE,
            TokenType.LPAREN,
            TokenType.RETURN,
            TokenType.PRINT,
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
        return False

    def parse_a(self):
        "A"
        # on ajoute A à l'arbre
        token = self.get_token()

        if token.type == TokenType.DEF:
            # on ajoute token à l'arbre
            self.next_token()
            token = self.get_token()
            if token.type == TokenType.IDENTIFIER:
                # on ajoute token à l'arbre
                self.next_token()
                token = self.get_token()
                if token.type == TokenType.LPAREN:
                    # on ajoute token à l'arbre
                    self.parse_i()
                    token = self.get_token()
                    if token.type == TokenType.RPAREN:
                        # on ajoute token à l'arbre
                        self.next_token()
                        token = self.get_token()
                        if token.type == TokenType.COLON:
                            # on ajoute token à l'arbre
                            self.next_token()
                            self.parse_b()

        return False

    def parse_i(self):
        # on ajoute I à l'arbre
        "I"
        token = self.get_token()
        if token.type == TokenType.IDENTIFIER:
            # on ajoute le token à l'arbre
            self.next_token()
            self.parse_i_1()
        return False

    def parse_i_1(self):
        "I'"
        # on ajoute I' à l'arbre
        token = self.get_token()
        if token.type == TokenType.COMMA:
            # on ajoute token à l'arbre
            self.next_token()
            token = self.get_token()
            if token.type == TokenType.IDENTIFIER:
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_i_1()
        if token.type == TokenType.RPAREN:
            pass
        return False

    def parse_b(self):
        "B"
        # on ajoute B à l'arbre
        token = self.get_token()
        if token.type == TokenType.NEWLINE:
            # on ajoute token à l'arbre
            self.next_token()
            token = self.get_token()
            if token.type == TokenType.BEGIN:
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_d()
                self.parse_b_1()
                token = self.get_token()
                if token.type == TokenType.END:
                    # on ajoute token à l'arbre
                    self.next_token()

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.RETURN,
            TokenType.PRINT,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.INTEGER,
        ]:
            self.parse_c()
            token = self.get_token()
            if token.type == TokenType.NEWLINE:
                # on ajoute token à l'arbre
                self.next_token()
        return False

        #

    def parse_b_1(self):
        "B1"
        # on ajoute B' à l'arbre
        token = self.get_token()
        if token.type == TokenType.NEWLINE:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_d()
            self.parse_b_1()
        if token.type == TokenType.END:
            pass
        return False

    def parse_c(self):
        "C"
        # on ajoute C à l'arbre
        token = self.get_token()
        if token.type == TokenType.RETURN:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
        if token.type == TokenType.IDENTIFIER:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_c_2()
        if token.type == TokenType.PRINT:
            self.next_token()
            token = self.get_token()
            if token.type == TokenType.LPAREN:
                # je viens de voir un pb à voir, si on est ici on insère (
                # dans l'arbre mais si la suite ne correspond pas il faudra l'enlever
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_e()
                token = self.get_token()
                if token.type == TokenType.RPAREN:
                    # on ajoute token à l'arbre
                    self.next_token()

        if token.type in [
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.INTEGER,
        ]:
            self.parse_e()
            self.parse_c_1()
        return False

    def parse_c_1(self):
        "C'"
        # ajouter C' à l'arbre
        token = self.get_token()

        if token.type == TokenType.LSQUARE:
            # on ajouter token à l'arbre
            self.next_token()
            # self.parse_e()
            token = self.get_token()
            if token.type == TokenType.RSQUARE:
                # on ajoute token à l'arbre
                self.next_token()
                token = self.get_token()
                if token.type == TokenType.EQUALS:
                    # on ajoute token à l'arbre
                    self.next_token()
                    self.parse_e()
        if token.type == TokenType.NEWLINE:
            pass
        return False

    def parse_c_2(self):
        "C''"
        # on ajoute C'' à l'arbre
        token = self.get_token()

        if token.type == TokenType.EQUALS:
            # on ajoute token à l'arbre
            self.next_token()
            # self.parse_e()
        if token.type == TokenType.LPAREN:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_3()
            token = self.get_token()
            if token.type == TokenType.RPAREN:
                # on ajoute token à l'arbre
                self.next_token()

        if token.type == TokenType.NEWLINE:
            pass
        return False

    def parse_d(self):
        "D"
        # on ajoute D à l'arbre
        token = self.get_token()

        if token.type == TokenType.IF:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
            token = self.get_token()
            if token.type == TokenType.COLON:
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_b()
                self.parse_d_1()
        if token.type == TokenType.FOR:
            # on ajoute token à l'arbre
            self.next_token()
            token = self.get_token()
            if token.type == TokenType.IDENTIFIER:
                # on ajoute token à) l'arbre
                self.next_token()
                token = self.get_token()
                if token.type == TokenType.IN:
                    # on ajoute token à l'arbre
                    self.next_token()
                    self.parse_e()
                    token = self.get_token()
                    if token.type == TokenType.COLON:
                        # on ajoute token à l'arbre
                        self.next_token()
                        self.parse_b()

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.RETURN,
            TokenType.PRINT,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.INTEGER,
        ]:
            self.parse_c()
            token = self.get_token()
            if token.type == TokenType.NEWLINE:
                # on ajoute token à l'arbre
                self.next_token()
        return False

    def parse_d_1(self):
        "D1"
        # on ajoute D' à l'arbre

        token = self.get_token()
        if token.type == TokenType.ELSE:
            # on ajoute token à l'arbre
            self.next_token()
            token = self.get_token()
            if token.type == TokenType.COLON:
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_b()
        if token.type in [
            TokenType.EOF,
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.RETURN,
            TokenType.PRINT,
            TokenType.IF,
            TokenType.FOR,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.INTEGER,
        ]:
            pass
        return False

    def parse_f(self):
        "F"
        # on ajoute F à l'arbre
        token = self.get_token()
        if token.type in [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MULTIPLY,
            TokenType.FLOOR_DIVIDE,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.NOT_EQUAL,
            TokenType.AND,
            TokenType.OR,
        ]:
            print("FFF")
            # on ajoute token à l'arbre
            self.next_token()
        return False

    def parse_g(self):
        "G"
        # on ajoute G à l'arbre
        token = self.get_token()
        if token.type == TokenType.INTEGER:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_g_1()
        return False

    def parse_g_1(self):
        "G'"
        # on ajoute G' à l'arbre
        token = self.get_token()
        if token.type == TokenType.INTEGER:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_g_1()
        if token.type in [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MULTIPLY,
            TokenType.FLOOR_DIVIDE,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.NOT_EQUAL,
            TokenType.AND,
            TokenType.OR,
            TokenType.COMMA,
            TokenType.NEWLINE,
            TokenType.RPAREN,
            TokenType.LSQUARE,
            TokenType.RSQUARE,
        ]:
            pass
        return False

    # à faire la suite
    def parse_h(self):
        "H"
        # on ajoute H à l'arbre

    def parse_e(self):
        "E"
        # on ajoute E à l'arbre

    def parse_e_1(self):
        "E'"
        # on ajoute E à l'arbre

    def parse_e_2(self):
        "E''"
        # on ajoute E à l'arbre

    def parse_e_3(self):
        "E'''"
        # on ajoute E à l'arbre

    def parse_e_s(self):
        "E*"
        # on ajoute E à l'arbre


# parser = Parser(lexer)
# parser.parse()
# print(parser.parse())
