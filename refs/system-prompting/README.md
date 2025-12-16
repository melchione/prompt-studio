# Guide de Référence : Techniques de Prompt Engineering pour LLM

## Vue d'ensemble

Ce guide présente les techniques de prompt engineering les plus avancées en 2025 pour optimiser les performances des LLM. Chaque technique est documentée avec ses avantages, inconvénients et cas d'usage appropriés.

## Navigation

1. [Stratégies de Décision de Routing](01-routing-decision-strategies.md) - Vue globale des approches de routing
2. [Chain-of-Thought (CoT) Prompting](02-chain-of-thought-prompting.md) - Raisonnement étape par étape
3. [Least-to-Most Prompting](03-least-to-most-prompting.md) - Décomposition en sous-problèmes
4. [Automatic Prompt Engineering (APE)](04-automatic-prompt-engineering.md) - Optimisation automatique
5. [EvolInstruct & Complexity Evolution](05-evolinstruct-complexity.md) - Évolution de complexité
6. [Prompt Chaining](06-prompt-chaining.md) - Chaînage séquentiel et workflows
7. [ReAct Framework](07-react-framework.md) - Synergie raisonnement et action
8. [Cognitive Flexibility](08-cognitive-flexibility.md) - Adaptation dynamique et routing intelligent
9. [Guide d'Implémentation](09-implementation-guide.md) - Mise en pratique et combinaisons

## Matrice de Décision Rapide

| Technique | Complexité | Latence | Coût | Cas d'usage principal |
|-----------|------------|---------|------|----------------------|
| **Réponse Directe** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | Questions simples, définitions |
| **CoT** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Raisonnement complexe, maths |
| **Least-to-Most** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Problèmes compositionnels |
| **APE** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | Optimisation de prompts |
| **Prompt Chaining** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Workflows multi-étapes |
| **ReAct** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | Agents autonomes |
| **Routing Dynamique** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | Optimisation coût/performance |

## Arbre de Décision

```
Début
│
├─ La tâche nécessite-t-elle un raisonnement ?
│  │
│  ├─ NON → Réponse Directe
│  │
│  └─ OUI → La tâche a-t-elle plusieurs étapes ?
│     │
│     ├─ NON → Chain-of-Thought (CoT)
│     │
│     └─ OUI → Les étapes sont-elles interdépendantes ?
│        │
│        ├─ NON → Prompt Chaining (parallèle)
│        │
│        └─ OUI → Nécessite-t-elle des actions externes ?
│           │
│           ├─ NON → Least-to-Most
│           │
│           └─ OUI → ReAct Framework
```

## Glossaire

- **Prompt Engineering** : L'art et la science de concevoir des instructions optimales pour les LLM
- **Routing** : Processus de direction des requêtes vers le modèle ou la méthode la plus appropriée
- **Charge Cognitive** : Quantité d'effort mental requis pour traiter une tâche
- **Token** : Unité de base du texte traité par un LLM
- **Few-Shot** : Technique d'apprentissage avec quelques exemples
- **Zero-Shot** : Exécution sans exemples préalables
- **Orchestration** : Coordination de multiples modèles ou agents

## Principes Fondamentaux

### 1. Simplicité d'abord
Commencez toujours par l'approche la plus simple qui pourrait fonctionner.

### 2. Mesure et itération
Mesurez les performances (latence, coût, précision) et itérez.

### 3. Combinaison de techniques
Les meilleures solutions combinent souvent plusieurs techniques.

### 4. Adaptation au contexte
Choisissez la technique en fonction du contexte spécifique de votre application.

## Métriques Clés

- **Latence** : Temps de réponse end-to-end
- **Coût** : Tokens consommés × prix par token
- **Précision** : Taux de réponses correctes/satisfaisantes
- **Robustesse** : Performance sur cas edge et inputs variés
- **Interprétabilité** : Capacité à comprendre le raisonnement

## Ressources Additionnelles

- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Papers on LLM Reasoning](https://arxiv.org/list/cs.CL/recent)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Constitutional AI](https://www.anthropic.com/constitutional.pdf)

## Contribution

Ce guide est basé sur les recherches et développements les plus récents en 2025. Pour des mises à jour ou corrections, consultez les sources originales citées dans chaque section.