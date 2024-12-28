from lexer import *

pylint: disable = all

with open("../tests/source_code.txt", "r") as file:
    source_code = file.read()

lexer = Lexer(source_code)


class Parser:
    "Parser class"

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def next_token(self):
        self.current_token = self.lexer.get_next_token()

    def get_token(self):
        return self.current_token

    def peek_next_token(self):
        return self.lexer.peek_next_token()

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
            TokenType.CONST,
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
            TokenType.CONST,
        ]:
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
            # on renvoie l'arbre
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
            TokenType.CONST,
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
            TokenType.CONST,
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
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_e()
                self.parse_c_1()
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
            TokenType.CONST,
        ]:
            self.parse_e()
            self.parse_c_1()
        if token.type == TokenType.IDENTIFIER:
            snd_token = self.peek_next_token()
            if snd_token.type in [
                TokenType.NEWLINE,
                TokenType.LPAREN,
                TokenType.EQUALS,
            ]:
                self.next_token()
                self.parse_c_2()
            if snd_token.type in [
                TokenType.IDENTIFIER,
                TokenType.LPAREN,
                TokenType.LSQUARE,
                TokenType.NOT,
                TokenType.MINUS,
                TokenType.CONST,
                TokenType.TRUE,
                TokenType.FALSE,
                TokenType.NONE,
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
            self.parse_e()
        if token.type == TokenType.LPAREN:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_1()
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
            TokenType.CONST,
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
            TokenType.NEWLINE,
            TokenType.END,
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
            TokenType.CONST,
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
        token = self.get_token()

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.CONST,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.NOT,
            TokenType.MINUS,
            TokenType.CONST,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            self.parse_e_or()

    def parse_e_or(self):
        "E'"
        # on ajoute E à l'arbre
        token = self.get_token()

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.NOT,
            TokenType.MINUS,
            TokenType.CONST,
            TokenType.TRUE,
            TokenType.CONST,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            self.parse_e_and()
            self.parse_e_or_tail()

    def parse_e_or_tail(self):
        token = self.get_token()

        if token.type in [
            TokenType.NEWLINE,
            TokenType.LPAREN,
            TokenType.COLON,
            TokenType.COMMA,
            TokenType.LSQUARE,
            TokenType.RSQUARE,
        ]:
            pass
        if token.type == TokenType.OR:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_and()
            self.parse_e_or_tail()
        return False

    def parse_e_and(self):
        "E''"
        # on ajoute E à l'arbre
        token = self.get_token()

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.NOT,
            TokenType.MINUS,
            TokenType.CONST,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            self.parse_e_not()
            self.parse_e_and_tail()
        return False

    def parse_e_and_tail(self):
        token = self.get_token()

        if token.type in [
            TokenType.NEWLINE,
            TokenType.RPAREN,
            TokenType.COLON,
            TokenType.COMMA,
            TokenType.LSQUARE,
            TokenType.OR,
        ]:
            pass
        if token.type == TokenType.AND:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_not()
            self.parse_e_and_tail()
        return False

    def parse_e_not(self):

        token = self.get_token()

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.MINUS,
            TokenType.CONST,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            self.parse_e_rel()
        if token.type == TokenType.NOT:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_rel()
        return False

    def parse_e_rel(self):
        token = self.get_token()

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.MINUS,
            TokenType.CONST,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            self.parse_e_add()
            self.parse_e_rel_tail()
        return False

    def parse_e_rel_tail(self):
        token = self.get_token()
        if token.type in [
            TokenType.NEWLINE,
            TokenType.RPAREN,
            TokenType.COLON,
            TokenType.COMMA,
            TokenType.LSQUARE,
            TokenType.RSQUARE,
            TokenType.OR,
            TokenType.AND,
        ]:
            pass
        if token.type in [
            TokenType.GREATER_OR_EQUAL,
            TokenType.LESS_OR_EQUAL,
            TokenType.GREATER,
            TokenType.LESS,
            TokenType.EQUALS,
            TokenType.NEQUAL,
        ]:
            self.parse_o_r()
            self.parse_e_add()
            self.parse_e_rel_tail()
        return False

    def parse_e_add(self):
        token = self.get_token()

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.MINUS,
            TokenType.CONST,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            self.parse_e_mult()
            self.parse_e_add_tail()
        return False

    def parse_e_add_tail(self):
        token = self.get_token()

        if token.type in [
            TokenType.NEWLINE,
            TokenType.RPAREN,
            TokenType.COLON,
            TokenType.COMMA,
            TokenType.LSQUARE,
            TokenType.RSQUARE,
            TokenType.OR,
            TokenType.AND,
            TokenType.GREATER_EQUAL,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.LESS,
            TokenType.NOT_EQUAL,
            TokenType.EQUALS,
        ]:
            pass
        if token.type == TokenType.PLUS:
            self.parse_o_plus()
            self.parse_e_mult()
            self.parse_e_add_tail()
        return False

    def parse_e_mult(self):
        token = self.get_token()

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LSQUARE,
            TokenType.MINUS,
            TokenType.CONST,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            self.parse_e_un()
            self.parse_e_mult_tail()
        return False

    def parse_e_mult_tail(self):
        token = self.get_token()

        if token.type in [
            TokenType.NEWLINE,
            TokenType.RPAREN,
            TokenType.COLON,
            TokenType.COMMA,
            TokenType.LSQUARE,
            TokenType.RSQUARE,
            TokenType.OR,
            TokenType.AND,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.NOT_EQUAL,
            TokenType.EQUALS,
            TokenType.PLUS,
        ]:
            pass

        if token.type in [TokenType.MULTIPLY, TokenType.FLOOR_DIVIDE, TokenType.MODULO]:
            self.parse_o_star()
            self.parse_e_un()
            self.parse_e_mult_tail()
        return False

    def parse_e_un(self):
        token = self.get_token()

        if token.type == TokenType.LPAREN:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
            token = self.get_token()
            if token.type == TokenType.RPAREN:
                # on ajoute token à l'arbre
                self.next_token()
        if token.type == TokenType.LSQUARE:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
            token = self.get_token()
            if token.type == TokenType.RSQUARE:
                # on ajoute token à l'arbre
                self.next_token()
        if token.type == TokenType.MINUS:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_un()

        if token.type in [
            TokenType.IDENTIFIER,
            TokenType.CONST,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            self.parse_o_un()
        return False

    def parse_e_1(self):
        token = self.get_token()

        if token.type in [
            TokenType.LPAREN,
            TokenType.IDENTIFIER,
            TokenType.LSQUARE,
            TokenType.NOT,
            TokenType.MINUS,
            TokenType.CONST,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            self.parse_e()
            self.parse_e_2()
        return False

    def parse_e_2(self):
        token = self.get_token()

        if token.type == TokenType.COMMA:
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
            self.parse_e_2()

        return False

    def parse_o_r(self):
        token = self.get_token()

        if token.type == [
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.NOT_EQUAL,
            TokenType.EQUALS,
        ]:
            # on ajoute token à l'arbre
            self.next_token()
        return False

    def parse_o_plus(self):
        token = self.get_token()

        if token.type == TokenType.PLUS:
            # on ajoute token à l'arbre
            self.next_token()
        return False

    def parse_o_star(self):
        token = self.get_token()

        if token.type == [TokenType.MULTIPLY, TokenType.FLOOR_DIVIDE, TokenType.MODULO]:
            # on ajoute token à l'arbre
            self.next_token()
        return False

    def parse_o_un(self):
        token = self.get_token()

        if token.type == [
            TokenType.IDENTIFIER,
            TokenType.CONST,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            # on ajoute token à l'arbre
            self.next_token()
        return False
