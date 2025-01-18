# compile-project

## PCL 1 - Exécution & exploitation

### Afficher un arbre (abstrait ou non)

Lors de la construction d'un arbre, il peut être utile de l'afficher pour voir concrètement ce que l'on fait. Pour cela, il existe une méthode de la classe **_Tree_**, `get_flowchart`. Cette méthode prend en argument un chemin vers un fichier `.txt` pour y écrire un équivalent de l'arbre en Mermaid (un outil en JS qui permet d'afficher des diagrammes en utilisant une syntaxe particulière). Après génération, il suffit de copier l'intégralité du fichier `.txt` construit et de le coller dans l'éditeur en ligne de Mermaid (disponible [ici](mermaid.live)).

## [PROJET DE COMPILATION - Mini Python]

### Objectif du Projet

L'objectif de ce projet est de développer un compilateur pour un langage de haut niveau, appelé **Mini Python**, qui représente un fragment du langage Python. Le projet couvre toutes les étapes de compilation, y compris la conception des analyseurs lexical et syntaxique, la construction de l'arbre abstrait et sa visualisation.

### Instructions Générales

- Aucun générateur d'analyseur lexical et syntaxique ne doit être utilisé. Vous devez développer vous-même l'automate de reconnaissance des unités lexicales et l'analyseur syntaxique.
- L'analyseur syntaxique descendant doit être construit à l'aide de "fonctions récursives".
- Le langage de développement pour votre compilateur est **Python**.
- Il est nécessaire de définir complètement la grammaire du langage, la conception des analyseurs lexical et syntaxique, ainsi que la construction et la visualisation de l'arbre abstrait.

### Gestion des Erreurs

Votre compilateur doit signaler les erreurs lexicales et syntaxiques rencontrées. Chaque erreur doit être accompagnée d'un message explicite, incluant, si possible, un numéro de ligne. Le compilateur ne doit pas s'arrêter après avoir rencontré une erreur ; il doit tenter de continuer l'analyse syntaxique.

### Tests

Vous devez tester votre compilateur avec des exemples variés de programmes corrects en Mini Python, ainsi qu'avec des exemples comportant des erreurs lexicales et syntaxiques.

---

## [1 Présentation du langage : aspects lexical et syntaxique]

### [1.1 Conventions lexicales]

- Le symbole `^x` indique que le symbole `x` est en exposant, tandis que `_y` signifie qu'il est en indice. Par exemple, `<motif>^*_` signifie que `<motif>` a pour exposant le symbole `*` et pour indice le symbole `,` (virgule).
- Un commentaire débute par `#` et s'étend jusqu'à la fin de la ligne.
- Les identificateurs d'un programme sont définis par l'expression régulière suivante :  
  `<digit> ::= 0-9`  
  `<alpha> ::= a-z | A-Z`  
  `<ident> ::= (<alpha> | _) (<alpha> | _ | <digit>)^*`

- Les constantes entières sont définies par l'expression régulière suivante :  
  `<integer> ::= 0 | 1-9 <digit>^*`

### Types du Langage

Les types du langage sont les suivants :  
`{int, str}`  
_Remarque :_ Les chaînes de caractères doivent être écrites entre guillemets (symbole `"`).
_Remarque :_ Deux séquences d'échappement sont définies : `\"` pour le caractère `"` et `\n` pour le saut de ligne.

### Mots Clés

Les mots clés du langage incluent :  
`{if, else, and, or, not, True, False, None, def, return, print, for, in}`

### Opérateurs Binaires, Unaires et d'Assignation

Les opérateurs binaires du langage sont les suivants :  
`{+, -, *, //, %, <=, >=, >, <, !=, ==, and, or}`

Les opérateurs unaires du langage sont les suivants :  
`{-, not}`
_Remarque :_ L'opérateur `-` peut être soit binaire soit unaire.
_Remarque :_ Une expression comme `x < y < z` n'est pas autorisée.

L'opérateur d'assignation du langage est :
`{=}`

### Délimiteurs

Les délimiteurs du langage sont :  
`{(, ), [, ], :, ,}`

### [1.2 Syntaxe]

Pour la spécification de la grammaire, nous utiliserons les notations suivantes :

- `<motif>^*` : répétition de `<motif>` un nombre quelconque de fois ou aucune fois.
- `<motif>^*_t` : comme précédemment, mais avec des occurrences séparées par le terminal `t`.
- `<motif>^+` : répétition de `<motif>` au moins une fois.
- `<motif>^+_t` : comme précédemment, avec des occurrences séparées par le terminal `t`.
- `<motif>?` : utilisation optionnelle de `<motif>` (0 ou 1 fois).

### Associativité et Précédence des Opérateurs

Les associativités et précédences des opérateurs sont récapitulées dans le tableau suivant, allant de la plus faible à la plus forte priorité.

```
+---------------------------+--------------------+------------------+
|    Opérateur              |    Associativité   |     Priorité     |
+---------------------------+--------------------+------------------+
| or                        | gauche             | plus faible      |
| and                       | gauche             | ...              |
| not                       | - (Non applicable) | ...              |
| <, <=, >, >=, ==, !=      | - (Non applicable) | ...              |
| +, -                      | gauche             | ...              |
| *, //, %                  | gauche             | ...              |
| - (Unaire)                | - (Non applicable) | plus forte       |
+---------------------------+--------------------+------------------+
```

### Indentation et Gestion des Blocs

En Python, les structures de blocs sont définies par l'indentation. L'indentation se fait par groupes de quatre espaces. L'analyseur lexical produit trois tokens pour gérer les indentations : `NEWLINE`, `BEGIN` et `END`, qui correspondent respectivement à la fin de ligne, à l'incrémentation et à la décrémentation de l'indentation.

#### Algorithme d'Indentation

L'analyseur lexical utilise une pile d'entiers pour représenter les indentations successives, initialement contenant la valeur `0`. Lorsqu'un passage à la ligne est détecté, le token `NEWLINE` est produit. L'indentation de la nouvelle ligne, notée `n`, est comparée à la valeur au sommet de la pile, notée `m`. Les cas possibles sont :

1. Si `n = m`, aucune action n'est nécessaire.
2. Si `n > m`, empiler `n` et produire le token `BEGIN`.
3. Si `n < m`, dépiler jusqu'à trouver la valeur `n`, produisant un token `END` pour chaque valeur dépilée strictement supérieure à `n`. Si aucune valeur égale à `n` n'est trouvée, émettre le message `indentation error`.

### Grammaire du Langage Mini Python

La grammaire du langage Mini Python est définie comme suit (le symbole `|` sépare les différentes productions) :

```
<file> ::= NEWLINE? <def>^* <stmt>^+ EOF
<def> ::= def <ident> (<ident>^*_,): <suite>
<suite> ::= <simple_stmt> NEWLINE | NEWLINE BEGIN <stmt>^+ END
<simple_stmt> ::= return <expr> | <ident> = <expr> | <expr> [<expr>] = <expr> | print(<expr>) | <expr>
<stmt> ::= <simple_stmt> NEWLINE | if <expr>: <suite> | if <expr>: <suite> else: <suite> | for <ident> in <expr>: <suite>
<expr> ::= <const> | <ident> | <expr> [<expr>] | -<expr>| not <expr> | <expr> <binop> <expr> | <ident> (<expr>^*_,) | [<expr>^*_,] | (<expr>)
<binop> ::= + | - | * | // | % | <= | >= | > | < | != | == | and | or
<const> ::= <integer> | <string> | True | False | None
```
