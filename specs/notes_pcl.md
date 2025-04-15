---
id: notes_pcl
aliases: []
tags: []
---

## Erreurs sémantiques
- types (mais que pour les constantes, le reste
lors de l'execution du code)
- si défini dans le bloc d'imbrication
- redeclaration
- var non declaré 
- paramètres pas assez
- index errors
- key errors, dictionnary (pas ici)
- division par zero (explicite) 
- fonction non declarée


## Ce qui a été fait

- le type de retour d'une fonction, ex si on fait a = fn(x), le type de a est le type de la variable après return dans fn
- il y la verification du type de paramètre et le nb de paramètre dans un appel de fonction

## A faire encore

- la partie que Amine a fait, à savoir autoriser les opérations True + 1 etc, pour l'instant ça donne une erreur sémantique
- il y a un parsing failed pour des fonctions sans paramètre
- return l[0] pour l'instant pris comme une liste, il y a un todo, c'est pas très compliqué
- rm identifier de list_identifier lors de la redefinition, idem pour fonction
- retour de fonction pour des trucs definis dans la table englobante
- recalculer les deplacements
- petit pb si on a a = main(x) et a est une liste et main renvoie une liste, cf le source code, mais ça j'ai mal géré la portion qui géré les appels de listes
