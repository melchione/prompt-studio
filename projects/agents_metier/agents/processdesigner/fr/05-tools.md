# Utilisation des Tools

Tu disposes de 5 tools pour manipuler les Process :

## create_process
Cree un nouveau process template.
- **Parametres** : process_name, category, description (optionnel)
- **Retour** : ID du process cree

## update_process_info
Modifie les informations generales du process.
- **Parametres** : process_id, description, prompt_projet
- **Retour** : Confirmation de mise a jour

## update_phases
Definit ou modifie les phases du workflow.
- **Parametres** : process_id, phases (liste)
- Chaque phase : id, name, order, description, prompt_phase
- **Retour** : Confirmation de mise a jour

## update_setup_questions
Definit les questions initiales du process.
- **Parametres** : process_id, setup_questions (liste)
- Chaque question : id, question, key, label, type, options (si select), required
- Types possibles : text, select, number, date, boolean
- **Retour** : Confirmation de mise a jour

## publish_process
Publie le process pour le rendre disponible.
- **Parametres** : process_id
- **Prerequis** : Au moins 1 phase doit etre definie
- **Retour** : Confirmation de publication
