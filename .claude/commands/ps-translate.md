# /ps:translate - Traduire les sections

Traduit les sections d'un agent d'une langue vers une autre en utilisant un sub-agent specialise.

## Usage

```
/ps:translate [cible] [options]
```

## Arguments

- `cible` : Peut etre :
  - Nom d'un agent (ex: `executive`) - traduit toutes ses sections
  - Chemin vers un fichier (ex: `projects/cowai/agents/executive/fr/01-context.md`)
  - Rien = agent actif (depuis `.state.json`)

## Options

- `--from fr|en` : Langue source (defaut: detectee depuis le chemin ou `fr`)
- `--to fr|en` : Langue cible (defaut: `en`)
- `--dry-run` : Previsualiser sans ecrire
- `--force` : Ecraser les traductions existantes

## Prerequis

- Un projet doit etre actif dans `.state.json`
- Les sections sources doivent exister

## Instructions

### 1. Detection de la cible

Analyser `$ARGUMENTS` pour determiner la cible :

```
TRADUCTION PROMPT STUDIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Projet : {projet}
Cible  : {agent|fichier}
Direction : {source_lang} → {target_lang}
```

**Logique de detection :**
- Si `$ARGUMENTS` contient un chemin de fichier (avec `/`) → traduire ce fichier
- Si `$ARGUMENTS` contient un nom simple → c'est un agent
- Si `$ARGUMENTS` est vide → utiliser `active_agent` de `.state.json`

### 2. Analyse des sections (si cible = agent)

Lister toutes les sections a traduire :

```
SECTIONS A TRADUIRE - Agent "{agent}"

Source ({source_lang}/) :
  01-context.md          (234 mots)
  02-instructions.md     (512 mots)
  03-tools.md            (189 mots)
  04-examples.md         (345 mots)

Destination ({target_lang}/) :
  01-context.md          Existant (230 mots)
  02-instructions.md     Manquant
  03-tools.md            Manquant
  04-examples.md         Manquant

RESUME : 3 sections a traduire
         1 section existante (utilisez --force pour ecraser)
```

### 3. Confirmation

Si pas `--force` ni `--dry-run`, demander confirmation :

```
Confirmer la traduction de 3 sections ? [O/n]
```

Si `--dry-run` :
```
MODE DRY-RUN : Aucun fichier ne sera ecrit
```

### 4. Traduction via sub-agent

Pour CHAQUE section a traduire, invoquer le sub-agent `prompt-translator` :

```
Traduction 1/3 : 02-instructions.md
```

**IMPORTANT** : Utiliser le Task tool pour invoquer le sub-agent avec ces parametres :
- `subagent_type`: `"prompt-translator"` (doit etre enregistre dans les agents)
- `prompt`: Le contenu source a traduire + les instructions de langue

**Alternative si le sub-agent n'est pas disponible** : Effectuer la traduction directement en respectant les regles de tokens proteges documentees dans le sub-agent.

Apres chaque traduction :

```
02-instructions.md traduit
  Source  : 512 mots | 2,456 caracteres
  Resultat: 489 mots | 2,312 caracteres
  Tokens proteges : 12 (preserves)
  Fichier : projects/{projet}/agents/{agent}/en/02-instructions.md
```

### 5. Ecriture des fichiers

Pour chaque section traduite :
1. Creer le dossier cible si necessaire : `projects/{projet}/agents/{agent}/{target_lang}/`
2. Ecrire le fichier traduit
3. Verifier que les tokens proteges sont intacts

### 6. Resume final

```
TRADUCTION TERMINEE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent     : {agent}
Direction : {source_lang} → {target_lang}

Sections traduites : 3
Tokens proteges    : 45 (tous preserves)

Fichiers crees :
  projects/{projet}/agents/{agent}/en/02-instructions.md
  projects/{projet}/agents/{agent}/en/03-tools.md
  projects/{projet}/agents/{agent}/en/04-examples.md

Prochaine etape : /ps:validate pour verifier les traductions
```

## Tokens Proteges

Les elements suivants ne doivent JAMAIS etre traduits :

| Type | Exemple | Action |
|------|---------|--------|
| Balises XML | `<user_request>`, `</response>` | Conserver tel quel |
| Variables | `$current_date_and_time$` | Conserver tel quel |
| Code inline | `` `fonction()` `` | Conserver tel quel |
| Blocs code | ` ```python ... ``` ` | Conserver tel quel |
| References | `RESULT_FROM_0`, `CURRENT_ITEM` | Conserver tel quel |
| Jinja2 | `{% include '...' %}`, `{{ var }}` | Conserver (adapter `/fr/` → `/en/` dans les includes) |
| MCP tools | `mcp__google_calendar__*` | Conserver tel quel |

## Gestion des erreurs

### Agent non trouve
```
Agent "{nom}" introuvable dans le projet "{projet}"

Agents disponibles :
  - executive
  - planner
  - common
```

### Fichier source inexistant
```
Source introuvable : projects/cowai/agents/executive/fr/01-context.md

Verifiez le chemin ou utilisez /ps:agent {nom} pour activer l'agent.
```

### Traduction existante (sans --force)
```
La traduction existe deja : en/01-context.md

Options :
  - Utilisez --force pour ecraser
  - Editez manuellement avec /ps:write 01-context.md puis changez de langue
```

## Exemples d'utilisation

```bash
# Traduire l'agent actif (fr -> en par defaut)
/ps:translate

# Traduire un agent specifique
/ps:translate executive

# Traduire un fichier specifique
/ps:translate projects/cowai/agents/planner/fr/03-thinking.md

# Forcer la retraduction de tout un agent
/ps:translate executive --force

# Preview sans ecrire
/ps:translate executive --dry-run

# Traduction inverse (en -> fr)
/ps:translate executive --from en --to fr
```

## Résumé et Prochaines Étapes

À la fin de la traduction, afficher :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TRADUCTION TERMINÉE

📋 Ce qui a été fait :
   • {N} sections traduites ({source} → {target})
   • Tokens protégés préservés
   • Includes adaptés (chemins de langue)
   • Fichiers créés dans {target}/

📁 Fichiers créés :
   {liste des fichiers traduits}

📊 Statistiques :
   • Sections : {N}
   • Mots source : {N}
   • Mots traduits : {N}
   • Tokens protégés : {N}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 PROCHAINES COMMANDES DISPONIBLES

▶️  /ps:validate         Vérifier les traductions (RECOMMANDÉ)
    /ps:build            Compiler les prompts
    /ps:write [section]  Ajuster une section manuellement
    /ps:translate --force Retraduire si nécessaire

{Si mode dry-run}
▶️  /ps:translate        Exécuter la traduction (RECOMMANDÉ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
