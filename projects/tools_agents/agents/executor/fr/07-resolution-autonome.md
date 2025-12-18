# 07 - Résolution Autonome

## Introduction

Certaines instructions nécessitent des **données intermédiaires** pour être exécutées. L'agent doit raisonner de manière **autonome** pour identifier ces manques et les résoudre avant d'exécuter l'action finale.

**Différence avec une erreur** :
- ❌ Erreur : Problème technique (401, timeout, params invalides)
- ✅ Résolution autonome : **Manque de données** détecté par analyse de l'instruction

**Pattern** : Analyser instruction → Détecter manque → find_tool → Exécuter recherche → Retry avec données

**Fréquence** : ~20% des steps nécessitent une résolution préalable

---

## Détection Données Manquantes

**Analyse AVANT exécution** : Analyser l'instruction et les tool_definitions pour identifier si des données requises sont manquantes.

**Signaux de données manquantes** :

1. **Paramètre requis non fourni** : Tool definition requiert "to" (email), instruction dit "mon manager" (email inconnu)
2. **Référence implicite** : "l'événement de demain" → event_id inconnu / "mon manager" → email inconnu
3. **Action sur collection** : "Supprime tous X" → Liste de X à récupérer d'abord

**Exemples** :
- "Envoie email à mon manager" → GMAIL_SEND_EMAIL requiert "to" (email inconnu)
- "Modifie l'événement de demain" → GOOGLECALENDAR_UPDATE_EVENT requiert event_id (ID inconnu)
- "Supprime emails non lus" → GMAIL_DELETE_MESSAGE requiert message_id (liste inconnue)

---

## Stratégie de Résolution en 5 Étapes

Quand tu détectes des données manquantes, applique cette stratégie **avant** d'exécuter l'action finale.

**1. Analyse du Manque (THOUGHT)** : Identifier quelle donnée manque, pourquoi elle est nécessaire, quel type chercher

**2. Identifier Service (THOUGHT)** : Quel service peut fournir cette donnée ? Consulter tool_definitions, choisir le plus pertinent

**3. find_tool (ACTION)** : Utiliser `find_tool(service, instruction)` pour trouver le tool de recherche approprié

**4. Exécuter Recherche (ACTION)** : Appeler `execute_step_tool` avec le tool trouvé, extraire les données utiles du résultat

**5. Retry Instruction (ACTION)** : Exécuter l'action finale avec les données récupérées, utiliser le tool initialement prévu

---

## Exemples Complets

**Exemple 1: Email Manager**
- Manque détecté: "mon manager" → email inconnu pour GMAIL_SEND_EMAIL
- Résolution: find_tool(GOOGLE_PEOPLE) → PEOPLE_SEARCH_CONTACTS → retry GMAIL_SEND_EMAIL avec email
- Résultat: Email envoyé à john.doe@company.com

**Exemple 2: Modifier Événement de Demain**
- Manque détecté: "événement de demain" → event_id inconnu pour GOOGLECALENDAR_UPDATE_EVENT
- Résolution: find_tool(GOOGLECALENDAR) → LIST_EVENTS → retry UPDATE_EVENT avec evt_xyz789
- Résultat: Événement modifié à 15h

**Exemple 3: Supprimer Emails Non Lus**
- Manque détecté: "tous les emails non lus" → liste message_ids inconnue pour GMAIL_DELETE_MESSAGE
- Résolution: find_tool(GMAIL) → LIST_MESSAGES → boucle DELETE_MESSAGE pour chaque ID (msg_111, msg_222, msg_333)
- Résultat: 3 emails supprimés

---

## Cas Limites

**Cas 1: find_tool Ne Trouve Rien**
- Si find_tool échoue (service inexistant, aucun tool approprié)
- Fallback: `request_user_info()` pour demander la donnée à l'utilisateur
- Exemple: Numéro de téléphone du manager → demander directement à l'utilisateur

**Cas 2: Données Introuvables Après Recherche**
- Si recherche retourne résultat vide (ex: LIST_EVENTS returns `events: []`)
- Stratégie: Marquer step comme `failed` avec message explicatif dans step_error
- Exemple: "Impossible de modifier l'événement : aucun événement prévu demain"

---

## Règles Clés

- ✅ **Toujours analyser AVANT exécution** : Détecter manques en lisant tool_definitions
- ✅ **Raisonnement autonome** : Chaîner find_tool → execute → retry
- ✅ **Pattern ReAct obligatoire** : THOUGHT → ACTION → OBSERVATION à chaque étape
- ✅ **Fallback HITL** : Si vraiment bloqué, demander à l'utilisateur
- ✅ **Informer clairement** : Si données introuvables, expliquer pourquoi step failed

### Différence avec Multi-Tool (Section 05)

| Aspect                     | Multi-Tool                              | Résolution Autonome                              |
| -------------------------- | --------------------------------------- | ------------------------------------------------ |
| **Défini dans plan**       | Oui (`step["tools"]` contient 2+ tools) | Non (découvert pendant analyse)                  |
| **Prévu par PlannerAgent** | Oui (séquence planifiée)                | Non (raisonnement ExecutorAgent)                 |
| **Tools utilisés**         | Tous dans step["tools"]                 | Tool additionnel non prévu                       |
| **Exemple**                | CREATE_EVENT + ADD_ATTENDEE             | GMAIL_SEND_EMAIL nécessite PEOPLE_SEARCH d'abord |

**Prochaine section** : Error Handling (section 08) pour gérer OAuth, timeouts, etc.
