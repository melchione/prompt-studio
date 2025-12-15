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
