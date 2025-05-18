from src.lexer import *
from src.tree_struct import *


class ParsingFailedError(Exception):
    pass


# -------------------------------------------------------------------------------------------------


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
        self.success = True

    def next_token(self):
        self.current_token = self.lexer.get_next_token()

    def get_token(self):
        return self.current_token

    def peek_next_token(self):
        return self.lexer.peek_next_token()

    def parse(self):
        "Axiome"
        self.parse_s()
        if self.success:
            print("Parsing completed successfully")
        else:
            self.root.get_flowchart(file_path="tests/flowchart.txt", print_result=False)
            raise ParsingFailedError

    def parse_s(self):
        "S"
        # ajouter S à l'arbre
        non_terminal_node = Tree(data="S", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node

        token = self.get_token()
        if self.debug_mode:
            print("in parse_s")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_s_1(self):
        "S'"
        # ajouter S' à l'arbre
        non_terminal_node = Tree(data="S1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()
        if self.debug_mode:
            print("in parse_s1")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_s_2(self):
        "S''"
        # ajout S'' à l'arbre
        non_terminal_node = Tree(data="S2", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()
        if self.debug_mode:
            print("in parse_s2")
            print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] == "EOF":
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_a(self):
        "A"
        # on ajoute A à l'arbre
        non_terminal_node = Tree(data="A", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node

        token = self.get_token()
        if self.debug_mode:
            print("in parse_a")
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
        self.success = False
        self.tree = self.tree.father

        return False

    def parse_i(self):
        # on ajoute I à l'arbre
        non_terminal_node = Tree(data="I", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()
        if self.debug_mode:
            print("in parse i")
            print(TokenType.lexicon[token.number])

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
        if TokenType.lexicon[token.number] == ")":
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_i_1(self):
        "I'"
        # on ajoute I' à l'arbre
        non_terminal_node = Tree(data="I1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse i1")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_b(self):
        "B"
        # on ajoute B à l'arbre
        non_terminal_node = Tree(data="B", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse b")
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
                if TokenType.lexicon[token.number] == "END":
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
            print("In B")
            self.parse_c()
            self.parse_n()
            self.tree = self.tree.father
            return True
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in B",
            )
        )
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_b_1(self):
        "B1"
        # on ajoute B' à l'arbre
        non_terminal_node = Tree(data="B1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse b 1")
            print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "if",
            "for",
            "return",
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_c(self):
        "C"
        # on ajoute C à l'arbre
        non_terminal_node = Tree(data="C", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_c")
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
            self.parse_c_1()
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
        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in C",
            )
        )

        self.success = False
        self.tree = self.tree.father
        return False

    def parse_c_1(self):
        "C'"
        # ajouter C' à l'arbre
        non_terminal_node = Tree(data="C1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_c1")
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
            if TokenType.lexicon[peek_token.number] in [
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
            else:
                self.tree = self.tree.father
                return True

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
            # NOTE: ajout ici
            ":",
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_d(self):
        "D"
        non_terminal_node = Tree(data="D", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        # on ajoute D à l'arbre
        token = self.get_token()

        if self.debug_mode:
            print("in parse_d")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_d_1(self):
        "D1"
        # on ajoute D' à l'arbre
        non_terminal_node = Tree(data="D1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_d1")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e(self):
        "E"
        # on ajoute E à l'arbre
        non_terminal_node = Tree(data="E", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_or(self):
        "E'"
        # on ajoute E à l'arbre
        non_terminal_node = Tree(data="E_or", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_or")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_or_tail(self):
        # on ajoute E_or_tail à l'arbre
        non_terminal_node = Tree(data="E_or_tail", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_or_tail")
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
            self.tree.add_tree_child(
                Tree(
                    data=token.number,
                    line_index=token.line,
                    is_terminal=True,
                )
            )
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_and(self):
        "E''"
        # on ajoute E_and à l'arbre
        non_terminal_node = Tree(data="E_and", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_and")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_and_tail(self):
        # on ajoute e_and_tail à l'arbre
        non_terminal_node = Tree(data="E_and_tail", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_and_tail")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_not(self):
        # on ajoute e_not à l'arbre
        non_terminal_node = Tree(data="E_not", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_not")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_rel(self):
        # on ajoute e_rel à l'arbre
        non_terminal_node = Tree(data="E_rel", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_rel")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_rel_tail(self):
        # on ajoute le e_rel_tail à l'arbre
        non_terminal_node = Tree(data="E_rel_tail", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_rel_tail")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_add(self):
        # on ajoute e_add à l'arbre
        non_terminal_node = Tree(data="E_add", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_add")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_add_tail(self):
        non_terminal_node = Tree(data="E_add_tail", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_add_tail")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_mult(self):
        # on ajoute e_mult à l'arbre
        non_terminal_node = Tree(data="E_mult", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_mult")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_mult_tail(self):
        token = self.get_token()
        non_terminal_node = Tree(data="E_mult_tail", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node

        if self.debug_mode:
            print("in parse_e_mult_tail")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_un(self):
        # on ajoute e_un à l'arbre
        non_terminal_node = Tree(data="E_un", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_un")
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

        if TokenType.lexicon[token.number] == "IDENTIFIER":
            peek_token = self.peek_next_token()
            if TokenType.lexicon[peek_token.number] in ["(", "["]:
                self.tree.add_tree_child(
                    Tree(
                        data=token.number,
                        line_index=token.line,
                        is_terminal=True,
                        value=token.value,
                    )
                )
                self.next_token()
                self.parse_e_3()
                self.tree = self.tree.father
                return True
            else:
                self.parse_o_un()
                self.tree = self.tree.father
                return True
        if TokenType.lexicon[token.number] in [
            # NOTE: changement ici du à parse un -> ident (E1)
            "STRING",
            "INTEGER",
            "True",
            "False",
            "None",
            "NEWLINE",
            # NOTE: ajout perso aussi
            # "IDENTIFIER",
        ]:
            self.parse_o_un()
            self.tree = self.tree.father
            return True
        if TokenType.lexicon[token.number] == ":":
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_1(self):
        non_terminal_node = Tree(data="E1", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_1")
            print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "(",
            "IDENTIFIER",
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
            self.parse_e_2()
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
                value="Parsing failed in E_1",
            )
        )
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_2(self):
        # on ajoute e_2 à l'arbre
        non_terminal_node = Tree(data="E2", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_2")
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
            self.parse_e()
            self.parse_e_2()
            self.tree = self.tree.father
            return True
        # NOTE: ajout à enlever eventuellement
        if TokenType.lexicon[token.number] in [")", "]", ":", "NEWLINE"]:
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_e_3(self):
        non_terminal_node = Tree(data="E3", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_e_3")
            print(TokenType.lexicon[token.number])
        # FIXME: finish this
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

        self.tree.add_tree_child(
            Tree(
                data="ERROR",
                line_index=token.line,
                is_terminal=True,
                value="Parsing failed in E_1",
            )
        )
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_o_r(self):
        # on ajoute o_r à l'arbre
        non_terminal_node = Tree(data="O_r", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_o_r")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_o_plus(self):
        # on ajoute o_plus à l'arbre
        non_terminal_node = Tree(data="O_plus", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_o_plus")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_o_star(self):
        # on ajoute o_star à l'arbre
        non_terminal_node = Tree(data="O_star", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_o_star")
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_o_un(self):
        # on ajoute o_un à l'arbre
        non_terminal_node = Tree(data="O_un", line_index=-1, is_terminal=False)
        self.tree.add_tree_child(non_terminal_node)
        self.tree = non_terminal_node
        token = self.get_token()

        if self.debug_mode:
            print("in parse_o_un")
            print(TokenType.lexicon[token.number])

        if TokenType.lexicon[token.number] in [
            "IDENTIFIER",
            "STRING",
            "INTEGER",
            "False",
            "None",
            "True",
            "NEWLINE",
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
        self.success = False
        self.tree = self.tree.father
        return False

    def parse_n(self):
        # on ajoute n à l'arbre
        token = self.get_token()

        if self.debug_mode:
            print("in parse n")
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
            # NOTE: ajout ici
            ":",
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
        self.success = False
        self.tree = self.tree.father
        return False
