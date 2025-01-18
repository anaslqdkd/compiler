# Définition d'une fonction pour calculer le carré d'un nombre
def square(x):
    return x * x

# Définition d'une fonction pour vérifier si un nombre est pair
def is_even(n):
    if n % 2 == 0:
        return True
    else:
        return False

# Définition d'une fonction pour trouver le maximum entre deux nombres
def max_of_two(a, b):
    if a > b:
        return a
    else:
        return b

# Utilisation des opérateurs unaires et des mots-clés logiques
def complex_logic(a, b, c):
    if not a and (b or c):
        return "Condition met"
    else:
        return "Condition not met"

# Initialisation des variables
x = 10
y = 5
z = -3

# Calculs avec des opérateurs binaires et unaires
sum_result = x + y
diff_result = x - y
product_result = x * y
division_result = x // y
mod_result = x % y
neg_z = -z  # Opérateur unaire

# Comparaisons
is_x_greater_than_y = x > y
is_x_less_than_or_equal_y = x <= y
are_x_and_y_equal = x == y
are_x_and_y_not_equal = x != y

# Affichage des résultats intermédiaires
print("Sum:", sum_result)
print("Difference:", diff_result)
print("Product:", product_result)
print("Integer Division:", division_result)
print("Modulo:", mod_result)
print("Negation of z:", neg_z)

# Affichage des résultats des comparaisons
print("Is x > y:", is_x_greater_than_y)
print("Is x <= y:", is_x_less_than_or_equal_y)
print("Are x and y equal:", are_x_and_y_equal)
print("Are x and y not equal:", are_x_and_y_not_equal)

# Utilisation de chaînes de caractères avec des séquences d'échappement
message = "Hello, \"Mini Python\"!\nThis is a test."
print(message)

# Boucle pour itérer sur une liste et afficher les carrés des nombres
numbers = [1, 2, 3, 4, 5]
for num in numbers:
    if is_even(num):
        print("Even:", num, "Square:", square(num))
    else:
        print("Odd:", num, "Square:", square(num))

# Appel de la fonction de logique complexe
logic_result = complex_logic(False, True, False)
print("Logic result:", logic_result)

# Test avec la fonction max_of_two
max_value = max_of_two(x, y)
print("Max of x and y:", max_value)

# Affichage de None pour vérifier la gestion
empty_value = None
print("Empty value:", empty_value)
