# 02 - Format Plan Enrichi

## Structure Globale

```json
{
  "goal": "Description de l'objectif utilisateur",
  "steps": [
    { /* step 1 */ },
    { /* step 2 */ }
  ]
}
```

- **`goal`** (string): Objectif final à atteindre
- **`steps`** (list): Liste ordonnée des étapes à exécuter

---

## Format Step

```json
{
  // OBLIGATOIRES
  "id": "1",
  "service": "GOOGLECALENDAR",
  "tools": ["GOOGLECALENDAR_CREATE_EVENT"],
  "instruction": "Créer un événement 'Réunion équipe' demain à 14h",
  "dependencies": [],

  // OPTIONNELS
  "condition": "RESULT_FROM_0 contains confirmed",
  "loopover": "RESULT_FROM_1",
  "start_step": "2",
  "display_result": true,
  "pause_for_response": false,
  "title": "Créer réunion",
  "expected_result": "Événement créé avec ID"
}
```

### Champs Obligatoires

- **`id`** (string): Identifiant unique, utilisé pour dependencies et `RESULT_FROM_X`
- **`service`** (string): Service concerné en UPPERCASE (ex: `GOOGLECALENDAR`, `GMAIL`)
- **`tools`** (list): Liste de 1+ tools. Multi-tool (2+) = exécution séquentielle (voir section 05)
- **`instruction`** (string): Action à effectuer. Variables supportées: `RESULT_FROM_X`, `CURRENT_ITEM`, `LOOP_INDEX`
- **`dependencies`** (list): IDs des steps prérequis (détermine l'ordre d'exécution)

### Champs Optionnels

- **`condition`** (string): Condition d'exécution (si false → skipped). Opérateurs: `contains`, `equals`, `not_contains` → Section 06.1
- **`loopover`** (string): Boucle sur liste (ex: `RESULT_FROM_1`) → Section 06.1
- **`start_step`** (string): ID du step initial dans une boucle
- **`display_result`** (boolean): Afficher résultat à l'utilisateur
- **`pause_for_response`** (boolean): Nécessite réponse utilisateur (tool `request_user_info`) → Section 06.2
- **`title`** (string): Titre court pour logging/UI
- **`expected_result`** (string): Description du résultat attendu

---

## Flux d'Utilisation des Tools

**Process** :
1. `step["tools"]` contient les noms des tools → Extraits au démarrage
2. Durant exécution → Consulter Section 03 (Tools Composio Disponibles) pour construire les paramètres selon `instruction`
3. Appeler `execute_step_tool(tool_name, parameters)` avec les paramètres construits
