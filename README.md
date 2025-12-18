# Prompt Studio

Bienvenue dans Prompt Studio, votre atelier de création de prompts pour agents IA.

## C'est quoi Prompt Studio ?

Prompt Studio vous accompagne dans la création de prompts de qualité professionnelle. Au lieu d'écrire un prompt d'un seul bloc, vous le construisez étape par étape, guidé par Claude.

**Le résultat ?** Des prompts bien structurés, faciles à maintenir, et réutilisables entre vos différents agents.

---

## Installation

### Prérequis

- [Claude Code](https://claude.ai/code) installé sur votre machine
- Python 3.8+ (pour l'éditeur web)

### Installer Prompt Studio

```bash
# Clonez le dépôt
git clone https://github.com/votre-repo/prompt-studio.git

# Entrez dans le dossier
cd prompt-studio

# Lancez l'installation
python tools/install.py
```

L'installation vous guide pour configurer votre premier projet.

**Alternative rapide :** Si vous avez déjà Claude Code, vous pouvez directement ouvrir le dossier et commencer à utiliser les commandes `/ps:*`.

---

## Premiers pas

### 1. Lancez Prompt Studio

Ouvrez un terminal dans le dossier `prompt-studio` et lancez Claude Code :

```bash
claude
```

### 2. Voyez où vous en êtes

```
/ps:status
```

Cette commande vous montre l'état actuel : quel projet est actif, quel agent, et où vous en êtes dans le processus.

### 3. Créez votre premier projet

```
/ps:project mon-assistant
```

Un projet regroupe plusieurs agents qui travaillent ensemble. Par exemple, un projet "support-client" pourrait contenir des agents pour le chat, les emails, et les FAQ.

### 4. Créez votre premier agent

```
/ps:agent conseiller
```

Un agent = un prompt = un rôle spécifique. Chaque agent a sa propre personnalité, ses instructions, et ses exemples.

---

## Le workflow en 5 étapes

### Étape 1 : Concevoir

```
/ps:conceive
```

Claude vous pose des questions pour comprendre votre agent :
- Quel est son objectif ?
- Dans quel contexte travaille-t-il ?
- Quelles données reçoit-il et produit-il ?
- Quelles sont ses contraintes ?

**Pourquoi c'est important ?** Cette réflexion en amont évite de réécrire le prompt 10 fois.

### Étape 2 : Structurer

```
/ps:structure
```

Claude analyse votre conception et propose une structure adaptée. Il vérifie aussi quelles **techniques de prompting avancées** seraient utiles (Chain-of-Thought, ReAct, etc.) et vous suggère des sections spécifiques.

Vous obtenez un plan clair :
```
📁 conseiller/
├── 01-context.md        # Qui est l'agent
├── 02-instructions.md   # Ce qu'il doit faire
├── 03-tools.md          # Ses outils
├── 04-examples.md       # Des exemples concrets
└── 05-constraints.md    # Ses limites
```

### Étape 3 : Rédiger

```
/ps:write 01-context
```

Rédigez section par section. Claude vous rappelle :
- Le contexte de conception
- Les techniques de prompting à appliquer
- Des templates adaptés

Vous pouvez aussi simplement taper `/ps:write` pour continuer avec la prochaine section.

### Étape 4 : Valider

```
/ps:validate
```

Claude vérifie que tout est cohérent :
- Les sections se complètent bien
- Les références entre agents fonctionnent
- Les traductions sont complètes

### Étape 5 : Compiler et exporter

```
/ps:build
```

Votre prompt est assemblé en un seul fichier, prêt à être utilisé.

```
/ps:export /chemin/vers/mon-projet
```

Exportez le résultat vers votre projet.

---

## L'éditeur visuel

Préférez une interface graphique ? Lancez l'éditeur web :

```
/ps:editor
```

Ouvrez ensuite http://localhost:8236 dans votre navigateur.

**Ce que vous pouvez faire :**
- Naviguer entre projets et agents
- Éditer les sections avec coloration syntaxique
- Réorganiser les sections par glisser-déposer
- Basculer entre français et anglais
- Voir le résultat compilé en temps réel

**Raccourcis utiles :**
- `Ctrl+S` : Sauvegarder
- `Ctrl+I` : Insérer une référence vers une autre section
- `Escape` : Fermer les fenêtres

---

## Réutiliser du contenu entre agents

Vous avez plusieurs agents qui partagent le même contexte ? Utilisez les includes :

```markdown
{% include 'common/fr/01-context.md' %}
```

Lors de la compilation, cette ligne est remplacée par le contenu de la section référencée. Modifiez une fois, propagez partout.

---

## Techniques de prompting intégrées

Prompt Studio intègre des guides de techniques avancées dans `refs/system-prompting/` :

| Technique | Quand l'utiliser |
|-----------|------------------|
| **Chain-of-Thought** | L'agent doit raisonner étape par étape |
| **ReAct** | L'agent utilise des outils et doit réfléchir entre chaque action |
| **Routing** | L'agent doit classifier et rediriger vers d'autres agents |
| **Least-to-Most** | L'agent résout des problèmes complexes par décomposition |

Ces techniques sont automatiquement suggérées lors de la phase de structure, et rappelées lors de la rédaction.

---

## Commandes rapides

| Commande | Ce qu'elle fait |
|----------|-----------------|
| `/ps:status` | Voir où vous en êtes |
| `/ps:project [nom]` | Créer ou changer de projet |
| `/ps:agent [nom]` | Créer ou changer d'agent |
| `/ps:conceive` | Démarrer la conception |
| `/ps:structure` | Définir les sections |
| `/ps:write [section]` | Rédiger une section |
| `/ps:validate` | Vérifier la cohérence |
| `/ps:build` | Compiler le prompt |
| `/ps:version [type]` | Créer une version (patch/minor/major) |
| `/ps:export [chemin]` | Exporter vers un projet |
| `/ps:editor` | Ouvrir l'éditeur web |

---

## Un exemple concret

Imaginons que vous créez un agent de support client :

```
/ps:project support-saas
/ps:agent chat-support
/ps:conceive
```

Claude vous demande :
> "Quel est le but principal de cet agent ?"

Vous répondez :
> "Répondre aux questions des clients sur notre logiciel SaaS, les guider dans l'utilisation, et escalader vers un humain si nécessaire."

Claude continue avec le contexte, les entrées/sorties, les contraintes...

Puis :
```
/ps:structure
```

Claude analyse et propose :
> "Pour cet agent de support, je recommande la technique **ReAct** pour la gestion des outils (base de connaissances, tickets) et **Routing** pour l'escalade. Voici la structure suggérée..."

Vous validez, puis rédigez section par section. À la fin, vous avez un prompt professionnel, documenté, et versionné.

---

## Besoin d'aide ?

- Tapez `/ps:status` pour voir où vous en êtes
- Chaque commande affiche les prochaines étapes suggérées
- L'éditeur web (`/ps:editor`) offre une vue d'ensemble visuelle

Bonne création !
