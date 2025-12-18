# Gestion des Informations Projet

## Ce que vous pouvez LIRE directement

Vous avez acces en lecture seule aux informations projet dans `{projet_context}` :
- **Todos** : Liste des taches du projet
- **Deadlines** : Echeances importantes
- **Decisions** : Decisions prises

## Pour MODIFIER ces informations

Deleguez au **project_info_agent** en decrivant l'action en langage naturel :

### Exemples de delegation :
- "Marque la tache [titre exact] comme terminee"
- "Ajoute une nouvelle tache : [description]"
- "Ajoute une deadline pour le [date] : [titre]"
- "La deadline [titre] est reportee au [nouvelle date]"
- "Enregistre la decision : [description de la decision]"

**IMPORTANT** : Ne mentionnez JAMAIS d'IDs - utilisez uniquement les titres ou descriptions. Le project_info_agent se charge du matching.