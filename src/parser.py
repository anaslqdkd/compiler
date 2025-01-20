from lexer import *
from tree_struct import *


with open("../tests/source_code.txt", "r") as file:
    source_code = file.read()

lexer = Lexer(source_code)


class Parser:
    "Parser class"

    def __init__(self, lexer, debug_mode):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.tree = Tree(
            data="axiome", line_index=self.current_token.line, is_terminal=False
        )
        self.root = self.tree
        self.debug_mode = debug_mode

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
        print(f"Before parsing S, current tree: {self.tree}")
        if self.debug_mode:
            print("in parse_s")
        non_terminal_node = Tree(data="S", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node

        token = self.get_token()
        print(TokenType.lexicon[token.number])
        if TokenType.lexicon[token.number] == "NEWLINE":

            token_node = Tree(
                data=token.number, line_index=token.line, is_terminal=True
            )
            self.tree.add_tree_child(token_node)
            self.next_token()
            self.parse_s_1()
            self.tree = self.tree.father
            return True
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
            "STRING",
            "INTEGER",
        ]:

            self.parse_s_1()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in S",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_s_1(self):
        "S'"
        if self.debug_mode:
            print("in parse_s1")
        # ajouter S' à l'arbre
        non_terminal_node = Tree(data="S1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()
        print(TokenType.lexicon[token.number])
        if TokenType.lexicon[token.number] == "EOF":
            self.tree = self.tree.father
            return True

        if TokenType.lexicon[token.number] == "def":
            self.parse_a()
            self.parse_s_1()
            self.tree = self.tree.father
            return True
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
            # TokenType.CONST,
            "STRING",
            "INTEGER",
        ]:
            self.parse_d()
            self.parse_s_1()
            self.tree = self.tree.father
            return True

        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in S1",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_s_2(self):
        "S''"
        # ajout S'' à l'arbre
        if self.debug_mode:
            print("in parse_s2")
        non_terminal_node = Tree(data="S2", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] == "EOF":
            # NOTE: here
            # ajout token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            # on renvoie l'arbre
            self.tree = self.tree.father
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
            # TokenType.CONST,
            "STRING",
            "INTEGER",
        ]:
            self.parse_d()
            self.parse_s_2()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in S2",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_a(self):
        "A"
        # on ajoute A à l'arbre
        if self.debug_mode:
            print("in parse_a")
        non_terminal_node = Tree(data="A", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node

        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] == "def":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "IDENTIFIER":
                # on ajoute token à l'arbre
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                        value=token.value,
                    )
                )
                self.next_token()
                token = self.get_token()
                if TokenType.lexicon[token.number] == "(":
                    # on ajoute token à l'arbre
                    self.tree.add_tree_child(
                        Tree(
                            data=token.number,
                            line_index=token.line,
                            is_terminal=True,
                        )
                    )
                    self.next_token()
                    self.parse_i()
                    token = self.get_token()
                    if TokenType.lexicon[token.number] == ")":
                        # on ajoute token à l'arbre
                        self.tree.add_tree_child(
                            Tree(
                                data=token.number,
                                line_index=token.line,
                                is_terminal=True,
                            )
                        )
                        self.next_token()
                        token = self.get_token()
                        if TokenType.lexicon[token.number] == ":":
                            # on ajoute token à l'arbre
                            self.tree.add_tree_child(
                                Tree(
                                    data=token.number,
                                    line_index=token.line,
                                    is_terminal=True,
                                )
                            )
                            self.next_token()
                            self.parse_b()
                            self.tree = self.tree.father
                            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in A",
            )
        )
        self.tree = self.tree.father

        return False

    def parse_i(self):
        # on ajoute I à l'arbre
        non_terminal_node = Tree(data="I", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()
        print(TokenType.lexicon[token.number])
        if self.debug_mode:
            print("in parse i")
        if TokenType.lexicon[token.number] == "IDENTIFIER":
            # on ajoute le token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                    value=token.value,
                )
            )
            self.next_token()
            self.parse_i_1()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in I",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_i_1(self):
        "I'"
        # on ajoute I' à l'arbre
        non_terminal_node = Tree(data="I1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse i1")
        token = self.get_token()
        print("in parse i1 with token type" + TokenType.lexicon[token.number])
        if TokenType.lexicon[token.number] == ",":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "IDENTIFIER":
                # on ajoute token à l'arbre
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                        value=token.value,
                    )
                )
                self.next_token()
                self.parse_i_1()
                self.tree = self.tree.father
                return True
        if TokenType.lexicon[token.number] == ")":
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in I1",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_b(self):
        "B"
        # on ajoute B à l'arbre
        non_terminal_node = Tree(data="B", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse b")
        token = self.get_token()
        print(TokenType.lexicon[token.number])
        if TokenType.lexicon[token.number] == "NEWLINE":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "BEGIN":
                # on ajoute token à l'arbre
                print("µµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµ*")
                print(TokenType.lexicon[token.number])
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                    )
                )
                self.next_token()
                self.parse_d()
                self.parse_b_1()
                token = self.get_token()
                print("(((((((((((((((((())))))))))))))))))")
                print(TokenType.lexicon[token.number])
                if TokenType.lexicon[token.number] == "END":
                    # on ajoute token à l'arbre
                    print("£££££££££££££££££££££££££££££")
                    print(TokenType.lexicon[token.number])
                    self.tree.add_tree_child(
                        Tree(
                            data=token.number,
                            line_index=token.line,
                            is_terminal=True,
                        )
                    )
                    self.next_token()
                    self.tree = self.tree.father
                    return True

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
            "STRING",
            "INTEGER",
        ]:
            self.parse_c()
            self.parse_n()
            self.tree = self.tree.father
            return True
        print("<<<<<<<<<<<<<<<<<<<<<<<<<")
        # print(TokenType.lexicon[token.value])
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in B",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_b_1(self):
        "B1"
        # on ajoute B' à l'arbre
        non_terminal_node = Tree(data="B1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse b 1")
        token = self.get_token()
        print(TokenType.lexicon[token.number])
        if TokenType.lexicon[token.number] == "NEWLINE":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.parse_d()
            self.parse_b_1()
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] == "END":
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in B1",
            )
        )
        print("####################")
        # print(TokenType.lexicon[token.value])
        self.tree = self.tree.father
        return False

    def parse_c(self):
        "C"
        # on ajoute C à l'arbre
        non_terminal_node = Tree(data="C", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_c")
        token = self.get_token()
        print(TokenType.lexicon[token.number])
        if TokenType.lexicon[token.number] == "return":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.parse_e()
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] == "IDENTIFIER":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                    value=token.value,
                )
            )
            self.next_token()
            self.parse_c_2()
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] == "print":
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "(":
                # on ajoute token à l'arbre
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                    )
                )
                self.next_token()
                # NOTE: changé ici de e à e1
                self.parse_e_1()
                # self.parse_c_1()
                token = self.get_token()
                if TokenType.lexicon[token.number] == ")":
                    # on ajoute token à l'arbre
                    self.tree.add_tree_child(
                        Tree(
                            data=token.number,
                            line_index=token.line,
                            is_terminal=True,
                        )
                    )
                    self.next_token()
                    self.tree = self.tree.father
                    return True

        if TokenType.lexicon[token.number] in [
            "(",
            "[",
            "True",
            "False",
            "None",
            "-",
            "not",
            "STRING",
            "INTEGER",
        ]:
            self.parse_e()
            self.parse_c_1()
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] == "IDENTIFIER":
            snd_token = self.peek_next_token()
            if TokenType.lexicon[snd_token.number] in [
                "NEWLINE",
                "(",
                "==",
            ]:
                self.next_token()
                self.parse_c_2()
                self.tree = self.tree.father
                return True
            if TokenType.lexicon[snd_token.number] in [
                "IDENTIFIER",
                "(",
                "[",
                "not",
                "-",
                "STRING",
                "INTEGER",
                "True",
                "False",
                "None",
            ]:
                self.parse_e()
                self.parse_c_1()
                self.tree = self.tree.father
                return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in C",
            )
        )

        self.tree = self.tree.father
        return False

    def parse_c_1(self):
        "C'"
        if self.debug_mode:
            print("in parse_c1")
        # ajouter C' à l'arbre
        non_terminal_node = Tree(data="C1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] == "[":
            # on ajouter token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )

            peek_token = self.peek_next_token()
            if TokenType.lexicon[peek_token] in [
                "IDENTIFIER",
                "(",
                "[",
                "not",
                "-",
                "STRING",
                "INTEGER",
                "True",
                "False",
                "None",
            ]:
                self.next_token()
                self.parse_e()
                token = self.get_token()
                if TokenType.lexicon[token.number] == "]":
                    # on ajoute token à l'arbre
                    self.tree.add_tree_child(
                        Tree(
                            data=token.number,
                            line_index=token.line,
                            is_terminal=True,
                        )
                    )
                    self.next_token()
                    token = self.get_token()
                    if TokenType.lexicon[token.number] == "==":
                        # on ajoute token à l'arbre
                        self.tree.add_tree_child(
                            Tree(
                                data=token.number,
                                line_index=token.line,
                                is_terminal=True,
                            )
                        )
                        self.next_token()
                        self.parse_e()
                        self.tree = self.tree.father
                        return True
            else:
                self.tree = self.tree.father
                return True
        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            "EOF",
            "def",
            "IDENTIFIER",
            "(",
            "END",
            "return",
            "if",
            "for",
            "else",
            "not",
            "-",
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in C1",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_c_2(self):
        "C''"
        if self.debug_mode:
            print("in parse_c2")
        non_terminal_node = Tree(data="C2", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        # on ajoute C'' à l'arbre
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] == "=":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.parse_e()
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] == "(":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.parse_e_1()
            token = self.get_token()
            if TokenType.lexicon[token.number] == ")":
                # on ajoute token à l'arbre
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                    )
                )
                self.next_token()
                self.tree = self.tree.father
                return True

        if TokenType.lexicon[token.number] == "NEWLINE":
            self.tree = self.tree.father
            return True

        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in C2",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_d(self):
        "D"
        if self.debug_mode:
            print("in parse_d")
        non_terminal_node = Tree(data="D", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        # on ajoute D à l'arbre
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] == "if":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.parse_e()
            token = self.get_token()
            if TokenType.lexicon[token.number] == ":":
                # on ajoute token à l'arbre
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                    )
                )
                self.next_token()
                self.parse_b()
                self.parse_d_1()
                self.tree = self.tree.father
                return True
        if TokenType.lexicon[token.number] == "for":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "IDENTIFIER":
                # on ajoute token à) l'arbre
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                        value=token.value,
                    )
                )
                self.next_token()
                token = self.get_token()
                if TokenType.lexicon[token.number] == "in":
                    # on ajoute token à l'arbre
                    self.tree.add_tree_child(
                        Tree(
                            data=token.number,
                            line_index=token.line,
                            is_terminal=True,
                        )
                    )
                    self.next_token()
                    self.parse_e()
                    token = self.get_token()
                    print(TokenType.lexicon[token.number])
                    if TokenType.lexicon[token.number] == ":":
                        self.tree.add_tree_child(
                            Tree(
                                data=token.number,
                                line_index=token.line,
                                is_terminal=True,
                            )
                        )
                        # on ajoute token à l'arbre
                        self.next_token()
                        self.parse_b()
                        self.tree = self.tree.father
                        return True

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
            "STRING",
            "INTEGER",
        ]:
            self.parse_c()
            self.parse_n()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in D",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_d_1(self):
        "D1"
        # on ajoute D' à l'arbre
        non_terminal_node = Tree(data="D1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_d1")

        token = self.get_token()
        print(TokenType.lexicon[token.number])
        if TokenType.lexicon[token.number] == "else":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            token = self.get_token()
            if TokenType.lexicon[token.number] == ":":
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                    )
                )
                # on ajoute token à l'arbre
                self.next_token()
                self.parse_b()
                self.tree = self.tree.father
                return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in D1",
            )
        )
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
            "STRING",
            "INTEGER",
        ]:
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in D1",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e(self):
        "E"
        # on ajoute E à l'arbre
        non_terminal_node = Tree(data="E", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "STRING",
            "INTEGER",
            "(",
            "[",
            "not",
            "-",
            "True",
            "False",
            "None",
        ]:
            self.parse_e_or()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_or(self):
        "E'"
        # on ajoute E à l'arbre
        non_terminal_node = Tree(data="E_or", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_or")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "not",
            "-",
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.parse_e_and()
            self.parse_e_or_tail()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_or",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_or_tail(self):
        # on ajoute E_or_tail à l'arbre
        non_terminal_node = Tree(
            data="E_or_tail", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_or_tail")

        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            "(",
            ":",
            ",",
            "[",
            "]",
            "STRING",
            "EOF",
            "def",
            "IDENTIFIER",
            ")",
            "END",
            "return",
            "print",
            "if",
            "for",
            "else",
            "and",
            "not",
            "-",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] == "or":
            # on ajoute token à l'arbre
            self.next_token()
            self.parse_e_and()
            self.parse_e_or_tail()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_or_tail",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_and(self):
        "E''"
        # on ajoute E_and à l'arbre
        non_terminal_node = Tree(
            data="E_and", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_and")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            "(",
            ":",
            ",",
            "[",
            "]",
            "STRING",
            "EOF",
            "def",
            "IDENTIFIER",
            "(",
            "END",
            "return",
            "print",
            "if",
            "for",
            "else",
            "not",
            "-",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.parse_e_not()
            self.parse_e_and_tail()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_and",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_and_tail(self):
        # on ajoute e_and_tail à l'arbre
        non_terminal_node = Tree(
            data="E_and_tail", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_and_tail")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            ":",
            ",",
            "[",
            "]",
            "or",
            "EOF",
            "def",
            "IDENTIFIER",
            "(",
            ")",
            ":",
            ",",
            "END",
            "return",
            "print",
            "[",
            "if",
            "else",
            "or",
            "for",
            "not",
            "-",
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] == "and":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.parse_e_not()
            self.parse_e_and_tail()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_and_tail",
            )
        )
        print(token.number)
        print(token.value)
        self.tree = self.tree.father
        return False

    def parse_e_not(self):
        # on ajoute e_not à l'arbre
        non_terminal_node = Tree(
            data="E_not", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_not")

        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "-",
            # TokenType.CONST,
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.parse_e_rel()
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] == "not":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.parse_e_rel()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_not",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_rel(self):
        # on ajoute e_rel à l'arbre
        non_terminal_node = Tree(
            data="E_rel", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_rel")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "-",
            # TokenType.CONST,
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.parse_e_add()
            self.parse_e_rel_tail()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_rel",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_rel_tail(self):
        # on ajoute le e_rel_tail à l'arbre
        non_terminal_node = Tree(
            data="E_rel_tail", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_rel_tail")
        token = self.get_token()
        print(TokenType.lexicon[token.number])
        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            "(",
            ":",
            ",",
            "[",
            "]",
            "STRING",
            "EOF",
            "def",
            "IDENTIFIER",
            ")",
            "END",
            "return",
            "print",
            "if",
            "for",
            "or",
            "else",
            "not",
            "and",
            "-",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.tree = self.tree.father
            return True
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
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_rel_tail",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_add(self):
        # on ajoute e_add à l'arbre
        non_terminal_node = Tree(
            data="E_add", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_add")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "-",
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.parse_e_mult()
            self.parse_e_add_tail()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_add",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_add_tail(self):
        if self.debug_mode:
            print("in parse_e_add_tail")
        non_terminal_node = Tree(
            data="E_add_tail", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "NEWLINE",
            "(",
            ":",
            ",",
            "[",
            "]",
            "STRING",
            "EOF",
            "def",
            "IDENTIFIER",
            ")",
            "END",
            "return",
            "print",
            "if",
            "for",
            "else",
            "not",
            "INTEGER",
            "and",
            "or",
            "True",
            "False",
            "None",
            ">=",
            "<=",
            ">",
            "<",
            "!=",
            "==",
        ]:
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] in ["+", "-"]:
            self.parse_o_plus()
            self.parse_e_mult()
            self.parse_e_add_tail()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_add_tail",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_mult(self):
        # on ajoute e_mult à l'arbre
        non_terminal_node = Tree(
            data="E_mult", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_mult")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "(",
            "[",
            "-",
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            # NOTE: here
            self.parse_e_un()
            self.parse_e_mult_tail()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_mult",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_mult_tail(self):
        if self.debug_mode:
            print("in parse_e_mult_tail")
        token = self.get_token()
        non_terminal_node = Tree(
            data="E_mult_tail", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "STRING",
            "EOF",
            "def",
            "IDENTIFIER",
            "(",
            "END",
            "return",
            "print",
            "if",
            "for",
            "else",
            "and",
            "or",
            "not",
            "-",
            "INTEGER",
            "True",
            "False",
            "None",
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
            print("1111111111111")
            print(TokenType.lexicon[token.number])
            self.tree = self.tree.father
            return True

        if TokenType.lexicon[token.number] in [
            "*",
            "//",
            "%",
        ]:
            self.parse_o_star()
            self.parse_e_un()
            self.parse_e_mult_tail()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_mult_tail",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_un(self):
        # on ajoute e_un à l'arbre
        non_terminal_node = Tree(data="E_un", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_un")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] == "(":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.parse_e_1()

            token = self.get_token()

            if TokenType.lexicon[token.number] == ")":
                # on ajoute token à l'arbre
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                    )
                )
                self.next_token()
                self.tree = self.tree.father
                return True
        if TokenType.lexicon[token.number] == "[":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            # NOTE: modif ici au lieu de parse_e je fais parse_e_1
            self.parse_e_1()
            token = self.get_token()
            if TokenType.lexicon[token.number] == "]":
                # on ajoute token à l'arbre
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                    )
                )
                self.next_token()
                self.tree = self.tree.father
                return True
        if TokenType.lexicon[token.number] == "-":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.parse_e_un()
            self.tree = self.tree.father
            return True

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            # TokenType.CONST,
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.parse_o_un()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_un",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_1(self):
        if self.debug_mode:
            print("in parse_e_1")
        non_terminal_node = Tree(data="E1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "(",
            "IDENTIFIER",
            "[",
            "not",
            "-",
            # TokenType.CONST,
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.parse_e()
            self.parse_e_2()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_1",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_e_2(self):
        # on ajoute e_2 à l'arbre
        non_terminal_node = Tree(data="E2", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_e_2")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] == ",":
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            print("""222222222222222222222""")
            print(TokenType.lexicon[token.number])
            self.parse_e()
            self.parse_e_2()
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] in [")", "]"]:
            self.tree = self.tree.father
            return True

        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_2",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_o_r(self):
        # on ajoute o_r à l'arbre
        non_terminal_node = Tree(data="O_r", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_o_r")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "<=",
            ">=",
            "<",
            ">",
            "!=",
            "==",
        ]:
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in O_r",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_o_plus(self):
        # on ajoute o_plus à l'arbre
        non_terminal_node = Tree(
            data="O_plus", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_o_plus")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in ["+", "-"]:
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in O_plus",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_o_star(self):
        # on ajoute o_star à l'arbre
        non_terminal_node = Tree(
            data="O_star", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_o_star")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "*",
            "//",
            "%",
        ]:
            # on ajoute token à l'arbre
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
            self.next_token()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in O_star",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_o_un(self):
        # on ajoute o_un à l'arbre
        non_terminal_node = Tree(data="O_un", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if self.debug_mode:
            print("in parse_o_un")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            # TokenType.CONST,
            "STRING",
            "INTEGER",
            "False",
            "None",
            "True",
        ]:
            # on ajoute token à l'arbre
            if token.value is not None:
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                        value=token.value,
                    )
                )
            else:
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                    )
                )

            self.next_token()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in O_un",
            )
        )
        self.tree = self.tree.father
        return False

    def parse_n(self):
        # on ajoute n à l'arbre
        if self.debug_mode:
            print("in parse n")
        token = self.get_token()
        print(TokenType.lexicon[token.number])

        non_terminal_node = Tree(data="N", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        if TokenType.lexicon[token.number] == "NEWLINE":
            token_node = Tree(
                data=token.number,
                line_index=token.line,
                is_terminal=True,
            )
            self.tree.add_tree_child(token_node)
            self.next_token()
            self.parse_n()
            self.tree = self.tree.father
            return True

        if TokenType.lexicon[token.number] in [
            "EOF",
            "def",
            "IDENTIFIER",
            "(",
            "END",
            "return",
            "print",
            "[",
            "if",
            "for",
            "not",
            "-",
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
        ]:
            self.tree = self.tree.father
            return True

        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in N",
            )
        )
        self.tree = self.tree.father
        return False
