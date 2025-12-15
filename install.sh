#!/bin/bash
#
# Prompt Studio - Installation rapide
# Usage: curl -fsSL https://raw.githubusercontent.com/[repo]/prompt-studio/install.sh | bash
# Ou localement: bash install.sh
#

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}   PROMPT STUDIO - Installation${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 non trouvé. Installation requise.${NC}"
    exit 1
fi

# Déterminer le répertoire d'installation
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Si le script est exécuté via curl, on est dans un répertoire temporaire
# Sinon on utilise le répertoire du script
if [[ "$SCRIPT_DIR" == "/tmp"* ]] || [[ "$SCRIPT_DIR" == "/var"* ]]; then
    # Installation depuis curl - demander où installer
    echo -e "📁 Où voulez-vous installer Prompt Studio ?"
    read -p "   Chemin [./prompt-studio]: " INSTALL_PATH
    INSTALL_PATH=${INSTALL_PATH:-./prompt-studio}

    # Créer le répertoire
    mkdir -p "$INSTALL_PATH"
    cd "$INSTALL_PATH"

    echo -e "${YELLOW}📥 Téléchargement des fichiers...${NC}"
    # Ici on pourrait télécharger depuis un repo git
    # Pour l'instant, on indique de copier manuellement
    echo -e "${YELLOW}⚠️  Copiez le dossier prompt-studio vers: $INSTALL_PATH${NC}"
    exit 1
else
    # Installation locale - utiliser le répertoire courant
    cd "$SCRIPT_DIR"
fi

echo -e "${GREEN}✅ Répertoire: $(pwd)${NC}"
echo ""

# Créer les dossiers nécessaires
echo "📁 Création de la structure..."
mkdir -p projects versions .claude/commands editor

# Lancer l'installation interactive
echo ""
echo -e "${BLUE}🚀 Lancement de la configuration...${NC}"
echo ""

python3 tools/install.py

echo ""
echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}   Installation terminée !${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""
echo "Pour commencer :"
echo ""
echo -e "  ${BLUE}cd $(pwd)${NC}"
echo -e "  ${BLUE}claude${NC}                    # Ouvrir Claude Code"
echo -e "  ${BLUE}python3 tools/server.py${NC}   # Lancer l'éditeur web"
echo ""
