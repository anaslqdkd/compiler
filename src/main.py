from lexer import *

def main():
    with open("../tests/source_code.txt", "r") as file:
        source_code = file.read()

    lexer = Lexer(source_code)

    while True:
        token = lexer.get_next_token()
        
        if token.type in TokenType.TOKEN_NUMBERS["VALUE"]:
            print((token.token_number, token.value))
            # print((token.token_number, token.value, token.line_number))
        else:
            print((token.token_number))
            # print((token.token_number, token.line_number))
            
        if token.type == "EOF":
            break
    
                
    print("\nIdentifier Lexicon:\n", lexer.identifier_lexicon)
    print("Constant Lexicon:\n", lexer.constant_lexicon)
    
    print("\nTest Lookahead:")
    lexer = Lexer(source_code)
    token1 = lexer.get_next_token()
    token2 = lexer.peek_next_token()
    token3 = lexer.get_next_token()
    
    print("Token 1:", token1)
    print("Token 2 (peek):", token2)
    print("Token 3:", token3)

if __name__ == "__main__":
    main()