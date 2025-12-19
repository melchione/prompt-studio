# /ps:status - État du Prompt Studio

Affiche l'état actuel du Prompt Studio.

## Instructions

1. Lire le fichier `.state.json` à la racine du projet
2. Afficher un résumé formaté :

```
📊 PROMPT STUDIO STATUS
━━━━━━━━━━━━━━━━━━━━━━━

🎯 Projet actif : {active_project ou "Aucun"}
🤖 Agent actif  : {active_agent ou "Aucun"}
📝 Phase        : {phase ou "Aucune"}
📄 Section      : {current_section ou "-"}
🕐 Dernier build: {last_build ou "Jamais"}

📁 Projets disponibles :
{liste des projets dans projects/}
```

3. Si un projet est actif, lister ses agents avec leur statut (nombre de sections, langues)

4. Si un agent est actif, afficher ses sections et leur état de complétion

## Résumé et Prochaines Étapes

À la fin de l'affichage du status, afficher :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 PROCHAINES COMMANDES DISPONIBLES

{Si aucun projet actif}
▶️  /ps:project [nom]    Créer ou activer un projet (RECOMMANDÉ)

{Si projet actif mais pas d'agent}
▶️  /ps:agent [nom]      Créer ou activer un agent (RECOMMANDÉ)
    /ps:project          Changer de projet

{Si agent actif sans sections}
▶️  /ps:conceive         Démarrer la conception (RECOMMANDÉ)
    /ps:structure        Définir la structure
    /ps:agent            Changer d'agent

{Si agent actif avec sections incomplètes}
▶️  /ps:write [section]  Continuer la rédaction (RECOMMANDÉ)
    /ps:validate         Vérifier l'état actuel
    /ps:translate        Traduire vers EN

{Si agent complet}
▶️  /ps:build            Compiler les prompts (RECOMMANDÉ)
    /ps:validate         Valider avant build
    /ps:export           Exporter vers projet cible
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
