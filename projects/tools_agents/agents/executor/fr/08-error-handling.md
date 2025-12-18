# 08 - Error Handling

## Introduction

Les erreurs techniques nécessitent une stratégie de récupération spécifique.

**Différence** :
- ❌ **Erreur** : Problème technique (401, timeout, params invalides)
- ✅ **Résolution autonome** : Manque de données détecté par analyse

**Types d'erreurs** :
1. OAuth (401/403) : Token expiré ou app non connectée
2. Tool introuvable (404) : Tool name incorrect
3. Paramètres invalides (400) : Format/type incorrect
4. Timeout (504) : API trop lente
5. Erreur métier : Tool exécuté mais logique échoue

**Pattern général** : THOUGHT (analyser type + cause) → ACTION (stratégie) → OBSERVATION (résultat)

---

## Erreur OAuth (401/403) ⭐

**Causes** : Token expiré, révoqué, app non connectée, permissions insuffisantes

**Détection** : Codes 401/403 ou messages "unauthorized", "token expired"

**Stratégie (max 1 retry)** :
1. THOUGHT : Analyser cause (token expiré vs app non connectée)
2. ACTION : `request_user_info` pour demander reconnexion
3. OBSERVATION : SDK pause → utilisateur se connecte → connexion établie
4. ACTION : Retry execute_step_tool avec mêmes paramètres
5. Si échec après reconnexion → FAIL step

**Exemple OAuth Error** :
```
ACTION: execute_step_tool("GOOGLECALENDAR_LIST_EVENTS")
OBSERVATION: {"success": false, "error": "401 Unauthorized: Token has expired"}

THOUGHT: Token expiré → demander reconnexion
ACTION: request_user_info("Reconnectez-vous à Google Calendar")
OBSERVATION: Connexion établie → retry successful ✓
```

---

## Tool Introuvable (404)

**Causes** : Typo dans tool name, tool manquant après enrichment, service mal identifié

**Détection** : Message "Tool {tool_name} not found in tool_definitions"

**Stratégie (max 1 retry)** :
1. THOUGHT : Tool non trouvé → probablement typo ou service incorrect
2. ACTION : `find_tool(service, instruction)` pour trouver correct tool
3. OBSERVATION : Tool trouvé ou erreur
4. Si trouvé → ACTION : execute_step_tool avec nouveau tool
5. Si non trouvé → FAIL step

**Exemple Tool 404** :
```
ACTION: execute_step_tool("GOOGLECALENDAR_CREAT_EVENT")  ← Typo
OBSERVATION: Tool not found

THOUGHT: Typo détectée (manque E dans CREATE)
ACTION: find_tool("GOOGLECALENDAR", "Créer événement") → GOOGLECALENDAR_CREATE_EVENT
OBSERVATION: Retry avec tool corrigé → success ✓
```

---

## Paramètres Invalides (400)

**Causes** : Mauvais type, format incorrect (date, email), champ required manquant, valeur hors limites

**Détection** : Code 400 + message "Invalid parameter 'X': expected format Y"

**Stratégie (max 2 retries)** :
1. THOUGHT : Analyser message → identifier paramètre fautif
2. ACTION : Relire tool_definitions pour format attendu
3. THOUGHT : Corriger paramètre avec bon format/type
4. ACTION : execute_step_tool avec params corrigés

**Exemple Params Invalides** :
```
ACTION: execute_step_tool("CREATE_EVENT", {start_time: "2025-11-14 10:00"})
OBSERVATION: {"error": "400: expected ISO8601 format"}

THOUGHT: Format invalide → doit être ISO8601 avec T et Z
ACTION: Relire definitions → retry avec "2025-11-14T10:00:00Z"
OBSERVATION: Success après correction ✓
```

---

## Timeout (504)

**Causes** : API externe lente, charge serveur élevée, réseau instable, opération complexe

**Détection** : Code 504 + message "Request timeout after X seconds"

**Stratégie (0 retry)** :
1. THOUGHT : Timeout détecté → action peut avoir réussi partiellement
2. ACTION : Logger erreur avec contexte complet
3. THOUGHT : Step bloquante ou optionnelle ?
4. Si bloquante → FAIL step avec message clair
5. Si optionnelle → SKIP et continuer

**❌ Pas de retry** : Risque de doublon si action partiellement réussie

**Exemple Timeout** :
```
ACTION: execute_step_tool("GMAIL_SEND_EMAIL", {...})
OBSERVATION: {"error": "504 Gateway Timeout"}

THOUGHT: Timeout → email peut avoir été envoyé partiellement, pas de retry
ACTION: update_state(step_failed) → informer utilisateur de réessayer manuellement
OBSERVATION: État sauvegardé, utilisateur notifié
```

---

## Erreur Métier

**Définition** : Tool s'exécute techniquement mais échoue pour raison logique/métier

**Exemples** : "Event not found", "Quota exceeded", "Calendar is read-only", "Email address invalid"

**Détection** : `{"success": false, "error": "Business error message"}` (pas de code HTTP)

**Stratégie (selon cas)** :
1. THOUGHT : Analyser message d'erreur métier
2. THOUGHT : Peut-on adapter l'instruction ou contourner ?
3. Si adaptable → corriger et retry
4. Si non adaptable → FAIL avec message clair

**Exemple Erreur Métier 1** (objectif atteint) :
```
ACTION: execute_step_tool("DELETE_EVENT", {event_id: "evt_123"})
OBSERVATION: {"error": "Event not found (already deleted)"}

THOUGHT: Événement déjà supprimé → objectif atteint
ACTION: update_state(step_completed, note="already_deleted")
```

**Exemple Erreur Métier 2** (non récupérable) :
```
ACTION: execute_step_tool("SEND_EMAIL", {...})
OBSERVATION: {"error": "Quota exceeded (max 500/day)"}

THOUGHT: Quota Gmail dépassé → impossible de contourner
ACTION: update_state(step_failed, response="Réessayez demain")
```

---

## Tableau Récapitulatif

| Type Erreur          | Code    | Stratégie                       | Retry?      | Max | Fallback              |
| -------------------- | ------- | ------------------------------- | ----------- | --- | --------------------- |
| **OAuth**            | 401/403 | request_user_info → reconnexion | ✅ Oui       | 1x  | Fail si refuse        |
| **Tool introuvable** | 404     | find_tool → retry avec bon tool | ✅ Oui       | 1x  | Fail si non trouvé    |
| **Params invalides** | 400     | Relire definitions → corriger   | ✅ Oui       | 2x  | Fail après 2          |
| **Timeout**          | 504     | Logger → Informer utilisateur   | ❌ Non       | 0x  | Fail (risque doublon) |
| **Erreur métier**    | 200/500 | Analyser → Adapter si possible  | ⚠️ Selon cas | 1x  | Fail avec message     |

---

## Règles Générales

**Pattern** : Toujours THOUGHT → ACTION → OBSERVATION pour chaque erreur

**Limites Retry** : Maximum 2 retries par step (OAuth: 1x, Tool 404: 1x, Params: 2x, Timeout: 0x)

**Logging** : Logger avec type erreur, code, message original, paramètres, tentative récupération

**Messages** : Clairs et actionnables, expliquer pourquoi, éviter jargon technique

**État** : Toujours update_state après gestion (status: "failed"/"completed", error: technique, response: utilisateur)

**Prochaine section** : Exemples (section 09) avec 5 scénarios complets end-to-end.
