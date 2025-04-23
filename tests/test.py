def calcul_simple():
    a = 5
    b = 10
    c = a + b
    d = a * b
    e = b // a
    f = b - a
    if c + d + e + f > 0:
        return "Result is positive"
    else:
        return "Result is negative or zero"
  
resultat = calcul_simple()
print(resultat)