from lexer import *


# TODO: à voir pour les constantes, conflit grammaire et impl,
# et reverifier les tokens, notamment les == et = dus aux erreurs de remplacement


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
        if TokenType.lexicon[token.number] == "NEWLINE":
            # ajouter token à l'arbre
            self.next_token()
            return self.parse_s_1()

        if TokenType.lexicon[token.number] in [
            "def",
            "[",
            "IDENTIFIER",
            "return",
            "(",
            "print",
            "if",
            "for",
            "True",
            "False",
            "None",
            "-",
            "not",
            TokenType.CONST,
        ]:

            return self.parse_s_1()
        return False

    def parse_s_1(self):
        "S'"
        # ajouter S' à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] == "def":
            # ajouter token à l'arbre
            self.parse_a()
            self.parse_s_1()
        if TokenType.lexicon[token.number] in [
            "[",
            "IDENTIFIER",
            "(",
            "return",
            "print",
            "if",
            "for",
            "True",
            "False",
            "None",
            "-",
            "not",
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

        if TokenType.lexicon[token.number] == "EOF":
            # ajout token à l'arbre
            # on renvoie l'arbre
            return True

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "[",
            "(",
            "return",
            "print",
            "if",
            "for",
            "True",
            "False",
            "None",
            "-",
            "not",
            TokenType.CONST,
        ]:
            self.parse_d()
            self.parse_s_2()
        return False

    def parse_a(self):
        "A"
        # on ajoute A à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] == "def":
            # on ajoute token à l'arbre
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "IDENTIFIER":
                # on ajoute token à l'arbre
                self.next_token()
                token = self.get_token()
                if TokenType.lexicon[token.number] == "(":
                    # on ajoute token à l'arbre
                    self.parse_i()
                    token = self.get_token()
                    if TokenType.lexicon[token.number] == ")":
                        # on ajoute token à l'arbre
                        self.next_token()
                        token = self.get_token()
                        if TokenType.lexicon[token.number] == ":":
                            # on ajoute token à l'arbre
                            self.next_token()
                            self.parse_b()

        return False

    def parse_i(self):
        # on ajoute I à l'arbre
        "I"
        token = self.get_token()
        if TokenType.lexicon[token.number] == "IDENTIFIER":
            # on ajoute le token à l'arbre
            self.next_token()
            self.parse_i_1()
        return False

    def parse_i_1(self):
        "I'"
        # on ajoute I' à l'arbre
        token = self.get_token()
        if TokenType.lexicon[token.number] == ",":
            # on ajoute token à l'arbre
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "IDENTIFIER":
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_i_1()
        if TokenType.lexicon[token.number] == ")":
            pass
        return False

    def parse_b(self):
        "B"
        # on ajoute B à l'arbre
        token = self.get_token()
        if TokenType.lexicon[token.number] == "NEWLINE":
            # on ajoute token à l'arbre
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "BEGIN":
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_d()
                self.parse_b_1()
                token = self.get_token()
                if TokenType.lexicon[token.number] == "END":
                    # on ajoute token à l'arbre
                    self.next_token()

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "return",
            "print",
            "True",
            "False",
            "None",
            "-",
            "not",
            TokenType.CONST,
        ]:
            self.parse_c()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "NEWLINE":
                # on ajoute token à l'arbre
                self.next_token()
        return False

        #

    def parse_b_1(self):
        "B1"
        # on ajoute B' à l'arbre
        token = self.get_token()
        if TokenType.lexicon[token.number] == "NEWLINE":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_d()
            self.parse_b_1()
        if TokenType.lexicon[token.number] == "END":
            pass
        return False

    def parse_c(self):
        "C"
        # on ajoute C à l'arbre
        token = self.get_token()
        if TokenType.lexicon[token.number] == "return":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
        if TokenType.lexicon[token.number] == "IDENTIFIER":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_c_2()
        if TokenType.lexicon[token.number] == "print":
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "(":
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_e()
                self.parse_c_1()
                token = self.get_token()
                if TokenType.lexicon[token.number] == ")":
                    # on ajoute token à l'arbre
                    self.next_token()

        if TokenType.lexicon[token.number] in [
            "(",
            "[",
            "True",
            "False",
            "None",
            "-",
            "not",
            TokenType.CONST,
        ]:
            self.parse_e()
            self.parse_c_1()
        if TokenType.lexicon[token.number] == "IDENTIFIER":
            snd_token = self.peek_next_token()
            if TokenType.lexicon[snd_token.number] in [
                "NEWLINE",
                "(",
                "==",
            ]:
                self.next_token()
                self.parse_c_2()
            if TokenType.lexicon[snd_token.number] in [
                "IDENTIFIER",
                "(",
                "[",
                "not",
                "-",
                TokenType.CONST,
                "True",
                "False",
                "None",
            ]:
                self.parse_e()
                self.parse_c_1()

        return False

    def parse_c_1(self):
        "C'"
        # ajouter C' à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] == "[":
            # on ajouter token à l'arbre
            self.next_token()
            # self.parse_e()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "]":
                # on ajoute token à l'arbre
                self.next_token()
                token = self.get_token()
                if TokenType.lexicon[token.number] == "==":
                    # on ajoute token à l'arbre
                    self.next_token()
                    self.parse_e()
        if TokenType.lexicon[token.number] == "NEWLINE":
            pass
        return False

    def parse_c_2(self):
        "C''"
        # on ajoute C'' à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] == "==":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
        if TokenType.lexicon[token.number] == "(":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_1()
            token = self.get_token()
            if TokenType.lexicon[token.number] == ")":
                # on ajoute token à l'arbre
                self.next_token()

        if TokenType.lexicon[token.number] == "NEWLINE":
            pass
        return False

    def parse_d(self):
        "D"
        # on ajoute D à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] == "if":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
            token = self.get_token()
            if TokenType.lexicon[token.number] == ":":
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_b()
                self.parse_d_1()
        if TokenType.lexicon[token.number] == "for":
            # on ajoute token à l'arbre
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "IDENTIFIER":
                # on ajoute token à) l'arbre
                self.next_token()
                token = self.get_token()
                if TokenType.lexicon[token.number] == "in":
                    # on ajoute token à l'arbre
                    self.next_token()
                    self.parse_e()
                    token = self.get_token()
                    if TokenType.lexicon[token.number] == ":":
                        # on ajoute token à l'arbre
                        self.next_token()
                        self.parse_b()

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "return",
            "print",
            "True",
            "False",
            "None",
            "-",
            "not",
            "INTEGER",
            TokenType.CONST,
        ]:
            self.parse_c()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "NEWLINE":
                # on ajoute token à l'arbre
                self.next_token()
        return False

    def parse_d_1(self):
        "D1"
        # on ajoute D' à l'arbre

        token = self.get_token()
        if TokenType.lexicon[token.number] == "else":
            # on ajoute token à l'arbre
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == ":":
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_b()
        if TokenType.lexicon[token.number] in [
            "EOF",
            "NEWLINE",
            "END",
            "IDENTIFIER",
            "(",
            "[",
            "return",
            "print",
            "if",
            "for",
            "True",
            "False",
            "None",
            "-",
            "not",
            "INTEGER",
            TokenType.CONST,
        ]:
            pass
        return False

    def parse_e(self):
        "E"
        # on ajoute E à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            TokenType.CONST,
            "(",
            "[",
            "not",
            "-",
            "True",
            "False",
            "None",
        ]:
            self.parse_e_or()

    def parse_e_or(self):
        "E'"
        # on ajoute E à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "not",
            "-",
            TokenType.CONST,
            "True",
            "False",
            "None",
        ]:
            self.parse_e_and()
            self.parse_e_or_tail()

    def parse_e_or_tail(self):
        # on ajoute E_or_tail à l'arbre

        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            "(",
            ":",
            ",",
            "[",
            "]",
        ]:
            pass
        if TokenType.lexicon[token.number] == "or":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_and()
            self.parse_e_or_tail()
        return False

    def parse_e_and(self):
        "E''"
        # on ajoute E_and à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "not",
            "-",
            TokenType.CONST,
            "True",
            "False",
            "None",
        ]:
            self.parse_e_not()
            self.parse_e_and_tail()
        return False

    def parse_e_and_tail(self):
        # on ajoute e_and_tail à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            ")",
            ":",
            ",",
            "[",
            "or",
        ]:
            pass
        if TokenType.lexicon[token.number] == "and":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_not()
            self.parse_e_and_tail()
        return False

    def parse_e_not(self):
        # on ajoute e_not à l'arbre

        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "-",
            TokenType.CONST,
            "True",
            "False",
            "None",
        ]:
            self.parse_e_rel()
        if TokenType.lexicon[token.number] == "not":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_rel()
        return False

    def parse_e_rel(self):
        # on ajoute e_rel à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "-",
            TokenType.CONST,
            "True",
            "False",
            "None",
        ]:
            self.parse_e_add()
            self.parse_e_rel_tail()
        return False

    def parse_e_rel_tail(self):
        # on ajoute le e_rel_tail à l'arbre
        token = self.get_token()
        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            ")",
            ":",
            ",",
            "[",
            "]",
            "or",
            "and",
        ]:
            pass
        if TokenType.lexicon[token.number] in [
            ">=",
            "<=",
            ">",
            "<",
            "==",
            "!=",
        ]:
            self.parse_o_r()
            self.parse_e_add()
            self.parse_e_rel_tail()
        return False

    def parse_e_add(self):
        # on ajoute e_add à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "-",
            TokenType.CONST,
            "True",
            "False",
            "None",
        ]:
            self.parse_e_mult()
            self.parse_e_add_tail()
        return False

    def parse_e_add_tail(self):
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            ")",
            ":",
            ",",
            "[",
            "]",
            "or",
            "and",
            ">=",
            "<=",
            ">",
            "<",
            "!=",
            "==",
        ]:
            pass
        if TokenType.lexicon[token.number] == "+":
            self.parse_o_plus()
            self.parse_e_mult()
            self.parse_e_add_tail()
        return False

    def parse_e_mult(self):
        # on ajoute e_mult à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "-",
            TokenType.CONST,
            "True",
            "False",
            "None",
        ]:
            self.parse_e_un()
            self.parse_e_mult_tail()
        return False

    def parse_e_mult_tail(self):
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            ")",
            ":",
            ",",
            "[",
            "]",
            "or",
            "and",
            "<=",
            ">=",
            "<",
            ">",
            "!=",
            "==",
            "+",
        ]:
            pass

        if TokenType.lexicon[token.number] in [
            "*",
            "//",
            "%",
        ]:
            self.parse_o_star()
            self.parse_e_un()
            self.parse_e_mult_tail()
        return False

    def parse_e_un(self):
        # on ajoute e_un à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] == "(":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
            token = self.get_token()
            if TokenType.lexicon[token.number] == ")":
                # on ajoute token à l'arbre
                self.next_token()
        if TokenType.lexicon[token.number] == "[":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "]":
                # on ajoute token à l'arbre
                self.next_token()
        if TokenType.lexicon[token.number] == "-":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_un()

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            TokenType.CONST,
            "True",
            "False",
            "None",
        ]:
            self.parse_o_un()
        return False

    def parse_e_1(self):
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "(",
            "IDENTIFIER",
            "[",
            "not",
            "-",
            TokenType.CONST,
            "True",
            "False",
            "None",
        ]:
            self.parse_e()
            self.parse_e_2()
        return False

    def parse_e_2(self):
        # on ajoute e_2 à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] == ",":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e()
            self.parse_e_2()

        return False

    def parse_o_r(self):
        # on ajoute o_r à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] in [
            "<=",
            ">=",
            "<",
            ">",
            "!=",
            "==",
        ]:
            # on ajoute token à l'arbre
            self.next_token()
        return False

    def parse_o_plus(self):
        # on ajoute o_plus à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] == "+":
            # on ajoute token à l'arbre
            self.next_token()
        return False

    def parse_o_star(self):
        # on ajoute o_star à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] == [
            "*",
            "//",
            "%",
        ]:
            # on ajoute token à l'arbre
            self.next_token()
        return False

    def parse_o_un(self):
        # on ajoute o_un à l'arbre
        token = self.get_token()

        if TokenType.lexicon[token.number] == [
            "IDENTIFIER",
            TokenType.CONST,
            "False",
            "None",
        ]:
            # on ajoute token à l'arbre
            self.next_token()
        return False
