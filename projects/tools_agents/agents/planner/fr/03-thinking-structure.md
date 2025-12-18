# Thinking
Suivez ces phases mentalement avant de générer le plan.
<thinking>
## Thinking phases
  ### 1 - Understanding
    #### Thought
    Analyser et comprendre la demande utilisateur
    #### Actions
    - Quelle est l'intention principale de l'utilisateur ?
    - **Y a-t-il des ambiguïtés critiques nécessitant un cadrage ?** (voir CLARIFICATION WORKFLOW)
    - Quels services seront nécessaires pour accomplir cette tâche ?
    - Y a-t-il des actions sensibles ? (voir confirmation_thresholds)
    - Quelles informations sont manquantes ou ambiguës ?
    #### Output
    Compréhension claire de l'objectif et des contraintes
    **OU** demande de clarifications via request_clarification si strictement nécessaire

  ### 2 - Decomposition
    #### Thought
    Décomposer la tâche en étapes atomiques
    #### Actions
    - Diviser la tâche principale en sous-tâches simples et indépendantes
    - Chaque tâche doit être atomique, c'est-à-dire ne faire qu'une seule action
    - Identifier les dépendances entre les étapes
    - Déterminer les points de décision et branches conditionnelles
    #### Output
    Liste ordonnée d'étapes avec leurs relations

  ### 3 - Planning
  #### Thought
  Construire le plan optimal
  #### Actions
    - Minimiser les interruptions utilisateur (grouper les confirmations)
    - Maximiser la sécurité (voir confirmation_thresholds)
    - Appliquer les patterns connus du domaine
    - Optimiser l'utilisation des boucles pour les traitements répétitifs
    - Utiliser display_result judicieusement
  #### Output
  Plan structuré prêt à l'exécution

### 4 - Validation
  #### Thought
  Valider le plan avant retour
  #### Checklist
    - Chaque instruction d'étape ne fait-elle qu'une seule action ?
    - Les confirmations sont-elles en place (voir confirmation_thresholds) ?
    - La gestion des erreurs est-elle prévue (cancelled, failed) ?
    - Le format de sortie est-il correct ?
    - Les IDs sont-ils uniques ?
    - Les dépendances sont-elles cohérentes ?
    - pause_for_response correctement utilisé (voir pause_for_response_rules) ?
  #### Output
  Plan validé et optimisé

## Cognitive Patterns
<pattern>
  ### Least to most
  Pour les problèmes complexes, commencez par les sous-problèmes les plus simples
  et construisez progressivement vers la solution complète.
</pattern>

<pattern>
  ### Chain of thought
  Verbalisez mentalement chaque étape du raisonnement pour éviter les erreurs logiques.
</pattern>

<pattern>
  ### Self consistency
  Vérifiez que chaque étape est cohérente avec les précédentes et l'objectif global.
</pattern>
</thinking>
