# /ps:editor - Lancer l'interface web

Lance le serveur de développement de l'éditeur web Prompt Studio avec vérification automatique des dépendances.

## Usage

```
/ps:editor
```

## Instructions

Exécuter les étapes suivantes dans cet ordre :

### 1. Vérifier les versions

Comparer la version de `app/package.json` avec la version installée dans `app/.installed-version`.

```bash
# Lire la version actuelle
APP_VERSION=$(cat /Users/melkione/Projets/Cowai/prompt-studio/app/package.json | grep '"version"' | head -1 | sed 's/.*"version": "\([^"]*\)".*/\1/')

# Lire la version installée (si existe)
INSTALLED_VERSION=""
if [ -f /Users/melkione/Projets/Cowai/prompt-studio/app/.installed-version ]; then
    INSTALLED_VERSION=$(cat /Users/melkione/Projets/Cowai/prompt-studio/app/.installed-version)
fi

echo "Version app: $APP_VERSION"
echo "Version installée: $INSTALLED_VERSION"
```

### 2. Si les versions diffèrent, installer les dépendances

**Condition** : Si `$INSTALLED_VERSION` est vide OU différent de `$APP_VERSION`

```bash
cd /Users/melkione/Projets/Cowai/prompt-studio/app && npm install
```

Puis mettre à jour le fichier de version :

```bash
echo "$APP_VERSION" > /Users/melkione/Projets/Cowai/prompt-studio/app/.installed-version
```

### 3. Vérifier si le serveur tourne déjà

```bash
lsof -i :5173
```

### 4. Si le port EST utilisé, le libérer

Si un processus utilise le port 5173, le tuer :

```bash
pkill -f "vite.*5173" || true
```

### 5. Lancer le serveur de développement

**IMPORTANT** : Lancer cette commande en background (`run_in_background: true`)

```bash
cd /Users/melkione/Projets/Cowai/prompt-studio/app && npm run dev
```

### 6. Attendre et vérifier

```bash
sleep 3 && lsof -i :5173
```

Si le port est maintenant utilisé, continuer. Sinon, afficher l'erreur.

### 7. Ouvrir le navigateur

```bash
open http://localhost:5173
```

## Script complet (référence)

```bash
#!/bin/bash
APP_DIR="/Users/melkione/Projets/Cowai/prompt-studio/app"

# Lire versions
APP_VERSION=$(grep '"version"' "$APP_DIR/package.json" | head -1 | sed 's/.*"version": "\([^"]*\)".*/\1/')
INSTALLED_VERSION=""
[ -f "$APP_DIR/.installed-version" ] && INSTALLED_VERSION=$(cat "$APP_DIR/.installed-version")

# Installer si nécessaire
if [ "$APP_VERSION" != "$INSTALLED_VERSION" ]; then
    echo "📦 Installation des dépendances (v$APP_VERSION)..."
    cd "$APP_DIR" && npm install
    echo "$APP_VERSION" > "$APP_DIR/.installed-version"
fi

# Lancer le serveur
cd "$APP_DIR" && npm run dev
```

## Message de confirmation

Afficher :

```
🌐 PROMPT STUDIO - Éditeur Web
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Serveur actif sur http://localhost:5173

📦 Version: {APP_VERSION}
🔄 Dépendances: {à jour / installées}

⌨️  Raccourcis :
   • Ctrl+S : Sauvegarder
   • Ctrl+I : Insérer include

Pour arrêter : pkill -f "vite"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Notes

- Port par défaut : 5173 (Vite)
- Fichier de version : `app/.installed-version`
- La version est lue depuis `app/package.json`
- Les dépendances ne sont réinstallées que si la version change
