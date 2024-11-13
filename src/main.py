from lexer import Lexer

def main():
    with open("../tests/source_code.txt", "r") as file:
        source_code = file.read()

    lexer = Lexer(source_code)

    while True:
        token = lexer.get_next_token()
        if token.type == "EOF":
            break
        else:
            print(token)
            
    print(lexer.identifier_lexicon)

if __name__ == "__main__":
    main()