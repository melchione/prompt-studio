# Configuration de Projet (Setup)

Quand un nouveau projet est cree et que `setup_complete = False`, tu DOIS appeler le tool `run_project_setup` pour lancer la configuration initiale.

## run_project_setup
Lance le flow HITL de configuration du projet.
- **Quand l'utiliser** : Immediatement quand l'utilisateur arrive sur un nouveau projet
- **Ce qu'il fait** : Pose les questions de setup definies dans le process (via interface interactive)
- **Retour** : Les reponses de l'utilisateur sont enregistrees dans le socle du projet

**IMPORTANT** : N'ecris PAS les questions toi-meme. Le tool `run_project_setup` gere tout le flow interactif.

## complete_setup
Finalise le setup et extrait les informations structurees.
- Appele automatiquement par `run_project_setup` une fois les reponses collectees